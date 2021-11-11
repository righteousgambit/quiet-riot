# ---------------------------------------------------------------------------------------------------------------------
# Service linked roles
# ---------------------------------------------------------------------------------------------------------------------
variable "aws_service_names" {
  description = "List of AWS Service Names for which service-linked roles will be created"
  type        = list(string)
  # This list is gathered manually using this link:
  #   <https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_aws-services-that-work-with-iam.html>
  # For most services that support Service-linked roles, follow the link on that
  # page and identify the Service Principal, and add it to the list. Some services
  # require a little more digging, such as actually using the service from the
  # console and checking in IAM for the service-linked role.
  default = [
    "access-analyzer.amazonaws.com",
    "accountdiscovery.ssm.amazonaws.com",
    "appmesh.amazonaws.com",
    "appstream.application-autoscaling.amazonaws.com",
    "autoscaling-plans.amazonaws.com",
    "cassandra.application-autoscaling.amazonaws.com",
    "chime.amazonaws.com",
    "cks.kms.amazonaws.com",
    "cloud9.amazonaws.com",
    "cloudhsm.amazonaws.com",
    "cloudtrail.amazonaws.com",
    "cloudwatch-crossaccount.amazonaws.com",
    "codeguru-profiler.amazonaws.com",
    "codeguru-reviewer.amazonaws.com",
    "codestar-notifications.amazonaws.com",
    "compute-optimizer.amazonaws.com",
    "config.amazonaws.com",
    "connect.amazonaws.com",
    "continuousexport.discovery.amazonaws.com",
    "dax.amazonaws.com",
    "ecs.amazonaws.com",
    "eks.amazonaws.com",
    "eks-nodegroup.amazonaws.com",
    "elasticache.amazonaws.com",
    "elasticbeanstalk.amazonaws.com",
    "elasticfilesystem.amazonaws.com",
    "elasticloadbalancing.amazonaws.com",
    "elasticmapreduce.amazonaws.com",
    "email.cognito-idp.amazonaws.com",
    "es.amazonaws.com",
    "fms.amazonaws.com",
    "fsx.amazonaws.com",
    "globalaccelerator.amazonaws.com",
    "guardduty.amazonaws.com",
    "inspector.amazonaws.com",
    "iotsitewise.amazonaws.com",
    "lakeformation.amazonaws.com",
    "lex.amazonaws.com",
    "logger.cloudfront.amazonaws.com",
    "macie.amazonaws.com",
    "maintenance.elasticbeanstalk.amazonaws.com",
    "managedupdates.elasticbeanstalk.amazonaws.com",
    "management.chatbot.amazonaws.com",
    "networkmanager.amazonaws.com",
    "ops.apigateway.amazonaws.com",
    "organizations.amazonaws.com",
    "rds.amazonaws.com",
    "redshift.amazonaws.com",
    "replicator.lambda.amazonaws.com",
    "robomaker.amazonaws.com",
    "securityhub.amazonaws.com",
    "sms.amazonaws.com",
    "ssm.amazonaws.com",
    "sso.amazonaws.com",
    "support.amazonaws.com",
    "transitgateway.amazonaws.com",
    "trustedadvisor.amazonaws.com",
    "voiceconnector.chime.amazonaws.com",
    "wafv2.amazonaws.com",
    "worklink.amazonaws.com",
  ]
}

variable "excluded_aws_service_names" {
  description = "List of AWS Service Names for which service-linked roles will *NOT* be created"
  type        = list(string)
  default = [
    "cloudtrail.amazonaws.com",
    "codeguru-profiler.amazonaws.com",
    "elasticfilesystem.amazonaws.com",
    "fms.amazonaws.com",
    "fsx.amazonaws.com",
    "networkmanager.amazonaws.com",
    "organizations.amazonaws.com",
    "replicator.lambda.amazonaws.com",
    "ssm.amazonaws.com",
    "sso.amazonaws.com",
    "support.amazonaws.com",
    "transitgateway.amazonaws.com",
    "trustedadvisor.amazonaws.com",
  ]
}

# ---------------------------------------------------------------------------------------------------------------------
# Well known roles
# ---------------------------------------------------------------------------------------------------------------------
variable "well_known_role_names" {
  description = "List of well known role names to create"
  type        = list(string)
  default     = []
}
