from quiet_riot.shared.utils import get_boto3_client, get_current_account_id, print_green, print_yellow
from quiet_riot.infra.ecr_repository import EcrRepository
from quiet_riot.infra.ecr_public_registry import EcrPublicRegistry
from quiet_riot.infra.s3_bucket import S3Bucket
from quiet_riot.infra.sns_topic import SnsTopic
from quiet_riot.infra.secrets_manager import SecretsManagerSecret


class InfraNotCreated(Exception):
    pass


class QuietInfra:
    def __init__(self, region: str, profile: str = None):
        self.region = region
        self.profile = profile
        sts_client = get_boto3_client(service="sts", profile=self.profile, region=self.region)
        self.account_id = get_current_account_id(sts_client=sts_client)
        # Attributes per infrastructure type
        self.ecr_public_repo = EcrPublicRegistry(region=region, profile=profile)
        self.ecr_private_repo = EcrRepository(region=region, profile=profile)
        self.s3_bucket = S3Bucket(profile=profile, region=region)
        self.secrets_manager_secret = SecretsManagerSecret(profile=profile, region=region)
        self.sns_topic = SnsTopic(profile=profile, region=region)

    def create(self):
        """Create the infrastructure"""
        print_green("Creating ECR Private Repository...")
        self.ecr_private_repo.create()
        print_green("Creating ECR Public Repository...")
        self.ecr_public_repo.create()
        print_green("Creating S3 Bucket...")
        self.s3_bucket.create()
        print_green("Creating Secrets Manager Secret...")
        self.secrets_manager_secret.create()
        print_green("Creating SNS Topics...")
        self.sns_topic.create()

    def list(self):
        """List the infrastructure ARNs"""
        resources = set()
        resources.update(set(self.ecr_public_repo.list()))
        resources.update(set(self.ecr_private_repo.list()))
        resources.update(set(self.s3_bucket.list()))
        resources.update(set(self.secrets_manager_secret.list()))
        resources.update(set(self.sns_topic.list()))
        resources = list(resources)
        resources.sort()
        return resources

    def delete(self):
        """Delete the Quiet Riot infrastructure"""
        print_green("Deleting ECR Private Repository...")
        self.ecr_private_repo.delete()
        print_green("Deleting ECR Public Repository...")
        self.ecr_public_repo.delete()
        print_green("Deleting S3 Bucket...")
        print_yellow("\tSkipping deletion of S3 bucket to avoid 1 hour delay before bucket with same name can be created.")
        # self.s3_bucket.delete()
        print_green("Deleting Secrets Manager Secret...")
        self.secrets_manager_secret.delete()
        print_green("Deleting SNS Topic...")
        self.sns_topic.delete()

    def verify_exists(self):
        """Quick method to verify that infrastructure exists"""
        infra_resources = self.list()
        # Create a new list that excludes S3. We are skipping deletion of the S3 bucket because otherwise we'd have to wait an hour before trying to create a bucket with the same name again.
        resources = []
        for resource in infra_resources:
            if "s3" not in resource:
                resources.append(resource)
        if not resources:
            raise InfraNotCreated("The Infrastructure is not created yet. Make sure you run 'quiet-riot infra create' before proceeding.'")
