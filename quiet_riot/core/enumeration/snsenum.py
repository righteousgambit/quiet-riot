#!/usr/bin/env python3
import json
import logging

from botocore.exceptions import ClientError

from ... import config as app_config
from .retry_handler import get_botocore_retry_config, retry_with_backoff

logger = logging.getLogger(__name__)


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
def sns_princ_checker(rand_account_id, session):
    """
    Check if an AWS principal (account ID or ARN) exists by attempting to set SNS topic policy.

    Args:
        rand_account_id: AWS account ID or ARN to check
        session: Boto3 session object

    Returns:
        str: 'Pass' if principal exists, 'Fail' if it doesn't, raises exception on other errors
    """
    # Create client with retry configuration
    botocore_config = get_botocore_retry_config(max_attempts=7)
    client = session.client("sns", config=botocore_config)

    my_managed_policy = {
        "Statement": [
            {
                "Sid": "grant-1234-publish",
                "Effect": "Allow",
                "Principal": {"AWS": f"{rand_account_id}"},
                "Action": ["sns:Publish"],
                "Resource": app_config.get_config().scan_objects[2],
            }
        ]
    }

    try:
        client.set_topic_attributes(
            TopicArn=app_config.get_config().scan_objects[2],
            AttributeName="Policy",
            AttributeValue=json.dumps(my_managed_policy),
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
            logger.warning(f"SNS throttling for {rand_account_id}: {e}")
            raise  # Will be retried by decorator
        # For other client errors, log and return Fail
        logger.debug(f"SNS client error for {rand_account_id}: {e}")
        return "Fail"
    except Exception as e:
        # Unexpected errors should be logged and re-raised
        logger.error(f"Unexpected error checking {rand_account_id} with SNS: {e}")
        raise
