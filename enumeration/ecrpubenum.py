#!/usr/bin/env python3
import random as rand
import json
import boto3
from botocore.exceptions import ClientError
import uuid
import datetime
from botocore.config import Config

config = Config(
    retries = dict(
        max_attempts = 7
    )
)

client = boto3.client('ecr-public', config = config)

def ecr_princ_checker(rand_account_id):
    my_managed_policy ={
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowPushPull",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    f'{rand_account_id}'
                ]
            },
            "Action": [
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",
                "ecr:CompleteLayerUpload",
                "ecr:GetDownloadUrlForLayer",
                "ecr:InitiateLayerUpload",
                "ecr:PutImage",
                "ecr:UploadLayerPart"
            ]
        }
    ]
}
    try:
        response = client.set_repository_policy(
            registryId='201012399609',
            repositoryName='2346cb8232894e7182d7d9d945dc9b3f',
            policyText=json.dumps(my_managed_policy)
        )
        print(rand_account_id)
        return("Pass")
# Handles the exception thrown when the Principal doesn't exist
    except client.exceptions.InvalidParameterException as e:
        return ("Fail")
    except BaseException as err:
      print(f"Unexpected {err=}, {type(err)=}")
      pass