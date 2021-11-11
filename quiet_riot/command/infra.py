import click
import os
import logging
from click_option_group import optgroup, MutuallyExclusiveOptionGroup
from quiet_riot.shared.utils import set_log_level, print_green, print_red
from quiet_riot.infra.quiet_infra import QuietInfra

logger = logging.getLogger(__name__)


@click.group(name="infra")
def infra():
    """Manage the scanning infrastructure in AWS."""


@infra.command(
    name="create",
    short_help="Create the AWS Infrastructure."
)
@optgroup.group("AWS Environment Options", help="")
@optgroup.option("-p", "--profile", "profile", type=str, required=False, help="The AWS IAM profile name.", envvar="AWS_DEFAULT_PROFILE")
@optgroup.option("-r", "--region", "region", type=str, required=False, default="us-east-1", help="The AWS region.", envvar="AWS_DEFAULT_REGION")
@optgroup.group("Other Options", help="")
@optgroup.option("-v", "--verbose", "verbosity", help="Log verbosity level.", count=True)
def create(profile: str, region: str, verbosity: int):
    set_log_level(verbosity)
    if region:
        os.environ["AWS_DEFAULT_REGION"] = region
    if profile:
        os.environ["AWS_DEFAULT_PROFILE"] = profile
    quiet_infra = QuietInfra(region=region, profile=profile)
    quiet_infra.create()
    resources = quiet_infra.list()
    print_green("SUCCESS! Created all the Quiet Infra scanning infrastructure in AWS.")
    if verbosity >= 1:
        print("Created resources:")
        for resource in resources:
            print(f"\t{resource}")


@infra.command(
    name="destroy",
    short_help="Delete all scanning infrastructure in AWS."
)
@optgroup.group("AWS Environment Options", help="")
@optgroup.option("-p", "--profile", "profile", type=str, required=False, help="The AWS IAM profile name.", envvar="AWS_DEFAULT_PROFILE")
@optgroup.option("-r", "--region", "region", type=str, required=False, default="us-east-1", help="The AWS region.", envvar="AWS_DEFAULT_REGION")
@optgroup.group("Other Options", help="")
@optgroup.option("-v", "--verbose", "verbosity", help="Log verbosity level.", count=True)
def destroy(profile: str, region: str, verbosity: int):
    set_log_level(verbosity)
    if region:
        os.environ["AWS_DEFAULT_REGION"] = region
    if profile:
        os.environ["AWS_DEFAULT_PROFILE"] = profile
    quiet_infra = QuietInfra(region=region, profile=profile)
    print("Destroying the scanning infrastructure in AWS.")
    quiet_infra.delete()
    print_green("SUCCESS! Destroyed scanning infrastructure.")
