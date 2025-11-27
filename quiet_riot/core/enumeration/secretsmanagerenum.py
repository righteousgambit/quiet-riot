#!/usr/bin/env python3
import json

import boto3

client = boto3.client("secretsmanager")


def secretsmanager_princ_checker(rand_account_id):
    my_managed_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "secretsmanager:*",
                "Principal": {"AWS": f"{rand_account_id}"},
                "Resource": "arn:aws:secretsmanager:us-east-1:201012399609:secret:test-secret-cZAvYf",
            }
        ],
    }
    try:
        response = client.put_resource_policy(SecretId="test-secret", ResourcePolicy=json.dumps(my_managed_policy))
        return "Pass"
    # Handles the exception thrown when the Principal doesn't exist
    except client.exceptions.MalformedPolicyDocumentException:
        return "Fail"
