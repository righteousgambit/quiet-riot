import json
import logging
import botocore
from botocore import exceptions
from quiet_riot.shared.utils import get_boto3_client, get_current_account_id, print_green, print_yellow
logger = logging.getLogger(__name__)
# Code Artifact boto3 docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codeartifact.html


class CodeArtifactDomain:
    def __init__(self, region: str, profile: str = None, name: str = None):
        """Create a Code Artifact Domain"""
        self.region = region
        self.profile = profile
        self.service = "codeartifact"
        sts_client = get_boto3_client(service="sts", profile=self.profile, region=self.region)
        self.account_id = get_current_account_id(sts_client=sts_client)
        if name:
            self.name = f"quiet-riot-{name}"
        else:
            self.name = f"quiet-riot"
        self.client = get_boto3_client(service=self.service, profile=profile, region=region)
        self.arn = f"arn:aws:{self.service}:{self.region}:{self.account_id}:domain/{self.name}"

    def create(self):
        """Create the resource if it does not exist"""
        try:
            self.client.create_domain(
                domain=self.name,
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ConflictException':
                print_yellow(f"\tThe domain '{self.arn}' already exists. Skipping...")
            else:
                raise error

    def list(self) -> list:
        these_resources = []
        paginator = self.client.get_paginator('list_domains')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            resources = page["domains"]
            for resource in resources:
                arn = resource.get("arn")
                if self.name in arn:
                    these_resources.append(arn)
        return these_resources

    def delete(self):
        try:
            response = self.client.delete_domain(domain=self.arn, domainOwner=self.account_id)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'InvalidParameter':
                print_yellow(f"\tThe domain '{self.arn}' does not exist so we don't need to delete it. Skipping...")
            else:
                raise error

    def principal_check(self, rand_account_id: str):
        my_managed_policy = {
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
                    "Resource": self.arn
                }
            ]
        }
        try:
            response = self.client.put_domain_permissions_policy(
                domain=self.name,
                domainOwner=self.account_id,  # Requires update with dynamic variable using end user account ID
                policyRevision='test',
                policyDocument=json.dumps(my_managed_policy)
            )
            print(rand_account_id)
            return "Pass"
        # Handles the exception thrown when the Principal doesn't exist
        except self.client.exceptions.InvalidParameterException as e:
            return "Fail"
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            pass
