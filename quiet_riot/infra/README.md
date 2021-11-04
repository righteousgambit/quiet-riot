The technique that we use for enumerating AWS Accounts and principals relies on modifying AWS resource based policies. That is fine for identifying a few AWS Accounts or even hundreds, but if we want to scale this out to every AWS Account in existence, we will have to avoid getting rate limited and fly under the radar.

We spread this technique across multiple resources that support resource-based policies. Here is the checklist of resources, whether they are supported under the old structure or the new structure


Migration status:

- [ ] Code Artifact
- [x] ECR Public
- [x] ECR Private
- [ ] S3 bucket ACLs
- [ ] S3 bucket policies
- [ ] Secrets manager
- [x] SNS Topic

After the above are migrated, we can add on more resources to speed things up in the future.
