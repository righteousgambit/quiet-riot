#!/usr/bin/env python3
"""
Resource manager for AWS resources created during scanning.
Ensures proper cleanup of all created resources.
"""

import contextlib
import logging

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
        self.ecr_public_repo: str | None = None
        self.ecr_private_repo: str | None = None
        self.sns_topic_arn: str | None = None
        self.s3_bucket: str | None = None
        self.canonical_id: str | None = None
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
        region = self.session.region_name or "us-east-1"
        account = self.session.client("sts").get_caller_identity()["Account"]
        self.sns_topic_arn = f"arn:aws:sns:{region}:{account}:{sns_topic}"
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
        """Delete only the bucket this manager created (paginated empty first)."""
        if not self.s3_bucket:
            return True
        s3 = self.session.client("s3")
        try:
            paginator = s3.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self.s3_bucket):
                objects = [{"Key": o["Key"]} for o in page.get("Contents", [])]
                if objects:
                    s3.delete_objects(Bucket=self.s3_bucket, Delete={"Objects": objects})
            s3.delete_bucket(Bucket=self.s3_bucket)
            logger.info(f"Deleted S3 bucket: {self.s3_bucket}")
            return True
        except s3.exceptions.NoSuchBucket:
            logger.debug(f"S3 bucket already gone: {self.s3_bucket}")
            return True
        except Exception as e:
            logger.warning(f"Error deleting S3 bucket {self.s3_bucket}: {e}")
            return False

    def _cleanup_ecr_public_repo(self) -> bool:
        """Delete only the ECR Public repository this manager created."""
        if not self.ecr_public_repo:
            return True
        ecr = self.session.client("ecr-public")
        try:
            ecr.delete_repository(repositoryName=self.ecr_public_repo, force=True)
            logger.info(f"Deleted ECR Public repository: {self.ecr_public_repo}")
            return True
        except ecr.exceptions.RepositoryNotFoundException:
            return True
        except Exception as e:
            logger.warning(f"Error deleting ECR Public repo {self.ecr_public_repo}: {e}")
            return False

    def _cleanup_ecr_private_repo(self) -> bool:
        """Delete only the ECR Private repo this manager created (+ its registry policy)."""
        if not self.ecr_private_repo:
            return True
        ecr = self.session.client("ecr")
        # The scan sets an account-level registry policy; remove it best-effort.
        with contextlib.suppress(Exception):
            ecr.delete_registry_policy()
        try:
            ecr.delete_repository(repositoryName=self.ecr_private_repo, force=True)
            logger.info(f"Deleted ECR Private repository: {self.ecr_private_repo}")
            return True
        except ecr.exceptions.RepositoryNotFoundException:
            return True
        except Exception as e:
            logger.warning(f"Error deleting ECR Private repo {self.ecr_private_repo}: {e}")
            return False

    def _cleanup_sns_topic(self) -> bool:
        """Delete only the SNS topic this manager created (delete_topic is idempotent)."""
        if not self.sns_topic_arn:
            return True
        sns = self.session.client("sns")
        try:
            sns.delete_topic(TopicArn=self.sns_topic_arn)
            logger.info(f"Deleted SNS topic: {self.sns_topic_arn}")
            return True
        except Exception as e:
            logger.warning(f"Error deleting SNS topic {self.sns_topic_arn}: {e}")
            return False
