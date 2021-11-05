This Terraform populates an AWS Account that has all the different IAM resources that we enumerate for, and nothing else. It will have all the SLRs that we check for, some dummy users, and other stuff.

We can use these for integration tests. Since AWS Account IDs are clearly no longer sensitive, the account ID that we use is: `227156886084`.

# Instructions

Feel free to use these instructions to replicate them in your own test environment.

## Creating the resources

* Ensure you are authenticated to AWS with admin privileges
* Install Terraform 0.14.0 and create the resources in AWS:

```bash
brew install tfenv
tfenv install 0.14.0
terraform init
terraform plan
terraform apply -auto-approve
```

## Validating resource deployment

### Listing all SLRs

* To list the Service Linked Roles (SLRs) that were created, run the following:

```bash
aws iam list-roles | jq ".Roles" | jq -r ".[].Arn" | grep "aws-service-role"
```

The output will look like the following:

<details>
<summary>Click to expand!</summary>
<p>

```
arn:aws:iam::227156886084:role/aws-service-role/access-analyzer.amazonaws.com/AWSServiceRoleForAccessAnalyzer
arn:aws:iam::227156886084:role/aws-service-role/braket.amazonaws.com/AWSServiceRoleForAmazonBraket
arn:aws:iam::227156886084:role/aws-service-role/chime.amazonaws.com/AWSServiceRoleForAmazonChime
arn:aws:iam::227156886084:role/aws-service-role/transcription.chime.amazonaws.com/AWSServiceRoleForAmazonChimeTranscription
arn:aws:iam::227156886084:role/aws-service-role/voiceconnector.chime.amazonaws.com/AWSServiceRoleForAmazonChimeVoiceConnector
arn:aws:iam::227156886084:role/aws-service-role/codeguru-reviewer.amazonaws.com/AWSServiceRoleForAmazonCodeGuruReviewer
arn:aws:iam::227156886084:role/aws-service-role/email.cognito-idp.amazonaws.com/AWSServiceRoleForAmazonCognitoIdpEmailService
arn:aws:iam::227156886084:role/aws-service-role/connect.amazonaws.com/AWSServiceRoleForAmazonConnect
arn:aws:iam::227156886084:role/aws-service-role/eks.amazonaws.com/AWSServiceRoleForAmazonEKS
arn:aws:iam::227156886084:role/aws-service-role/eks-connector.amazonaws.com/AWSServiceRoleForAmazonEKSConnector
arn:aws:iam::227156886084:role/aws-service-role/eks-fargate.amazonaws.com/AWSServiceRoleForAmazonEKSForFargate
arn:aws:iam::227156886084:role/aws-service-role/eks-nodegroup.amazonaws.com/AWSServiceRoleForAmazonEKSNodegroup
arn:aws:iam::227156886084:role/aws-service-role/es.amazonaws.com/AWSServiceRoleForAmazonElasticsearchService
arn:aws:iam::227156886084:role/aws-service-role/emr-containers.amazonaws.com/AWSServiceRoleForAmazonEMRContainers
arn:aws:iam::227156886084:role/aws-service-role/guardduty.amazonaws.com/AWSServiceRoleForAmazonGuardDuty
arn:aws:iam::227156886084:role/aws-service-role/inspector.amazonaws.com/AWSServiceRoleForAmazonInspector
arn:aws:iam::227156886084:role/aws-service-role/macie.amazonaws.com/AWSServiceRoleForAmazonMacie
arn:aws:iam::227156886084:role/aws-service-role/mq.amazonaws.com/AWSServiceRoleForAmazonMQ
arn:aws:iam::227156886084:role/aws-service-role/accountdiscovery.ssm.amazonaws.com/AWSServiceRoleForAmazonSSM_AccountDiscovery
arn:aws:iam::227156886084:role/aws-service-role/opsinsights.ssm.amazonaws.com/AWSServiceRoleForAmazonSSM_OpsInsights
arn:aws:iam::227156886084:role/aws-service-role/worklink.amazonaws.com/AWSServiceRoleForAmazonWorkLink
arn:aws:iam::227156886084:role/aws-service-role/events.workmail.amazonaws.com/AWSServiceRoleForAmazonWorkMailEvents
arn:aws:iam::227156886084:role/aws-service-role/ops.apigateway.amazonaws.com/AWSServiceRoleForAPIGateway
arn:aws:iam::227156886084:role/aws-service-role/appstream.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_AppStreamFleet
arn:aws:iam::227156886084:role/aws-service-role/cassandra.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_CassandraTable
arn:aws:iam::227156886084:role/aws-service-role/comprehend.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ComprehendEndpoint
arn:aws:iam::227156886084:role/aws-service-role/custom-resource.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_CustomResource
arn:aws:iam::227156886084:role/aws-service-role/dynamodb.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_DynamoDBTable
arn:aws:iam::227156886084:role/aws-service-role/ec2.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_EC2SpotFleetRequest
arn:aws:iam::227156886084:role/aws-service-role/ecs.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ECSService
arn:aws:iam::227156886084:role/aws-service-role/elasticache.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ElastiCacheRG
arn:aws:iam::227156886084:role/aws-service-role/kafka.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_KafkaCluster
arn:aws:iam::227156886084:role/aws-service-role/lambda.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_LambdaConcurrency
arn:aws:iam::227156886084:role/aws-service-role/neptune.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_NeptuneCluster
arn:aws:iam::227156886084:role/aws-service-role/rds.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_RDSCluster
arn:aws:iam::227156886084:role/aws-service-role/sagemaker.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_SageMakerEndpoint
arn:aws:iam::227156886084:role/aws-service-role/continuousexport.discovery.amazonaws.com/AWSServiceRoleForApplicationDiscoveryServiceContinuousExport
arn:aws:iam::227156886084:role/aws-service-role/mgn.amazonaws.com/AWSServiceRoleForApplicationMigrationService
arn:aws:iam::227156886084:role/aws-service-role/appmesh.amazonaws.com/AWSServiceRoleForAppMesh
arn:aws:iam::227156886084:role/aws-service-role/apprunner.amazonaws.com/AWSServiceRoleForAppRunner
arn:aws:iam::227156886084:role/aws-service-role/auditmanager.amazonaws.com/AWSServiceRoleForAuditManager
arn:aws:iam::227156886084:role/aws-service-role/autoscaling-plans.amazonaws.com/AWSServiceRoleForAutoScalingPlans_EC2AutoScaling
arn:aws:iam::227156886084:role/aws-service-role/management.chatbot.amazonaws.com/AWSServiceRoleForAWSChatbot
arn:aws:iam::227156886084:role/aws-service-role/cloud9.amazonaws.com/AWSServiceRoleForAWSCloud9
arn:aws:iam::227156886084:role/aws-service-role/license-manager.master-account.amazonaws.com/AWSServiceRoleForAWSLicenseManagerMasterAccountRole
arn:aws:iam::227156886084:role/aws-service-role/license-manager.member-account.amazonaws.com/AWSServiceRoleForAWSLicenseManagerMemberAccountRole
arn:aws:iam::227156886084:role/aws-service-role/license-manager.amazonaws.com/AWSServiceRoleForAWSLicenseManagerRole
arn:aws:iam::227156886084:role/aws-service-role/panorama.amazonaws.com/AWSServiceRoleForAWSPanorama
arn:aws:iam::227156886084:role/aws-service-role/servicecatalog-appregistry.amazonaws.com/AWSServiceRoleForAWSServiceCatalogAppRegistry
arn:aws:iam::227156886084:role/aws-service-role/backup.amazonaws.com/AWSServiceRoleForBackup
arn:aws:iam::227156886084:role/aws-service-role/reports.backup.amazonaws.com/AWSServiceRoleForBackupReports
arn:aws:iam::227156886084:role/aws-service-role/bugbust.amazonaws.com/AWSServiceRoleForBugBust
arn:aws:iam::227156886084:role/aws-service-role/acm.amazonaws.com/AWSServiceRoleForCertificateManager
arn:aws:iam::227156886084:role/aws-service-role/logger.cloudfront.amazonaws.com/AWSServiceRoleForCloudFrontLogger
arn:aws:iam::227156886084:role/aws-service-role/cloudhsm.amazonaws.com/AWSServiceRoleForCloudHSM
arn:aws:iam::227156886084:role/aws-service-role/events.amazonaws.com/AWSServiceRoleForCloudWatchEvents
arn:aws:iam::227156886084:role/aws-service-role/codestar-notifications.amazonaws.com/AWSServiceRoleForCodeStarNotifications
arn:aws:iam::227156886084:role/aws-service-role/compute-optimizer.amazonaws.com/AWSServiceRoleForComputeOptimizer
arn:aws:iam::227156886084:role/aws-service-role/config.amazonaws.com/AWSServiceRoleForConfig
arn:aws:iam::227156886084:role/aws-service-role/dax.amazonaws.com/AWSServiceRoleForDAX
arn:aws:iam::227156886084:role/aws-service-role/devops-guru.amazonaws.com/AWSServiceRoleForDevOpsGuru
arn:aws:iam::227156886084:role/aws-service-role/directconnect.amazonaws.com/AWSServiceRoleForDirectConnect
arn:aws:iam::227156886084:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS
arn:aws:iam::227156886084:role/aws-service-role/elasticache.amazonaws.com/AWSServiceRoleForElastiCache
arn:aws:iam::227156886084:role/aws-service-role/elasticmapreduce.amazonaws.com/AWSServiceRoleForEMRCleanup
arn:aws:iam::227156886084:role/aws-service-role/fis.amazonaws.com/AWSServiceRoleForFIS
arn:aws:iam::227156886084:role/aws-service-role/globalaccelerator.amazonaws.com/AWSServiceRoleForGlobalAccelerator
arn:aws:iam::227156886084:role/aws-service-role/ssm-incidents.amazonaws.com/AWSServiceRoleForIncidentManager
arn:aws:iam::227156886084:role/aws-service-role/iotsitewise.amazonaws.com/AWSServiceRoleForIoTSiteWise
arn:aws:iam::227156886084:role/aws-service-role/ivs.amazonaws.com/AWSServiceRoleForIVSRecordToS3
arn:aws:iam::227156886084:role/aws-service-role/kafkaconnect.amazonaws.com/AWSServiceRoleForKafkaConnect
arn:aws:iam::227156886084:role/aws-service-role/cks.kms.amazonaws.com/AWSServiceRoleForKeyManagementServiceCustomKeyStores
arn:aws:iam::227156886084:role/aws-service-role/mrk.kms.amazonaws.com/AWSServiceRoleForKeyManagementServiceMultiRegionKeys
arn:aws:iam::227156886084:role/aws-service-role/lakeformation.amazonaws.com/AWSServiceRoleForLakeFormationDataAccess
arn:aws:iam::227156886084:role/aws-service-role/lex.amazonaws.com/AWSServiceRoleForLexBots
arn:aws:iam::227156886084:role/aws-service-role/channels.lex.amazonaws.com/AWSServiceRoleForLexChannels
arn:aws:iam::227156886084:role/aws-service-role/lexv2.amazonaws.com/AWSServiceRoleForLexV2Bots
arn:aws:iam::227156886084:role/aws-service-role/channels.lexv2.amazonaws.com/AWSServiceRoleForLexV2Channels
arn:aws:iam::227156886084:role/aws-service-role/delivery.logs.amazonaws.com/AWSServiceRoleForLogDelivery
arn:aws:iam::227156886084:role/aws-service-role/license-management.marketplace.amazonaws.com/AWSServiceRoleForMarketplaceLicenseManagement
arn:aws:iam::227156886084:role/aws-service-role/mediatailor.amazonaws.com/AWSServiceRoleForMediaTailor
arn:aws:iam::227156886084:role/aws-service-role/memorydb.amazonaws.com/AWSServiceRoleForMemoryDB
arn:aws:iam::227156886084:role/aws-service-role/migrationhub.amazonaws.com/AWSServiceRoleForMigrationHub
arn:aws:iam::227156886084:role/aws-service-role/migrationhub-strategy.amazonaws.com/AWSServiceRoleForMigrationHubStrategy
arn:aws:iam::227156886084:role/aws-service-role/network-firewall.amazonaws.com/AWSServiceRoleForNetworkFirewall
arn:aws:iam::227156886084:role/aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS
arn:aws:iam::227156886084:role/aws-service-role/redshift.amazonaws.com/AWSServiceRoleForRedshift
arn:aws:iam::227156886084:role/aws-service-role/robomaker.amazonaws.com/AWSServiceRoleForRoboMaker
arn:aws:iam::227156886084:role/aws-service-role/route53resolver.amazonaws.com/AWSServiceRoleForRoute53Resolver
arn:aws:iam::227156886084:role/aws-service-role/storage-lens.s3.amazonaws.com/AWSServiceRoleForS3StorageLens
arn:aws:iam::227156886084:role/aws-service-role/securityhub.amazonaws.com/AWSServiceRoleForSecurityHub
arn:aws:iam::227156886084:role/aws-service-role/sms.amazonaws.com/AWSServiceRoleForSMS
arn:aws:iam::227156886084:role/aws-service-role/support.amazonaws.com/AWSServiceRoleForSupport
arn:aws:iam::227156886084:role/aws-service-role/opsdatasync.ssm.amazonaws.com/AWSServiceRoleForSystemsManagerOpsDataSync
arn:aws:iam::227156886084:role/aws-service-role/trustedadvisor.amazonaws.com/AWSServiceRoleForTrustedAdvisor
arn:aws:iam::227156886084:role/aws-service-role/waf.amazonaws.com/AWSServiceRoleForWAFLogging
arn:aws:iam::227156886084:role/aws-service-role/waf-regional.amazonaws.com/AWSServiceRoleForWAFRegionalLogging
arn:aws:iam::227156886084:role/aws-service-role/wafv2.amazonaws.com/AWSServiceRoleForWAFV2Logging
```
</details>


