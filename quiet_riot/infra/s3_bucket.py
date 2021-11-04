import json
import logging
import botocore
import boto3
from botocore import exceptions
from quiet_riot.shared.utils import get_boto3_client, get_current_account_id, print_green, print_yellow, print_grey
logger = logging.getLogger(__name__)


class S3Bucket:
    def __init__(self, region: str, profile: str = None):
        """Create an S3 bucket"""
        self.region = region
        self.profile = profile
        self.service = "s3"
        sts_client = get_boto3_client(service="sts", profile=self.profile, region=self.region)
        self.account_id = get_current_account_id(sts_client=sts_client)
        self.name = f"quiet-riot-{self.region}-{self.account_id}"
        self.client = get_boto3_client(service=self.service, profile=profile, region=region)
        self.arn = f"arn:aws:{self.service}:::bucket/{self.name}"

        session = boto3.Session(region_name=region, profile_name=profile)
        s3 = session.resource('s3')
        self.bucket = s3.Bucket(self.name)

    def create(self):
        """Create the repositories if they do not exist"""
        """Create an S3 bucket"""
        try:
            # No location constraint is needed for us-east-1, per https://stackoverflow.com/questions/51912072/invalidlocationconstraint-error-while-creating-s3-bucket-when-the-used-command-i#answer-51912090
            if self.region is None or self.region == "us-east-1":
                self.client.create_bucket(Bucket=self.name)
            else:
                location = {'LocationConstraint': self.region}
                response = self.client.create_bucket(Bucket=self.name, CreateBucketConfiguration=location)
        except self.client.exceptions.BucketAlreadyOwnedByYou as err:
            logging.info(err)
        except botocore.exceptions.ClientError as e:
            logging.error(e)
            return False
        return True

    def delete(self, verbosity: int = 0):
        """Delete the S3 bucket"""
        try:
            # Delete items in the bucket
            self.clean_objects(verbosity=verbosity)
            # then delete the bucket
            self.bucket.delete(ExpectedBucketOwner=self.account_id)
        except botocore.exceptions.ClientError as err:
            print_yellow(f"\tThe bucket {self.bucket.name} does not exist, so there is no need to delete it.")

    def list(self) -> list:
        client = get_boto3_client(service="s3", profile=self.profile, region=self.region)
        response = client.list_buckets()
        resources = []
        for resource in response.get("Buckets"):
            name = resource.get("Name")
            arn = f"arn:aws:s3:::{name}"
            if self.name in name:
                resources.append(arn)
        return resources

    def list_report_objects(self) -> list:
        """List the reports in the bucket"""
        try:
            # Delete items in the bucket
            object_keys = []
            bucket_objects_summary = self.bucket.objects.all()
            for item in bucket_objects_summary:
                object_keys.append(item.key)
            object_keys.sort()
        except botocore.exceptions.ClientError as err:
            print_yellow(f"\tThe bucket {self.bucket.name} does not exist, so there is no need to delete it.")
            object_keys = []
        return object_keys

    def clean_objects(self, verbosity: int = 0):
        """Clean the objects in the bucket"""
        try:
            object_keys = self.list_report_objects()
            # Delete items in the bucket
            self.bucket.objects.all().delete()
            if verbosity > 1:
                for object_key in object_keys:
                    print_grey(f"\tDELETED: {object_key}")
            print_green(f"\tSUCCESS! {len(object_keys)} objects were deleted from the S3 bucket: s3://{self.name}")

        except botocore.exceptions.ClientError as err:
            print_yellow(f"\tThe bucket {self.bucket.name} does not exist, so there is no need to delete it.")

    def principal_check(self, rand_account_id: str):
        my_managed_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Sid': 'AddPerm',
                'Effect': 'Allow',
                'Principal': {"AWS": f'{rand_account_id}'},
                'Action': ['s3:GetObject'],
                'Resource': f'arn:aws:s3:::{self.name}/*'
            }]
        }
        # Implement object to take my_managed_policy and parse for the generated account ID - then send that as return, not the fully policy
        try:
            response = self.client.put_bucket_policy(
                Bucket=self.name,  # TODO name of bucket that we put the policy against.
                ConfirmRemoveSelfBucketAccess=False,
                Policy=json.dumps(my_managed_policy),
                ExpectedBucketOwner=self.account_id  # TODO name of expected bucket owner
            )
            print(rand_account_id)
            return "Pass"

        # Handles the exception thrown when the Principal doesn't exist
        except self.client.exceptions.from_code('MalformedPolicy') as e:
            return 'Fail'
