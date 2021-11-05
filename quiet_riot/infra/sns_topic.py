import json
import logging
import botocore
from botocore import exceptions
from quiet_riot.shared.utils import get_boto3_client, get_current_account_id, print_green, print_yellow
logger = logging.getLogger(__name__)
# SNS boto3 docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sns.html


class SnsTopic:
    def __init__(self, region: str, profile: str = None, name: str = None):
        """Create an SNS Topic"""
        self.region = region
        self.profile = profile
        sts_client = get_boto3_client(service="sts", profile=self.profile, region=self.region)
        self.account_id = get_current_account_id(sts_client=sts_client)
        if name:
            self.name = f"quiet-riot-{name}"
        else:
            self.name = f"quiet-riot"
        self.client = get_boto3_client(service="sns", profile=profile, region=region)
        self.arn = f"arn:aws:sns:{self.region}:{self.account_id}:{self.name}"

    def create(self):
        """Create the resource if it does not exist"""
        try:
            self.client.create_topic(
                Name=self.name,
                Tags=[dict(Key="Project", Value="QuietRiot")],
            )
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'InternalErrorException':
                print_yellow(f"\tThe topic '{self.arn}' already exists. Skipping...")
            else:
                raise error

    def list(self) -> list:
        these_resources = []
        paginator = self.client.get_paginator('list_topics')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            resources = page["Topics"]
            for resource in resources:
                arn = resource.get("TopicArn")
                if self.name in arn:
                    these_resources.append(arn)
        return these_resources

    def delete(self):
        try:
            response = self.client.delete_topic(TopicArn=self.arn)
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'InvalidParameter':
                print_yellow(f"\tThe topic '{self.arn}' does not exist so we don't need to delete it. Skipping...")
            else:
                raise error

    def principal_check(self, rand_account_id: str):
        my_managed_policy = {
            "Statement": [{
                "Sid": "grant-1234-publish",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f'{rand_account_id}'
                },
                "Action": ["sns:Publish"],
                "Resource": self.arn
                # Needs to be replaced with the variable to allow this to be dynamically input.
            }]
        }
        try:
            response = self.client.set_topic_attributes(
                TopicArn=self.arn,
                # Needs to be set dynamically based on what gets spun up by the infra
                AttributeName='Policy',
                AttributeValue=json.dumps(my_managed_policy)
            )
            print(rand_account_id)
            return "Pass"
        # Handles the exception thrown when the Principal doesn't exist
        except self.client.exceptions.InvalidParameterException as e:
            return "Fail"
        except BaseException as err:
            print(f"Unexpected {err=}, {type(err)=}")
            pass