### Listing well-known IAM Roles

You can also list all the other roles with the following (using reverse grep):

```bash
 aws iam list-roles | jq ".Roles" | jq -r ".[].Arn" | grep -v "aws-service-role"
```


<details>
<summary>Click to expand!</summary>
<p>

```
arn:aws:iam::227156886084:role/ACCOUNTADMIN
arn:aws:iam::227156886084:role/alertlogic
arn:aws:iam::227156886084:role/Alert_Logic_Cloud_Defender
arn:aws:iam::227156886084:role/ANALYTICSDEVELOPER
arn:aws:iam::227156886084:role/AquaRole
arn:aws:iam::227156886084:role/AquasecRole
arn:aws:iam::227156886084:role/aws-elasticbeanstalk-ec2-role
arn:aws:iam::227156886084:role/AWS-Landing-Zone-ConfigRecorderRole
arn:aws:iam::227156886084:role/AWSCloudFormationStackSetExecutionRole
arn:aws:iam::227156886084:role/AWSControlTowerCloudTrailRole
arn:aws:iam::227156886084:role/AWSControlTowerStackSetRole
arn:aws:iam::227156886084:role/AWSGlueServiceRoleDefault
arn:aws:iam::227156886084:role/BILLING
arn:aws:iam::227156886084:role/bp-cloudhealth
arn:aws:iam::227156886084:role/bulletproof
arn:aws:iam::227156886084:role/cb-access
arn:aws:iam::227156886084:role/cloudability
arn:aws:iam::227156886084:role/cloudbreak
arn:aws:iam::227156886084:role/cloudcheckr
arn:aws:iam::227156886084:role/cloudcraft
arn:aws:iam::227156886084:role/CloudMGR
arn:aws:iam::227156886084:role/cloudsploit
arn:aws:iam::227156886084:role/CloudSploitRole
arn:aws:iam::227156886084:role/datadog
arn:aws:iam::227156886084:role/DatadogAWSIntegrationRole
arn:aws:iam::227156886084:role/deepsecurity
arn:aws:iam::227156886084:role/dome9
arn:aws:iam::227156886084:role/Dome9-Connect
arn:aws:iam::227156886084:role/Dome9Connect
arn:aws:iam::227156886084:role/DSWebAppsScanningRole
arn:aws:iam::227156886084:role/dynatrace
arn:aws:iam::227156886084:role/ECS-SERVICE-LINKED-ROLE
arn:aws:iam::227156886084:role/EMR_DefaultRole
arn:aws:iam::227156886084:role/EMR_EC2_DefaultRole
arn:aws:iam::227156886084:role/freshservice
arn:aws:iam::227156886084:role/FullLambdaAccess
arn:aws:iam::227156886084:role/globus
arn:aws:iam::227156886084:role/GrafanaCloudWatch
arn:aws:iam::227156886084:role/instaclustr
arn:aws:iam::227156886084:role/keyWatch
arn:aws:iam::227156886084:role/kochava
arn:aws:iam::227156886084:role/KochavaReadS3
arn:aws:iam::227156886084:role/LambdaAdminAccess
arn:aws:iam::227156886084:role/loggly
arn:aws:iam::227156886084:role/loggly-role
arn:aws:iam::227156886084:role/Loggly_aws
arn:aws:iam::227156886084:role/mediatemple
arn:aws:iam::227156886084:role/mongodb
arn:aws:iam::227156886084:role/MtSecurityScan
arn:aws:iam::227156886084:role/myMMSRole
arn:aws:iam::227156886084:role/newrelic
arn:aws:iam::227156886084:role/NewRelic-Infrastructure-AWS-Integration
arn:aws:iam::227156886084:role/okta
arn:aws:iam::227156886084:role/OktaSSO
arn:aws:iam::227156886084:role/opsclarity
arn:aws:iam::227156886084:role/OpsClarity-Access
arn:aws:iam::227156886084:role/opsworks
arn:aws:iam::227156886084:role/orbitera
arn:aws:iam::227156886084:role/OrganizationAccountAccessRole
arn:aws:iam::227156886084:role/OrganizationFormationBuildAccessRole
arn:aws:iam::227156886084:role/OrgMgmtRole
arn:aws:iam::227156886084:role/Prisma
arn:aws:iam::227156886084:role/PrismaCloud
arn:aws:iam::227156886084:role/PrismaCloudCustomRole
arn:aws:iam::227156886084:role/PrismaCloudRole
arn:aws:iam::227156886084:role/redline
arn:aws:iam::227156886084:role/redline13
arn:aws:iam::227156886084:role/RedlineAccess
arn:aws:iam::227156886084:role/roleWatch
arn:aws:iam::227156886084:role/s3stat
arn:aws:iam::227156886084:role/service-codebuild-mirza-service-role
arn:aws:iam::227156886084:role/signalfx
arn:aws:iam::227156886084:role/skeddly
arn:aws:iam::227156886084:role/stackdriver
arn:aws:iam::227156886084:role/teraproc
arn:aws:iam::227156886084:role/teraproc-access
arn:aws:iam::227156886084:role/threatstack
arn:aws:iam::227156886084:role/threatstackrole
arn:aws:iam::227156886084:role/workspaces
arn:aws:iam::227156886084:role/workspaces_defaultrole
```
</details>

### You can list all the roles together with:

```bash
aws iam list-roles | jq ".Roles" | jq -r ".[].Arn"
```

# References

* [Terraform module to managed AWS IAM Service Linked Roles](https://registry.terraform.io/modules/plus3it/tardigrade-service-linked-roles/aws/latest)

