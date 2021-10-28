#!/usr/bin/env python3
import random as rand
import json
import boto3
from botocore.exceptions import ClientError

# Establish boto3 sns session
client = boto3.client('s3')

def s3_princ_checker(rand_account_id):
    bucket_name = 'quiet-riot-global-bucket'
    my_managed_policy ={
    'Version': '2012-10-17',
    'Statement': [{
        'Sid': 'AddPerm',
        'Effect': 'Allow',
        'Principal': {"AWS":f'{rand_account_id}'},
        'Action': ['s3:GetObject'],
        'Resource': f'arn:aws:s3:::{bucket_name}/*'
        }]
    }
    # Implement object to take my_managed_policy and parse for the generated account ID - then send that as return, not the fully policy
    try:
      response = client.put_bucket_policy(
        Bucket='quiet-riot-global-bucket', # TODO name of bucket that we put the policy against.
        ConfirmRemoveSelfBucketAccess=False,
        Policy=json.dumps(my_managed_policy),
        ExpectedBucketOwner='201012399609' # TODO name of expected bucket owner
    )
      print(rand_account_id)
      return("Pass")

  # Handles the exception thrown when the Principal doesn't exist
    except client.exceptions.from_code('MalformedPolicy') as e:
        return('Fail')