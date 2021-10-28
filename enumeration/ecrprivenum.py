#!/usr/bin/env python3
import random as rand
import json
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

config = Config(
    retries = dict(
        max_attempts = 7
    )
)

client = boto3.client('ecr', config = config)

def ecr_princ_checker(rand_account_id):
    my_managed_policy ={
        "Version":"2012-10-17",
        "Statement":[
            {
                "Sid":"ReplicationAccessCrossAccount",
                "Effect":"Allow",
                "Principal":{
                    "AWS": f'{rand_account_id}'
                },
                "Action":[
                    "ecr:CreateRepository",
                    "ecr:ReplicateImage"
                ],
                "Resource": [
                    f'arn:aws:ecr:us-east-1:201012399609:repository/7c5c54d66a3e48e29c74f07a1386d362/*' # Needs to be updated to be more generalized
                ]
            }
        ]
    }
        # Implement object to take my_managed_policy and parse for the generated account ID - then send that as return, not the fully policy
    try:
        response = client.put_registry_policy(
            policyText=json.dumps(my_managed_policy)
        )
        print(rand_account_id)
        return("Pass")
# Handles the exception thrown when the Principal doesn't exist
    except client.exceptions.InvalidParameterException as e:
        return("Fail")
    except BaseException as err:
      print(f"Unexpected {err=}, {type(err)=}")
      raise