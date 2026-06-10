"""Shared test helpers for Quiet Riot."""

import types

import boto3
from botocore.exceptions import ClientError


def offline_client(service: str, region: str = "us-east-1"):
    """Build a real botocore client (no network) so ``.exceptions`` are populated.

    Individual methods can then be monkeypatched to simulate AWS responses.
    """
    return boto3.client(
        service,
        region_name=region,
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
    )


def make_fake_session(client):
    """Return an object whose ``.client(...)`` always returns ``client``."""
    return types.SimpleNamespace(client=lambda *a, **k: client)


def pass_client(service: str, method: str):
    """Client whose ``method`` succeeds -> enumerator should return 'Pass'."""
    c = offline_client(service)
    setattr(c, method, lambda **kw: {})
    return c


def fail_client(service: str, method: str, code: str = "InvalidParameterException"):
    """Client whose ``method`` raises a non-throttling ClientError -> 'Fail'."""
    c = offline_client(service)

    def _raise(**kw):
        raise ClientError({"Error": {"Code": code, "Message": "invalid principal"}}, "Op")

    setattr(c, method, _raise)
    return c


def configure_scan(
    account_no: str = "211125621822",
    ecr_pub: str = "quiet-riot-public-repo-test",
    ecr_priv: str = "quiet-riot-private-repo-test",
    sns_arn: str = "arn:aws:sns:us-east-1:211125621822:quiet-riot-sns-topic-test",
    bucket: str = "quiet-riot-bucket-test",
    canonical: str = "canon-id-test",
):
    """Populate the Config singleton with scan objects in the order the enumerators expect.

    Index map: [0]=ecr-public repo, [1]=ecr-private repo, [2]=sns topic arn,
    [3]=s3 bucket, [4]=s3 canonical id.
    """
    from quiet_riot import config

    cfg = config.get_config()
    cfg.account_no = account_no
    cfg.scan_objects = [ecr_pub, ecr_priv, sns_arn, bucket, canonical]
    return cfg
