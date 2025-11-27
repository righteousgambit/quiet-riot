#!/usr/bin/env python3
"""
Resource manager for AWS resources created during scanning.
Ensures proper cleanup of all created resources.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ResourceManager:
    """Manages AWS resources created for enumeration scanning."""

    def __init__(self, session):
        """
        Initialize resource manager.

        Args:
            session: Boto3 session object
        """
        self.session = session
        self.ecr_public_repo: Optional[str] = None
        self.ecr_private_repo: Optional[str] = None
        self.sns_topic_arn: Optional[str] = None
        self.s3_bucket: Optional[str] = None
        self.canonical_id: Optional[str] = None
        self.resources_created = False

    def create_resources(
        self, ecr_public_repo: str, ecr_private_repo: str, sns_topic: str, s3_bucket: str, canonical_id: str
    ):
        """
        Track created resources.

        Args:
            ecr_public_repo: ECR public repository name
            ecr_private_repo: ECR private repository name
            sns_topic: SNS topic name
            s3_bucket: S3 bucket name
            canonical_id: S3 canonical ID
        """
        self.ecr_public_repo = ecr_public_repo
        self.ecr_private_repo = ecr_private_repo
        self.sns_topic_arn = (
            f"arn:aws:sns:us-east-1:{self.session.client('sts').get_caller_identity()['Account']}:{sns_topic}"
        )
        self.s3_bucket = s3_bucket
        self.canonical_id = canonical_id
        self.resources_created = True

    def cleanup_all(self, force: bool = False) -> bool:
        """
        Clean up all created resources.

        Args:
            force: If True, skip confirmation prompts

        Returns:
            bool: True if cleanup was successful
        """
        if not self.resources_created:
            logger.debug("No resources to clean up")
            return True

        success = True

        # Clean up S3 bucket
        if self.s3_bucket:
            success &= self._cleanup_s3_bucket()

        # Clean up ECR Public repository
        if self.ecr_public_repo:
            success &= self._cleanup_ecr_public_repo()

        # Clean up ECR Private repository
        if self.ecr_private_repo:
            success &= self._cleanup_ecr_private_repo()

        # Clean up SNS topic
        if self.sns_topic_arn:
            success &= self._cleanup_sns_topic()

        if success:
            logger.info("All resources cleaned up successfully")
            self.resources_created = False
        else:
            logger.warning("Some resources may not have been cleaned up")

        return success

    def _cleanup_s3_bucket(self) -> bool:
        """Clean up S3 bucket."""
        try:
            s3 = self.session.client("s3")
            buckets = s3.list_buckets()

            for bucket in buckets.get("Buckets", []):
                if "quiet-riot-bucket" in bucket["Name"]:
                    try:
                        # Empty bucket first (required for deletion)
                        bucket_name = bucket["Name"]
                        try:
                            objects = s3.list_objects_v2(Bucket=bucket_name)
                            if "Contents" in objects:
                                for obj in objects["Contents"]:
                                    s3.delete_object(Bucket=bucket_name, Key=obj["Key"])
                        except Exception as e:
                            logger.debug(f"Error listing/emptying bucket {bucket_name}: {e}")

                        s3.delete_bucket(Bucket=bucket_name)
                        logger.info(f"Deleted S3 bucket: {bucket_name}")
                        return True
                    except Exception as e:
                        logger.warning(f"Error deleting S3 bucket {bucket['Name']}: {e}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Error during S3 bucket cleanup: {e}")
            return False

    def _cleanup_ecr_public_repo(self) -> bool:
        """Clean up ECR Public repository."""
        try:
            ecr_public = self.session.client("ecr-public")
            repos = ecr_public.describe_repositories()

            for repo in repos.get("repositories", []):
                if "quiet-riot-public-repo" in repo["repositoryName"]:
                    try:
                        ecr_public.delete_repository(repositoryName=repo["repositoryName"])
                        logger.info(f"Deleted ECR Public repository: {repo['repositoryName']}")
                        return True
                    except Exception as e:
                        logger.warning(f"Error deleting ECR Public repo {repo['repositoryName']}: {e}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Error during ECR Public cleanup: {e}")
            return False

    def _cleanup_ecr_private_repo(self) -> bool:
        """Clean up ECR Private repository."""
        try:
            ecr_private = self.session.client("ecr")
            repos = ecr_private.describe_repositories()

            for repo in repos.get("repositories", []):
                if "quiet-riot-private-repo" in repo["repositoryName"]:
                    try:
                        ecr_private.delete_repository(repositoryName=repo["repositoryName"])
                        logger.info(f"Deleted ECR Private repository: {repo['repositoryName']}")
                        return True
                    except Exception as e:
                        logger.warning(f"Error deleting ECR Private repo {repo['repositoryName']}: {e}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Error during ECR Private cleanup: {e}")
            return False

    def _cleanup_sns_topic(self) -> bool:
        """Clean up SNS topic."""
        try:
            sns = self.session.client("sns")
            topics = sns.list_topics()

            for topic in topics.get("Topics", []):
                if "quiet-riot-sns-topic" in topic["TopicArn"]:
                    try:
                        sns.delete_topic(TopicArn=topic["TopicArn"])
                        logger.info(f"Deleted SNS topic: {topic['TopicArn']}")
                        return True
                    except Exception as e:
                        logger.warning(f"Error deleting SNS topic {topic['TopicArn']}: {e}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Error during SNS topic cleanup: {e}")
            return False
