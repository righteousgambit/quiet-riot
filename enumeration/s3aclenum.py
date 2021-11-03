#!/usr/bin/env python3
import boto3
from botocore.config import Config

myconfig = Config(
    retries = dict(
        max_attempts = 7
    )
)



client = boto3.client('s3', config=myconfig)
response = client.put_bucket_acl(
    ACL='private'|'public-read'|'public-read-write'|'authenticated-read',
    AccessControlPolicy={
        'Grants': [
            {
                'Grantee': {
                    'DisplayName': 'string',
                    'EmailAddress': 'string',
                    'ID': 'string',
                    'Type': 'CanonicalUser'|'AmazonCustomerByEmail'|'Group',
                    'URI': 'string'
                },
                'Permission': 'FULL_CONTROL'|'WRITE'|'WRITE_ACP'|'READ'|'READ_ACP'
            },
        ],
        'Owner': {
            'DisplayName': 'string',
            'ID': 'string'
        }
    },
    Bucket='string',
    GrantFullControl='string',
    GrantRead='string',
    GrantReadACP='string',
    GrantWrite='string',
    GrantWriteACP='string',
    ExpectedBucketOwner='string'
)