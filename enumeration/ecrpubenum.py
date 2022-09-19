#!/usr/bin/env python3
import random as rand
import json
import boto3
from botocore.exceptions import ClientError
import uuid
import datetime
from botocore.config import Config
from .. import settings

# config = Config(
#     retries = dict(
#         max_attempts = 10
#     )
# )
# client = boto3.client('ecr-public', config=config)


def ecr_princ_checker(rand_account_id,session):
    client = session.client('ecr-public')

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
            registryId=settings.account_no,
            repositoryName=settings.scan_objects[0],
            policyText=json.dumps(my_managed_policy)
        )
        print(rand_account_id)
        return("Pass")
# Handles the exception thrown when the Principal doesn't exist
    except client.exceptions.InvalidParameterException as e:
        return ("Fail")
    except BaseException as err:
      print(f"You're being throttled by ECR-Public and {rand_account_id} was not checked.")
      pass