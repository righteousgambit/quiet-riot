import os
import json
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.client('dynamodb')
sns = boto3.client('sns')
ecr = boto3.client('ecr')
ecr_public = boto3.client('ecr-public')
sqs = boto3.client('sqs')
iam = boto3.client('iam')

SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
ECR_PUBLIC_REPO_ARN = os.environ['ECR_PUBLIC_REPO_ARN']
ECR_PRIVATE_REPO_ARN = os.environ['ECR_PRIVATE_REPO_ARN']
IAM_ROLE_ARN = os.environ['IAM_ROLE_ARN']
DYNAMODB_TABLE = os.environ['DYNAMODB_TABLE']
SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']

def lambda_handler(event, context):
    resource = event['resource']
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)

    # Check if the resource has been queried in the last 30 days
    response = dynamodb.get_item(
        TableName=DYNAMODB_TABLE,
        Key={
            'ResourceId': {'S': resource['id']}
        }
    )

    if 'Item' in response and datetime.fromisoformat(response['Item']['lastQueried']['S']) > thirty_days_ago:
        return response['Item']

    # If not, send the request to the SQS queue
    sqs.send_message(
        QueueUrl=SQS_QUEUE_URL,
        MessageBody=json.dumps(event)
    )

    # Store the result in DynamoDB
    dynamodb.put_item(
        TableName=DYNAMODB_TABLE,
        Item={
            'ResourceId': {'S': resource['id']},
            'lastQueried': {'S': now.isoformat()},
            'ResourceData': {'S': json.dumps(resource)}
        }
    )

    return resource
