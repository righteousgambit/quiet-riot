#!/usr/bin/env python3
import random as rand
import json
import boto3
from botocore.exceptions import ClientError
import uuid

client = boto3.client('serverlessrepo')

try:
    response = client.create_application(
        Author='righteousgambitresearch',
        Description='quiet-riot',
        HomePageUrl='https://github.com/righteousgambitresearch/quiet-riot/tree/main/example-code',
        Name=uuid.uuid4().hex,
        SourceCodeUrl='https://github.com/righteousgambitresearch/quiet-riot/tree/52c5035af86f25bc609b82c580fabe7b09fd9f85/example-code',
        TemplateBody='file://template.yaml',
        # TemplateUrl='string'
    )
except client.exceptions.BadRequestException as e:
    print(e)