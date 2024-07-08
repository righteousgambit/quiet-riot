import boto3
import datetime
from botocore.exceptions import ClientError

# Initialize AWS clients
dynamodb = boto3.client('dynamodb')
sqs = boto3.client('sqs')
sns = boto3.client('sns')
ecr = boto3.client('ecr')
iam = boto3.client('iam')

# Environment variables
DYNAMODB_TABLE = 'MyResultsTable'
SQS_QUEUE_URL = 'MyRequestQueueURL'
SNS_TOPIC_ARN = 'MySNSTopicARN'
ECR_PUBLIC_REPO_ARN = 'MyECRPublicRepoARN'
ECR_PRIVATE_REPO_ARN = 'MyECRPrivateRepoARN'
IAM_ROLE_ARN = 'MyIAMRoleARN'

def lambda_handler(event, context):
    for record in event['Records']:
        message = record['body']
        # Example message parsing, adjust as necessary
        principal = message.get('principal')
        action = message.get('action')
        
        try:
            if action == 'update_policy':
                update_policy(principal)
            else:
                raise ValueError("Unsupported action")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'NoSuchEntity':
                log_to_dynamodb(principal, 'Principal does not exist')
            else:
                log_to_dynamodb(principal, f'Error updating policy: {error_message}')
        
        log_to_dynamodb(principal, 'Policy updated successfully')

def update_policy(principal):
    # Example policy update, adjust as necessary
    iam.update_assume_role_policy(
        RoleName='YourRoleName',
        PolicyDocument=f'{{"Version":"2012-10-17","Statement":[{{"Effect":"Allow","Principal":{{"AWS":"{principal}"}},"Action":"sts:AssumeRole"}}]}}'
    )

def log_to_dynamodb(principal, message):
    dynamodb.put_item(
        TableName=DYNAMODB_TABLE,
        Item={
            'ResourceId': {'S': principal},
            'Timestamp': {'S': datetime.datetime.utcnow().isoformat()},
            'Message': {'S': message}
        }
    )
