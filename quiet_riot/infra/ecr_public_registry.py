import json
import logging
import botocore
from botocore import exceptions
from quiet_riot.shared.utils import get_boto3_client, get_current_account_id, print_green, print_yellow
logger = logging.getLogger(__name__)
# ECR Public boto3 docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr-public.html
# ECR Private boto3 docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr.html


class EcrPublicRegistry:
    def __init__(self, region: str, profile: str = None):
        """Create an ECR Public registry"""
        self.region = region
        self.profile = profile
        # Special for ECR
        self.service = "ecr-public"
        sts_client = get_boto3_client(service="sts", profile=self.profile, region=self.region)
        self.account_id = get_current_account_id(sts_client=sts_client)
        self.name = f"quiet-riot-{self.service}-repo"
        self.client = get_boto3_client(service=self.service, profile=profile, region=region)
        # special for ECR
        self.ecr_client = get_boto3_client(service="ecr", profile=profile, region=region)
        self.arn = f"arn:aws:{self.service}:{self.region}:{self.account_id}:repository/{self.name}"

    def create(self):
        """Create the repositories if they do not exist"""
        try:
            self.client.create_repository(
                repositoryName=self.name
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'RepositoryAlreadyExistsException':
                print_yellow(f"\tRepositoryAlreadyExistsException: The repository '{self.arn}' already exists. Skipping...")
            else:
                raise error

    def list(self) -> list:
        resources = []

        paginator = self.client.get_paginator("describe_repositories")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["repositories"]
            for resource in these_resources:
                name = resource.get("repositoryName")
                if self.name in name:
                    arn = resource.get("repositoryArn")
                    resources.append(arn)
        return resources

    def delete(self):
        try:
            response = self.client.delete_repository(
                registryId=self.account_id,
                repositoryName=self.name,
                force=True
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'RepositoryNotFoundException':
                print_yellow(f"\tRepositoryNotFoundException: The repository '{self.arn}' does not exist so we don't need to delete it. Skipping...")
            else:
                raise error

    def principal_check(self, rand_account_id: str):
        my_managed_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "ReplicationAccessCrossAccount",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f'{rand_account_id}'
                    },
                    "Action": [
                        "ecr:CreateRepository",
                        "ecr:ReplicateImage"
                    ],
                    "Resource": [
                        f'arn:aws:ecr:{self.region}:{self.account_id}:repository/{self.name}/*'
                        # Needs to be updated to be more generalized
                    ]
                }
            ]
        }
        # Implement object to take my_managed_policy and parse for the generated account ID - then send that as return, not the fully policy
        try:
            response = self.client.set_repository_policy(
                registryId=self.account_id,
                repositoryName=self.name,
                policyText=json.dumps(my_managed_policy)
            )
            print(rand_account_id)
            return "Pass"
        # Handles the exception thrown when the Principal doesn't exist
        except self.client.exceptions.InvalidParameterException as e:
            return "Fail"
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise
