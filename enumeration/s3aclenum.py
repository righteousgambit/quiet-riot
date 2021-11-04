#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import settings

myconfig = Config(
    retries = dict(
        max_attempts = 7
    )
)

client = boto3.client('s3', config=myconfig)

def s3_acl_princ_checker(rand_account_id):
    try:
        client.put_bucket_acl(
            AccessControlPolicy={
                'Grants': [
                    {
                        'Grantee': {
                            'EmailAddress': rand_account_id,
                            'Type': 'AmazonCustomerByEmail',
                        },
                        'Permission': 'READ'
                    },
                ],
                'Owner': {
                    'ID': settings.scan_objects[3]
                }
            },
            Bucket='quiet-riot-global-bucket',
            ExpectedBucketOwner=settings.account_no
    )
        return 'Pass'
    except BaseException as err:
        pass