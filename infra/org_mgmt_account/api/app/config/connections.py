import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

class AWSConnections:
    def __init__(self, region_name: str = "us-east-1"):
        self.region_name = region_name
        self.sqs_client = None
        self.dynamodb_client = None

    def create_sqs_client(self):
        try:
            self.sqs_client = boto3.client('sqs', region_name=self.region_name)
            print("SQS client created successfully")
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"Error creating SQS client: {e}")

    def create_dynamodb_client(self):
        try:
            self.dynamodb_client = boto3.client('dynamodb', region_name=self.region_name)
            print("DynamoDB client created successfully")
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"Error creating DynamoDB client: {e}")

    def get_sqs_client(self):
        if not self.sqs_client:
            self.create_sqs_client()
        return self.sqs_client

    def get_dynamodb_client(self):
        if not self.dynamodb_client:
            self.create_dynamodb_client()
        return self.dynamodb_client

aws_connections = AWSConnections()
