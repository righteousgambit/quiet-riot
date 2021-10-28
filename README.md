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

### ~~Exploitation~~ "Featureploitation"
Originally identified by Daniel Grzelak (Twitter: [@dagrz](https://twitter.com/dagrz)) and subsequently re-discovered a number of times, this technique can help attackers with a key capability - enumerating attack targets (Account IDs) and the associated footprint (root account e-mail, roles, users). In particular, static vendor roles and AWS "service-linked" roles give strong insights into the services and platforms/applications that a particular AWS account has configured. While AWS considers this capability a "_feature_", I am curious to see what scale of ~~exploitation~~ featureploitation might change AWS perspective. To this end, I have developed an Offensive Security Tool (OST) to exploit this AWS feature for the maximum possible impact. 
  
Even this idea is not new. Will Bengston (Twitter: [@__muscles](https://twitter.com/__muscles)) has [previously suggested a similar technique](https://twitter.com/__muscles/status/1433255950358618117?s=20). Seeing as how I haven't found a tool that implements Will's suggestion and I have very limited development experience, I decided to take the opportunity to hone my python chops further.  

### Featureploitation Limits
#### Throttling
After performing extensive analysis of scaling methods using the AWS Python (Boto3) SDK, I was able to determine that the bottleneck for scanning (at least for Python and awscli -based tools) is I/O capacity of a single-threaded Python application. After modifying the program to run with multiple threads, I was able to trigger exceptions in individual threads due to throttling by the various AWS APIs. You can see the results from running a few benchmarking test scans [here](./results/scan-run-statistics.txt). APIs that I tested had wildly different throttling limits and notably, s3 bucket policy attempts took ~10x as long as similar attempts against other services.

With further testing, I settled on a combination of SNS, ECR-Public, and ECR-Private services running in US-East-1 in ~40%/50%/10% configuration split with ~700 threads. The machine I used was a 2020 Macbook Air (M1 and 16 GB RAM). This configuration yielded on average ~1100 calls/sec, though the actual number of calls can fluctuate significantly depending on a variety of factors including network connectivity. Under these configurations, I did occasionally throw an exception on a thread from throttling...but I have subsequently configured additional (4 -> 7) re-try attempts via botocore that would eliminate this issue with some performance trade-off.

#### Computational Difficulty
To attempt every possible Account ID in AWS (1,000,000,000,000) would require an infeasible amount of time given only one account. Even assuming absolute efficiency*, over the course of a day an attacker will only be able to make 95,040,000 validation checks. Over 30 days, this is 2,851,200,000 validation checks and we are still over 28 years away from enumerating every valid AWS Account ID. Fortunately, there is nothing stopping us from registering many AWS accounts and automating this scan. While there is an initial limit of 20 accounts per AWS organization, I was able to get this limit increased for my Organization via console self-service and approval from an AWS representative. The approval occured without any further questions and now I'm off to automating this writ large. Again, assuming absolute efficiency, the 28 years of scanning could potentially be reduced down to ~100 days.

*~1100 API calls/check per second in perpetuity per account and never repeating a guessed Account ID.

#### Wordlists
TODO: Web Scraping, ect.

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