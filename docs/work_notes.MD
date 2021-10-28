
# Research Inspiration
https://twitter.com/donkersgood/status/1433148570723667978
> I figured I'd check the resource policies for some other services too. SQS accepts any input without validation (good!), 
> SNS fails on invalid principals, so do VPC endpoint policies, and S3 too (which is old news).

# Research Thesis
Given the # of services provided by AWS that may support this functionality, it is likely possible to enumerate and track every valid AWS account and a good majority of valid IAM principals across the entire platform using these type of capabilities. However, it will require a very distributed infrastructure to perform.

**Primary Constraints:** 
    - Governance: API Calls per second allowed by AWS
    - Technical: API Calls per second allowed by Boto3/Python SDK
    - Technical: API Calls per second allowed by Compute substrate
    - Technical: API Calls per second allowed 
    - Technical: _One trillion_ (10^12) is a very big number! 

# Notes from Weekend #1 (9/18-9/19/2021)

- **account-id_generator.py**
    - see final _primary constraint_.

- **cleanup.py** 
    - fully functional in current state and will delete any sns topics in the region it's tasked to
- **main.py**
    - topic_pool function will take user input and generate the required number of sns topics 
        - known issue: won't create topics for topic_name(str)=previously provisioned topic; should probably add short high entropy string to name (test before scaling!!!)
        - known issue: only tasks to the region of the relevant global session
        - known issue: # of tasks should probably be pre-defined based on what we can take advantage of - perhaps this is where the trade-off makes sense between 
          set_topic_attributes and create_topic
    - set_topic_attrib function is not properly configured to take in final_list variable (target Topic ARNs, based on what's available in the region)
        - known issue: even though a for loop is implemented to iterate through final_list, there is something wrong with the response:() setup.

## Enumeration Orchestration

S3 to Lambda? to ECS?

## Potential Supported Services

| # | AWS Service | Description | Resource Creation | Principal Checker | Resource Destruction |
| --- | ----------- | ----------- | --------------- |--------------- | ---------- |
| 1 | __SNS__ | Managed Serverless Notification Service | No | Yes | No |
| 2 | __KMS__ | Encryption Key Management Service | Yes | No | No |
| 3 | __SecretsManager__ | Managed Secret Store | Yes | Yes | No |
| 4 | __CodeArtifact__ | Managed Source Code Repository | Yes | Yes | No |
| 5 | __ECR Public__ | Managed Container Registry | Yes | Yes | No |
| 6 | __ECR Private__ | Managed Container Registry | No | Yes | No |
| 7 | __Lambda__ | Managed Serverless Function | No | Yes | No |
| 8 | __s3__ | Managed Serverless Object Store | No | Yes | No |
| 9 | __SES__ | SMTP Automation Service | No | No | No |
| 10 | __ACM__ | Private Certificate Authority | No | No | No |
| 11 | __CodeBuild__ | Software Build Agent | No | No | No |
| 12 | __AWS Backup__ | Managed Backup Service | No | No | No |
| 13 | __Cloud9__ | Managed IDE | No | No | No |
| 14 | __Glue__ | Managed ETL Job Service | No | No | No |
| 15 | __EKS__ | Managed K8s Service | No | No | No |
| 16 | __Lex V2__ | Managed NLP Service | No | No | No |
| 17 | __CloudWatch Logs__ | Managed Log Pipeline/Monitoring | No | No | No |
| 18 | __VPC Endpoints__ | Managed Virtual Network | No | No | No |
| 19 | __Elemental MediaStore__ | No | No | No | No |
| 20 | __OpenSearch__ | Managed ElasticSearch | No | No | No |
| 21 | __EventBridge__ | Managed Serverless Event Hub | No | No | No |
| 22 | __EventBridge Schemas__ | Managed Serverless Event Hub | No | No | No |
| 23 | __IoT__ | Internet-of-Things Management | No | No | No |
| 24 | __s3 Glacier__ | Cold Object Storage | No | No | No |
| 25 | __ECS__ | Managed Container Orchestration | No | No | No |
| 26 | __Serverless Application Repository__ | Managed Source Code Repository | N/A | N/A | N/A |
| 27 | __SQS__ | Managed Serverless Queueing Service | N/A | N/A | N/A |
| 28 | __EFS__ | Managed Serverless Elastic File System | N/A | N/A | N/A |