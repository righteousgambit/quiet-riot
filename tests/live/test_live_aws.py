"""Live AWS integration tests — exercise each enumeration service end-to-end.

These create REAL AWS resources (ECR-Public, ECR-Private, SNS, S3), run the
actual principal-validation technique against them using the CI account's own
account id as a known-valid principal, and clean everything up.

They are gated behind ``--run-live`` / ``QR_LIVE=1`` and skip automatically when
no AWS credentials are available. In CI they run under the github-actions-role
via OIDC. This is the layer that proves the ``app_app_config`` fix works against
real AWS (moto cannot mock ECR-Public).
"""

import contextlib
import json
import time
import uuid

import pytest

from quiet_riot.core.enumeration import ecrprivenum, ecrpubenum, s3aclenum, snsenum
from tests.helpers import configure_scan

pytestmark = pytest.mark.live

INVALID_ACCOUNT_ID = "000000000000"


def _suffix() -> str:
    return uuid.uuid4().hex[:10]


# --------------------------------------------------------------------------- #
# ECR Public (the path that was dead due to the undefined-name bug)
# --------------------------------------------------------------------------- #
def test_live_ecr_public_validates_own_account(live_session):
    account = live_session._qr_account_id
    client = live_session.client("ecr-public", region_name="us-east-1")
    repo = f"quiet-riot-public-repo-test-{_suffix()}"
    client.create_repository(repositoryName=repo)
    try:
        configure_scan(account_no=account, ecr_pub=repo)
        # Own account is a valid principal -> must return "Pass" (proves the fix).
        assert ecrpubenum.ecr_princ_checker(account, live_session) == "Pass"
        # A non-existent principal must not crash and should return "Fail".
        assert ecrpubenum.ecr_princ_checker(INVALID_ACCOUNT_ID, live_session) == "Fail"
    finally:
        client.delete_repository(repositoryName=repo, force=True)


# --------------------------------------------------------------------------- #
# SNS
# --------------------------------------------------------------------------- #
def test_live_sns_validates_own_account(live_session):
    account = live_session._qr_account_id
    sns = live_session.client("sns")
    topic_arn = sns.create_topic(Name=f"quiet-riot-sns-topic-test-{_suffix()}")["TopicArn"]
    try:
        configure_scan(account_no=account, sns_arn=topic_arn)
        assert snsenum.sns_princ_checker(account, live_session) == "Pass"
        assert snsenum.sns_princ_checker(INVALID_ACCOUNT_ID, live_session) == "Fail"
    finally:
        sns.delete_topic(TopicArn=topic_arn)


# --------------------------------------------------------------------------- #
# ECR Private (registry policy is account-global; serialize via unique repo)
# --------------------------------------------------------------------------- #
def test_live_ecr_private_validates_own_account(live_session):
    account = live_session._qr_account_id
    ecr = live_session.client("ecr")
    repo = f"quiet-riot-private-repo-test-{_suffix()}"
    ecr.create_repository(repositoryName=repo)
    try:
        configure_scan(account_no=account, ecr_priv=repo)
        assert ecrprivenum.ecr_princ_checker(account, live_session) == "Pass"
        assert ecrprivenum.ecr_princ_checker(INVALID_ACCOUNT_ID, live_session) == "Fail"
    finally:
        with contextlib.suppress(Exception):
            ecr.delete_registry_policy()
        ecr.delete_repository(repositoryName=repo, force=True)


# --------------------------------------------------------------------------- #
# S3 ACL (root-email path) — negative-only: we cannot safely assert a positive
# without a known AWS-registered email. Proving it returns "Fail" without a
# NameError is the regression guard for the s3aclenum app_app_config bug.
# --------------------------------------------------------------------------- #
def test_live_s3acl_invalid_email_returns_fail(live_session):
    account = live_session._qr_account_id
    s3 = live_session.client("s3")
    bucket = f"quiet-riot-bucket-test-{_suffix()}"
    s3.create_bucket(Bucket=bucket)
    canonical = s3.list_buckets()["Owner"]["ID"]
    try:
        configure_scan(account_no=account, bucket=bucket, canonical=canonical)
        result = s3aclenum.s3_acl_princ_checker(
            f"definitely-not-a-real-aws-email-{_suffix()}@example.invalid",
            live_session,
        )
        assert result == "Fail"
    finally:
        s3.delete_bucket(Bucket=bucket)


# --------------------------------------------------------------------------- #
# Full Scanner end-to-end: provision -> enumerate -> cleanup (AWS Account IDs).
# Repeats the known-valid id enough times that the random load-balancer routes
# it through the (formerly broken) ECR-Public path with overwhelming probability.
# --------------------------------------------------------------------------- #
def _retry_pass(checker, principal, session, tries=6, delay=2):
    """Retry a positive check briefly to absorb IAM eventual consistency."""
    result = "Fail"
    for _ in range(tries):
        result = checker(principal, session)
        if result == "Pass":
            return result
        time.sleep(delay)
    return result


def test_live_detects_real_vs_fake_role_and_user(live_session):
    """The core technique must distinguish a REAL role/user ARN from a FAKE one,
    not just account ids. Creates real IAM principals and verifies Pass/Fail."""
    account = live_session._qr_account_id
    iam = live_session.client("iam")
    s = _suffix()
    role_name = f"quiet-riot-test-role-{s}"
    user_name = f"quiet-riot-test-user-{s}"
    trust = json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}
            ],
        }
    )
    iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=trust)
    iam.create_user(UserName=user_name)

    ecrpub = live_session.client("ecr-public", region_name="us-east-1")
    repo = f"quiet-riot-public-repo-test-{s}"
    ecrpub.create_repository(repositoryName=repo)
    configure_scan(account_no=account, ecr_pub=repo)

    real_role = f"arn:aws:iam::{account}:role/{role_name}"
    real_user = f"arn:aws:iam::{account}:user/{user_name}"
    fake_role = f"arn:aws:iam::{account}:role/quiet-riot-nope-{uuid.uuid4().hex[:8]}"
    fake_user = f"arn:aws:iam::{account}:user/quiet-riot-nope-{uuid.uuid4().hex[:8]}"
    try:
        assert _retry_pass(ecrpubenum.ecr_princ_checker, real_role, live_session) == "Pass"
        assert _retry_pass(ecrpubenum.ecr_princ_checker, real_user, live_session) == "Pass"
        assert ecrpubenum.ecr_princ_checker(fake_role, live_session) == "Fail"
        assert ecrpubenum.ecr_princ_checker(fake_user, live_session) == "Fail"
    finally:
        with contextlib.suppress(Exception):
            ecrpub.delete_repository(repositoryName=repo, force=True)
        with contextlib.suppress(Exception):
            iam.delete_role(RoleName=role_name)
        with contextlib.suppress(Exception):
            iam.delete_user(UserName=user_name)


def test_live_full_account_id_scan(live_session, tmp_path):
    from quiet_riot.core.scanner import Scanner

    account = live_session._qr_account_id
    wordlist = tmp_path / "accounts.txt"
    wordlist.write_text("\n".join([account] * 20 + [INVALID_ACCOUNT_ID] * 5) + "\n")

    from quiet_riot.core.models import ScanConfig, ScanType

    scanner = Scanner(live_session)
    cfg = ScanConfig(scan_type=ScanType.AWS_ACCOUNT_IDS, wordlist_path=str(wordlist), threads=10)
    result = scanner.run_scan(cfg, cleanup=True)

    assert result.status == "completed", result.error
    assert account in result.valid_principals, "own account should validate across services"
    # Resources should have been torn down.
    assert scanner.resource_mgr.resources_created is False
