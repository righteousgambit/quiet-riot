#!/usr/bin/env python3
import json
import boto3
from botocore.exceptions import ClientError

session = boto3.Session(profile_name='default')
client = session.client('codeartifact')

def codeartifact_princ_checker(rand_account_id):
    my_managed_policy ={
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "codeartifact:CreateRepository"
            ],
            "Effect": "Allow",
            "Principal": {
                 "AWS": f'{rand_account_id}'
            },
            "Resource": "arn:aws:codeartifact:us-east-1:201012399609:domain/test-domain"
        }
    ]
}
    # Implement object to take my_managed_policy and parse for the generated account ID - then send that as return, not the fully policy
    try:
        response = client.put_domain_permissions_policy(
            domain='test-domain',
            domainOwner='201012399609', # Requires update with dynamic variable using end user account ID
            policyRevision= 'test',
            policyDocument=json.dumps(my_managed_policy)
        )
        print(rand_account_id)
        return('Pass')
    except client.exceptions.ConflictException as e:
        print(rand_account_id)
        return('Pass')
  # Handles the exception thrown when the Principal doesn't exist
    except client.exceptions.ValidationException as e:
      return(str(rand_account_id)+" FAIL")