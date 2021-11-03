#!/usr/bin/env python3
import boto3
from botocore.config import Config

myconfig = Config(
    retries = dict(
        max_attempts = 7
    )
)

rand_account_id = 'wsladd@icloud.com'

client = boto3.client('s3', config=myconfig)
response = client.put_bucket_acl(
    AccessControlPolicy={
        'Grants': [
            {
                'Grantee': {
                    'EmailAddress': rand_account_id,
                },
                'Permission': 'READ'
            },
        ],
        'Owner': {
            'DisplayName': 'string',
            'ID': 'string'
        }
    },
    Bucket='string',
    ExpectedBucketOwner='string'
)