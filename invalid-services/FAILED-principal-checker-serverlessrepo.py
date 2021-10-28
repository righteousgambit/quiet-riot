#!/usr/bin/env python3

###################################################################
##SAM REPO Technique does not work: Leaving for research purposes##
###################################################################

import random as rand
import json
import boto3
from botocore.exceptions import ClientError
import uuid

client = boto3.client('serverlessrepo')

quantity = input("Enter # of Random Account IDs to Attempt:")
def serverlessrepo_princ_checker(*args, **kwargs):
    #rand_account_id = rand.randint(10**11, 10**12)
    # Implement object to take my_managed_policy and parse for the generated account ID - then send that as return, not the fully policy
    try:
        response = client.put_application_policy(
            ApplicationId='arn:aws:serverlessrepo:us-east-1:201012399609:applications/5c36b0c25594419495343f1407d0864a',
            Statements=[
                {
                    'Actions': [
                        'GetApplication',
                    ],
                    'Principals': [
                        'arn:aws:iam::201012399609:user/conor',
                    ],
                    'StatementId': f'{uuid.uuid4().hex}'
                },
            ]
        )
        return("PASS")
  # Handles the exception thrown when the Principal doesn't exist
    except client.exceptions.BadRequestException as e:
      return(e)

# Creates list to output results
output_list = []
# Append results to output_list TODO output valid Principal ID to file
for i in range(0, int(quantity)): 
  output_list.append(str(serverlessrepo_princ_checker()))

# Output results to console
for i in output_list:
    print(i)


