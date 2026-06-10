"""Unit tests for AWS resource tracking + cleanup (moto-mocked).

Note: moto 5.x does not implement ECR-Public, so these tests cover S3, SNS,
and ECR-Private. The ECR-Public path is covered by the live integration tests.
"""

from quiet_riot.core.enumeration.resource_manager import ResourceManager


def _seed_resources(session):
    s3 = session.client("s3")
    sns = session.client("sns")
    ecr = session.client("ecr")
    s3.create_bucket(Bucket="quiet-riot-bucket-unit")
    topic = sns.create_topic(Name="quiet-riot-sns-topic-unit")["TopicArn"]
    ecr.create_repository(repositoryName="quiet-riot-private-repo-unit")
    return topic


def test_create_resources_tracks_and_builds_sns_arn(moto_session):
    rm = ResourceManager(moto_session)
    assert rm.resources_created is False
    rm.create_resources(
        ecr_public_repo="quiet-riot-public-repo-unit",
        ecr_private_repo="quiet-riot-private-repo-unit",
        sns_topic="quiet-riot-sns-topic-unit",
        s3_bucket="quiet-riot-bucket-unit",
        canonical_id="canon",
    )
    assert rm.resources_created is True
    assert rm.sns_topic_arn.endswith(":quiet-riot-sns-topic-unit")
    assert rm.s3_bucket == "quiet-riot-bucket-unit"


def test_cleanup_removes_s3_sns_ecr_private(moto_session):
    topic_arn = _seed_resources(moto_session)
    rm = ResourceManager(moto_session)
    # Track public repo as None so the (moto-unsupported) ECR-Public path is skipped.
    rm.ecr_public_repo = None
    rm.ecr_private_repo = "quiet-riot-private-repo-unit"
    rm.sns_topic_arn = topic_arn
    rm.s3_bucket = "quiet-riot-bucket-unit"
    rm.canonical_id = "canon"
    rm.resources_created = True

    rm.cleanup_all(force=True)

    s3 = moto_session.client("s3")
    sns = moto_session.client("sns")
    ecr = moto_session.client("ecr")
    bucket_names = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    topic_arns = [t["TopicArn"] for t in sns.list_topics().get("Topics", [])]
    repo_names = [r["repositoryName"] for r in ecr.describe_repositories().get("repositories", [])]

    assert "quiet-riot-bucket-unit" not in bucket_names
    assert topic_arn not in topic_arns
    assert "quiet-riot-private-repo-unit" not in repo_names


def test_cleanup_noop_when_nothing_created(moto_session):
    rm = ResourceManager(moto_session)
    assert rm.cleanup_all(force=True) is True
