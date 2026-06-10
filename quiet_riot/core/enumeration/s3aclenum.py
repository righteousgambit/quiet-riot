#!/usr/bin/env python3
import logging

from botocore.exceptions import ClientError

from ... import config as app_config
from .retry_handler import get_botocore_retry_config, retry_with_backoff

logger = logging.getLogger(__name__)


@retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=10.0)
def s3_acl_princ_checker(rand_account_id, session):
    """
    Check if an email address is associated with an AWS root account by attempting to set S3 bucket ACL.

    Args:
        rand_account_id: Email address to check
        session: Boto3 session object

    Returns:
        str: 'Pass' if email is associated with root account, 'Fail' otherwise
    """
    # Create client with retry configuration
    botocore_config = get_botocore_retry_config(max_attempts=7)
    client = session.client("s3", config=botocore_config)

    try:
        client.put_bucket_acl(
            AccessControlPolicy={
                "Grants": [
                    {
                        "Grantee": {
                            "EmailAddress": rand_account_id,
                            "Type": "AmazonCustomerByEmail",
                        },
                        "Permission": "READ",
                    },
                ],
                "Owner": {"ID": app_config.get_config().scan_objects[4]},
            },
            Bucket=app_config.get_config().scan_objects[3],
            ExpectedBucketOwner=app_config.get_config().account_no,
        )
        logger.info(f"Valid root account email found: {rand_account_id}")
        return "Pass"
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        # Re-raise throttling and other retryable errors
        if error_code in ("Throttling", "ThrottlingException", "ServiceUnavailable"):
            logger.warning(f"S3 ACL throttling for {rand_account_id}: {e}")
            raise  # Will be retried by decorator
        # Invalid email or other client errors mean the email is not associated
        logger.debug(f"S3 ACL check failed for {rand_account_id}: {e}")
        return "Fail"
    except Exception as e:
        # Unexpected errors should be logged and re-raised
        logger.error(f"Unexpected error checking {rand_account_id} with S3 ACL: {e}")
        raise
