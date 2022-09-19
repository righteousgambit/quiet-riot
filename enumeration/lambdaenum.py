#!/usr/bin/env python3
import random as rand
import json
import boto3
from botocore.exceptions import ClientError
import uuid

session = boto3.Session(profile_name='default')
client = session.client('lambda')

def lambda_princ_checker(rand_account_id):
    # Implement object to take my_managed_policy and parse for the generated account ID - then send that as return, not the fully policy
    try:
        response = client.add_permission(
            Action='lambda:InvokeFunction',
            FunctionName='quiet-riot-runner',
            Principal=f'{rand_account_id}',
            StatementId=uuid.uuid4().hex,
        )
        print(rand_account_id)
        return("Pass")
  # Handles the exception thrown when the Principal doesn't exist
    except client.exceptions.InvalidParameterValueException as e:
        return("Fail")