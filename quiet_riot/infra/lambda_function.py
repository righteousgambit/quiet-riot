import json
import logging
import botocore
import uuid
import zipfile
import os
import time
from botocore import exceptions
from quiet_riot.shared.utils import get_boto3_client, get_current_account_id, print_green, print_yellow
logger = logging.getLogger(__name__)
# Lambda docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html


class LambdaFunction:
    def __init__(self, region: str, profile: str = None):
        """Create a Secret in Secrets Manager Repository"""
        self.region = region
        self.profile = profile

        self.service = "lambda"
        sts_client = get_boto3_client(service="sts", profile=self.profile, region=self.region)
        self.account_id = get_current_account_id(sts_client=sts_client)
        self.name = f"quiet-riot"
        self.client = get_boto3_client(service=self.service, profile=profile, region=region)
        self.arn = f"arn:aws:{self.service}:{self.region}:{self.account_id}:function/{self.name}"
        self.role_name = f"{self.name}-role"

    def create(self):
        """Create the function if it does not exist"""

        def create_iam_role():
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#IAM.Client.create_role
            try:
                # TODO: IF the role already exists, make sure that the assume role document is accurate
                assume_role_policy_document = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "lambda.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }

                iam_client = get_boto3_client(service="iam", profile=self.profile, region=self.region)

                create_response = iam_client.create_role(
                    RoleName=self.role_name,
                    AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
                    Description="Quiet Riot",
                    Tags=[dict(Key="Project", Value="DogeMachine")]
                )
                role_arn = create_response["Role"]["Arn"]
                return role_arn
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'EntityAlreadyExists':
                    print_yellow(f"\tThe role {self.role_name} already exists")
                else:
                    print("Unexpected error: %s" % e)
                return f"arn:aws:iam::{self.account_id}:role/{self.role_name}"

        iam_role_arn = create_iam_role()

        # https://gist.github.com/steinwaywhw/9d64db15518099c1f26f254ee35c4217
        # Creates a zip file containing our handler code.
        hello_world_python_file = os.path.join(os.path.dirname(__file__), "hello.py")
        hello_world_zip_file = os.path.join(os.path.dirname(__file__), "HelloWorld.zip")
        if not os.path.exists(hello_world_zip_file):
            with zipfile.ZipFile(hello_world_zip_file, 'w') as z:
                z.write(hello_world_python_file)
        # Loads the zip file as binary code.
        with open(hello_world_zip_file, 'rb') as f:
            code = f.read()
        try:
            # "Calling the invoke API action failed with this message: The role defined for the function cannot be assumed by Lambda.
            response = self.client.create_function(
                FunctionName=self.name,
                Role=iam_role_arn,
                Code={"ZipFile": code},
                Description=f"Lambda function where we make a Lambda invocation policy for Quiet Riot",
                Timeout=900,
                MemorySize=256,
                Runtime='python3.7',
                Handler="hello.handler",
                PackageType="Zip"
            )
        # Case: Race condition
        except self.client.exceptions.InvalidParameterValueException as error:
            time.sleep(2)
            self.create()
        except self.client.exceptions.ResourceConflictException as error:
            print_yellow(f"\tThe function already exists. Skipping...")
            pass

    def list(self) -> list:
        resources = []

        paginator = self.client.get_paginator("list_functions")
        page_iterator = paginator.paginate()
        for page in page_iterator:
            these_resources = page["Functions"]
            for resource in these_resources:
                name = resource.get("FunctionName")
                if self.name in name:
                    arn = resource.get("FunctionArn")
                    resources.append(arn)
        return resources

    def delete(self):
        # Delete the Lambda function first
        try:
            response = self.client.delete_function(
                FunctionName=self.name,
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceNotFoundException':
                print_yellow(f"\tThe function '{self.arn}' does not exist so we don't need to delete it. Skipping...")
            else:
                raise error
        # Then delete the IAM Role
        try:
            iam_client = get_boto3_client(service="iam", profile=self.profile, region=self.region)
            response = iam_client.delete_role(
                RoleName=self.role_name
            )
            print_green(f"\tDeleted role: {self.role_name}")
        except self.client.exceptions.NoSuchEntityException as error:
            print_yellow(f"\tThe role {self.role_name} does not exist, so there is no need to delete it.")

    def principal_check(self, rand_account_id: str):
        try:
            response = self.client.add_permission(
                Action='lambda:InvokeFunction',
                FunctionName='quiet-riot-runner',
                Principal=f'{rand_account_id}',
                StatementId=uuid.uuid4().hex,
            )
            print(rand_account_id)
            return "Pass"
        # Handles the exception thrown when the Principal doesn't exist
        except self.client.exceptions.InvalidParameterValueException as e:
            return "Fail"
