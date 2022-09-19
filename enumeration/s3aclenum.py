#!/usr/bin/env python3
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from .. import settings

# myconfig = Config(
#     retries = dict(
#         max_attempts = 10
#     )
# )
# client = boto3.client('s3')

def s3_acl_princ_checker(rand_account_id,session):
    client = session.client('s3')
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
                    'ID': settings.scan_objects[4]
                }
            },
            Bucket=settings.scan_objects[3],
            ExpectedBucketOwner=settings.account_no
    )
        return 'Pass'
    except BaseException as err:
        print(err)
        pass