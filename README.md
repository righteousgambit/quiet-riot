# Quiet Riot 
### :notes: *C'mon, Feel The Noise* :notes:
  
_An enumeration tool for scalable, unauthenticated validation of AWS principals; including AWS Acccount IDs, root e-mail addresses, users, and roles._

**Table of Contents**
- [Background](#Background)
    - [Resource-Based IAM Policies](#Resource-Based-IAM-Policies) 
    - [Resource-Based Policy Validation](#Resource-Based-Policy-Validation)
    - [Exploitation](#Exploitation) 
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

### ~~Exploitation~~ "Featureploitation"
Originally identified by Daniel Grzelak (Twitter: [@dagrz](https://twitter.com/dagrz)) and subsequently re-discovered a number of times, this technique can help attackers with a key capability - enumerating attack targets. While AWS considers this capability a "_feature_", I am curious to see what scale of ~~exploitation~~ featureploitation might change AWS perspective. To this end, I have developed an Offensive Security Tool (OST) to exploit this AWS feature for the maximum possible impact. 
  
Even this idea is not new. Will Bengston (Twitter: [@__muscles](https://twitter.com/__muscles)) has [previously suggested this general technique](https://twitter.com/__muscles/status/1433255950358618117?s=20). Seeing as how I haven't found a tool that implements Will's suggestion...and I have very limited development experience, I decided to take the opportunity to hone my python chops.  

### Featureploitation Update
After doing extensive analysis of this method using the AWS Python (Boto3) SDK, I was able to determine that the fundamental bottleneck for scanning (at least for Python and Python-based (awscli) API calls) is I/O in a single-threaded Python application. After modifying the program to run multi-threaded, I finally started getting throttled by the APIs. You can see the results from running various test scans [here](./enumeration/scan-run-statistics.txt). 

After further testing, I finally settled on a combination of SNS and ECR-Public running in US-East-1 in ~40%/60% split with ~600 threads on a 2020 Macbook Air with an M1 and 16 GB RAM. This configuration yields on average ~1100 calls/sec, though this can fluctuate significantly depending on a variety of factors. Under these configurations, I did occasionally throw an exception on a thread from throttling...but you can configure additional re-try attempts via botocore that would eliminate this issue with some performance trade-off.

To attempt every possible Account ID in AWS (1,000,000,000,000) would require an infeasible amount of time given only one account. Even assuming absolute efficiency*, over the course of a day an attacker will only be able to make 95,040,000 validation checks. Over 30 days, this is 2,851,200,000 validation checks and we are still over 28 years away from enumerating every valid AWS Account ID. Fortunately, there is nothing stopping us from registering many AWS accounts and automating this scan. While there is an initial limit of 20 accounts per AWS organization, I was able to get this limit increased for my Organization via console self-service and approval from an AWS representative. The approval occured without any further questions and now I'm off to automating this writ large. Again, assuming absolute efficiency, the 28 years of scanning could potentially be reduced down to ~100 days.

*~1100 API calls/check per second in perpetuity per account and never repeating a guessed Account ID

*Author's Note (10/28/2021): * While not quite ready for release - a wordlist can be fed to enumeration/loadbalancer.py after updating enumeration/snsenum.py and enumeration/ecrpubenum.py with resources you own and you should be able to return valid principals from your list @ valid_principals.txt in the local directory where you run the tool.

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

## API Throttling, Costs, and Other Scalability Considerations
  
AWS services, resources, and service API endpoints have various considerations that impact the approach taken to maximize impact. For the following sub-sections, we'll look at two example services and how the approach and cost differ.

### API Throttling
Each service API endpoint has a standard quota level that is provisioned to end customers by default. The quota specifies how many API calls (requests) can be made per second.

#### SNS

#### Lambda

### Costs
Most AWS services have an associated cost. The services used to stand up Quiet Riot infrastructure for enumeration purposes will have varying degrees of cost associated with them.
  
#### SNS
While [SNS](https://aws.amazon.com/sns/pricing/) does not have a cost associated directly with the creation of the "Topic" that we will be using to test AWS principals and the first 1 million API calls (i.e.) are free,  
  
#### Lambda



## Getting Started With Quiet Riot
### Prerequisites
### Configuration Options