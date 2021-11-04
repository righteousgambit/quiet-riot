from quiet_riot.shared.utils import get_boto3_client, get_current_account_id, print_green
from quiet_riot.infra.ecr_repository import EcrRepository
from quiet_riot.infra.ecr_public_registry import EcrPublicRegistry
from quiet_riot.infra.sns_topic import SnsTopic


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
        self.sns_topic = SnsTopic(profile=profile, region=region)

    def create(self):
        """Create the infrastructure"""
        print_green("Creating ECR Private Repository...")
        self.ecr_private_repo.create()
        print_green("Creating ECR Public Repository...")
        self.ecr_public_repo.create()
        print_green("Creating SNS Topics...")
        self.sns_topic.create()

    def list(self):
        """List the infrastructure ARNs"""
        resources = set()
        resources.update(set(self.ecr_public_repo.list()))
        resources.update(set(self.ecr_private_repo.list()))
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
        print_green("Deleting SNS Topic...")
        self.sns_topic.delete()

    def verify_exists(self):
        """Quick method to verify that infrastructure exists"""
        resources = self.list()
        if not resources:
            raise InfraNotCreated("The Infrastructure is not created yet. Make sure you run 'quiet-riot infra create' before proceeding.'")
