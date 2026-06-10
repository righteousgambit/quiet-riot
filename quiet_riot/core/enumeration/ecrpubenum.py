#!/usr/bin/env python3
import json
import logging

from botocore.exceptions import ClientError

from ... import config as app_config
from .retry_handler import get_botocore_retry_config, retry_with_backoff

logger = logging.getLogger(__name__)


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
def ecr_princ_checker(rand_account_id, session):
    """
    Check if an AWS principal (account ID or ARN) exists by attempting to set ECR Public repository policy.

    Args:
        rand_account_id: AWS account ID or ARN to check
        session: Boto3 session object

    Returns:
        str: 'Pass' if principal exists, 'Fail' if it doesn't, raises exception on other errors
    """
    # Create client with retry configuration
    botocore_config = get_botocore_retry_config(max_attempts=7)
    client = session.client("ecr-public", config=botocore_config)

    my_managed_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowPushPull",
                "Effect": "Allow",
                "Principal": {"AWS": [f"{rand_account_id}"]},
                "Action": [
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:CompleteLayerUpload",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:InitiateLayerUpload",
                    "ecr:PutImage",
                    "ecr:UploadLayerPart",
                ],
            }
        ],
    }

    try:
        client.set_repository_policy(
            registryId=app_config.get_config().account_no,
            repositoryName=app_config.get_config().scan_objects[0],
            policyText=json.dumps(my_managed_policy),
        )
        logger.info(f"Valid principal found: {rand_account_id}")
        return "Pass"
    except client.exceptions.InvalidParameterException:
        # Principal doesn't exist - this is expected for invalid accounts
        return "Fail"
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        # Re-raise throttling and other retryable errors
        if error_code in ("Throttling", "ThrottlingException", "ServiceUnavailable"):
            logger.warning(f"ECR-Public throttling for {rand_account_id}: {e}")
            raise  # Will be retried by decorator
        # For other client errors, log and return Fail
        logger.debug(f"ECR-Public client error for {rand_account_id}: {e}")
        return "Fail"
    except Exception as e:
        # Unexpected errors should be logged and re-raised
        logger.error(f"Unexpected error checking {rand_account_id} with ECR-Public: {e}")
        raise
