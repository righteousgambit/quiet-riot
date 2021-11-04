import json
import logging
import botocore
from botocore import exceptions
from quiet_riot.shared.utils import get_boto3_client, get_current_account_id, print_green, print_yellow
logger = logging.getLogger(__name__)
# Secrets manager docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html


class SecretsManagerSecret:
    def __init__(self, region: str, profile: str = None):
        """Create a Secret in Secrets Manager Repository"""
        self.region = region
        self.profile = profile

        self.service = "secretsmanager"
        sts_client = get_boto3_client(service="sts", profile=self.profile, region=self.region)
        self.account_id = get_current_account_id(sts_client=sts_client)
        self.name = f"quiet-riot-{self.region}"
        self.client = get_boto3_client(service=self.service, profile=profile, region=region)
        self.arn = f"arn:aws:{self.service}:{self.region}:{self.account_id}:secret/{self.name}"

    def create(self):
        """Create the secret if it does not exist"""
        try:
            self.client.create_secret(
                Name=self.name
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceExistsException':
                print_yellow(f"\tResourceExistsException: The secret '{self.arn}' already exists. Skipping...")
            else:
                raise error

    def list(self) -> list:
        resources = []

        paginator = self.client.get_paginator("list_secrets")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["SecretList"]
            for resource in these_resources:
                name = resource.get("Name")
                if self.name in name:
                    arn = resource.get("ARN")
                    resources.append(arn)
        return resources

    def delete(self):
        try:
            response = self.client.delete_secret(
                SecretId=self.name,
                ForceDeleteWithoutRecovery=True,
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                print_yellow(f"\tResourceNotFoundException: The secret '{self.arn}' does not exist so we don't need to delete it. Skipping...")
            else:
                raise error

    def principal_check(self, rand_account_id: str):
        my_managed_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "secretsmanager:*",
                    "Principal": {"AWS": f'{rand_account_id}'},
                    "Resource": self.arn
                }
            ]
        }
        try:
            response = self.client.put_resource_policy(
                SecretId=self.name,
                ResourcePolicy=json.dumps(my_managed_policy)
            )
            print(rand_account_id)
            return "Pass"
        # Handles the exception thrown when the Principal doesn't exist
        except self.client.exceptions.MalformedPolicyDocumentException as e:
            return "Fail"
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise
