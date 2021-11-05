This Terraform populates an AWS Account that has all the different IAM resources that we enumerate for, and nothing else. It will have all the SLRs that we check for, some dummy users, and other stuff.

We can use these for integration tests. Since AWS Account IDs are clearly no longer sensitive, the account ID that we use is: `227156886084`.

# References

* [Terraform module to managed AWS IAM Service Linked Roles](https://registry.terraform.io/modules/plus3it/tardigrade-service-linked-roles/aws/latest)

