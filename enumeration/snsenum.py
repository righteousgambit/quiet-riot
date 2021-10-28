#!/usr/bin/env python3
import random as rand
import json
import boto3
from botocore.exceptions import ClientError
import datetime
from botocore.config import Config

config = Config(
    retries = dict(
        max_attempts = 7
    )
)

# Establish boto3 sns session
client = boto3.client('sns', config = config)

valid_list = []

def sns_princ_checker(rand_account_id):
    my_managed_policy = {
      "Statement": [{
        "Sid": "grant-1234-publish",
        "Effect": "Allow",
        "Principal": {
          "AWS": f'{rand_account_id}'
        },
        "Action": ["sns:Publish"],
        "Resource": "arn:aws:sns:us-east-1:201012399609:test-topic" # Needs to be replaced with the variable to allow this to be dynamically input.
      }]
    }
    try:
      response = client.set_topic_attributes(
        TopicArn='arn:aws:sns:us-east-1:201012399609:test-topic', # Needs to be set dynamically based on what gets spun up by the infra
        AttributeName='Policy',
        AttributeValue=json.dumps(my_managed_policy)
    )
      print(rand_account_id)
      return("Pass")
  # Handles the exception thrown when the Principal doesn't exist
    except client.exceptions.InvalidParameterException as e:
      return("Fail")
    except BaseException as err:
      print(f"Unexpected {err=}, {type(err)=}")
      pass