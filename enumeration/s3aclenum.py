#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

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
                    'ID': '9523268a3a3b5a4599d502f2f8bb3678b6df2e9bdce8293dfd62960fb070e000'
                }
            },
            Bucket='quiet-riot-global-bucket',
            ExpectedBucketOwner='201012399609'
    )
        return 'Pass'
    except BaseException as err:
        pass