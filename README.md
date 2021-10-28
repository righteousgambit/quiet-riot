# Quiet Riot 
### :notes: *C'mon, Feel The Noise* :notes:
  
_An enumeration tool for scalable, unauthenticated validation of AWS principals; including AWS Acccount IDs, root e-mail addresses, users, and roles._

**Table of Contents**
- [Background](#Background)
    - [Resource-Based IAM Policies](#Resource-Based-IAM-Policies) 
    - [Resource-Based Policy Validation](#Resource-Based-Policy-Validation)
    - [~~Exploitation~~ Featureploitation](#Exploitation) 
- [Potential Supported Services](#Potential-Supported-Services)
- [API Throttling, Costs, and Other Scalability Considerations](#API-Throttling-Costs-and-Other-Scalability-Considerations)
- [Getting Started with Quiet Riot](#Getting-Started-with-Quiet-Riot)
    - [Prerequisites](#Prerequisites)
    - [Configuration Options](#Configuration-Options)

## Background

### Resource-Based IAM Policies
[AWS services that work with IAM](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_aws-services-that-work-with-iam.html) include a number of services that support [_"Resource-based policies"_](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html). These resource-based policies allow direct access to AWS service-level resources and are evaluated prior to Identity-based policies when determining whether a given user (unauthenticated user, any authenticated AWS principal, or specific AWS IAM principals) has access to the specified resource. 

![AWS IAM Policy Evaluation Logic](./static/PolicyEvaluationHorizontal.png)
  
### Resource-Based Policy Validation
To determine the validity of a particular resource-based policy, the AWS IAM engine validates the form of a particular policy **and critically** _the included AWS principals_ at the time the policy is attached to the relevant resource. Many services that support such resource-based policies will throw an error for an invalid AWS principal in the policy. This means that a policy containing a single AWS principal can be used as a proxy to validate whether that principal exists or not.

## Potential Supported Services

| # | AWS Service | Description | API Limits | Resource Pricing | Enumeration Capability |
| --- | ----------- | ----------- | --------------- |--------------- | ---------- |
| 1 | __SNS__ | Managed Serverless Notification Service | Unknown | Unknown | Yes |
| 2 | __KMS__ | Encryption Key Management Service | Unknown | Unknown | Yes |
| 3 | __SecretsManager__ | Managed Secret Store | Unknown | Unknown | Yes |
| 4 | __CodeArtifact__ | Managed Source Code Repository | Unknown | Unknown | Yes |
| 5 | __ECR Public__ | Managed Container Registry | Unknown | Unknown | Yes |
| 6 | __ECR Private__ | Managed Container Registry | Unknown | Unknown | Yes |
| 7 | __Lambda__ | Managed Serverless Function | Unknown | Unknown | Yes |
| 8 | __s3__ | Managed Serverless Object Store | Unknown | Unknown | Yes |
| 9 | __SES__ | SMTP Automation Service | Unknown | Unknown | Unknown |
| 10 | __ACM__ | Private Certificate Authority | Unknown | Unknown | Unknown |
| 11 | __CodeBuild__ | Software Build Agent | Unknown | Unknown | Unknown |
| 12 | __AWS Backup__ | Managed Backup Service | Unknown | Unknown | Unknown |
| 13 | __Cloud9__ | Managed IDE | Unknown | Unknown | Unknown |
| 14 | __Glue__ | Managed ETL Job Service | Unknown | Unknown | Unknown |
| 15 | __EKS__ | Managed K8s Service | Unknown | Unknown | Unknown |
| 16 | __Lex V2__ | Managed NLP Service | Unknown | Unknown | Unknown |
| 17 | __CloudWatch Logs__ | Managed Log Pipeline/Monitoring | Unknown | Unknown | Unknown |
| 18 | __VPC Endpoints__ | Managed Virtual Network | Unknown | Unknown | Unknown |
| 19 | __Elemental MediaStore__ | Unknown | Unknown | Unknown | Unknown |
| 20 | __OpenSearch__ | Managed ElasticSearch | Unknown | Unknown | Unknown |
| 21 | __EventBridge__ | Managed Serverless Event Hub | Unknown | Unknown | Unknown |
| 22 | __EventBridge Schemas__ | Managed Serverless Event Hub | Unknown | Unknown | Unknown |
| 23 | __IoT__ | Internet-of-Things Management | Unknown | Unknown | Unknown |
| 24 | __s3 Glacier__ | Cold Object Storage | Unknown | Unknown | Unknown |
| 25 | __ECS__ | Managed Container Orchestration | Unknown | Unknown | Unknown |
| 26 | __Serverless Application Repository__ | Managed Source Code Repository | Unknown | Unknown | No |
| 27 | __SQS__ | Managed Serverless Queueing Service | Unknown | Unknown | No |
| 28 | __EFS__ | Managed Serverless Elastic File System | Unknown | Unknown | No |

## Getting Started With Quiet Riot
### Prerequisites
### Configuration Options