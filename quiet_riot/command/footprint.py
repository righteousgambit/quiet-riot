import os
import sys
import logging
import click
from click_option_group import optgroup
from quiet_riot.shared.utils import set_log_level, write_file_by_lines
from quiet_riot.shared import constants
from quiet_riot.enumeration.thread_manager import ThreadManager
from quiet_riot.enumeration.wordlist import get_rendered_wordlist
from quiet_riot.infra.quiet_infra import QuietInfra
logger = logging.getLogger(__name__)


""""
Example usage to scan Fortinet:

quiet-riot footprint -a 854209929931
"""
@click.command(
    name="footprint",
    short_help="Footprint the services used by an AWS Account",
)
@optgroup.group("Main Arguments", help="")
@optgroup.option("-a", "--target-account", "target_account", type=str, required=True, help="The target AWS account ID.", envvar="TARGET_ACCOUNT")
@optgroup.option("-tc", "--thread-count", "thread_count", type=int, required=False, default=700, help="The thread count.")
@optgroup.group("File options", help="")
@optgroup.option("-w", "--wordlist-file", "wordlist_file", type=click.Path(exists=True), required=True, default=constants.SERVICE_LINKED_ROLES_FILE, help="The wordlist file containing AWS principals to enumerate.")
@optgroup.option("-o", "--output-file", "output_file", type=click.Path(exists=False), required=False, default=os.path.join(os.getcwd(), "valid_scan_results.txt"), help="The file to store results in.")
@optgroup.group("AWS Environment Options", help="")
@optgroup.option("-p", "--profile", "profile", type=str, required=False, help="The AWS IAM profile name.", envvar="AWS_DEFAULT_PROFILE")
@optgroup.option("-r", "--region", "region", type=str, required=False, default="us-east-1", help="The AWS region.", envvar="AWS_DEFAULT_REGION")
@optgroup.group("Other Options", help="")
@optgroup.option("-v", "--verbose", "verbosity", help="Log verbosity level.", count=True)
def footprint(target_account: str, thread_count: int, wordlist_file: str, output_file: str, profile: str, region: str, verbosity: int):
    """Footprint the services used by an AWS Account"""
    set_log_level(verbosity)
    # Get the wordlist and render it as a new list in ARN format, with the account ID and principal type
    wordlist = get_rendered_wordlist(wordlist_principal_type="role", target_account_number=target_account, wordlist_file=wordlist_file)
    # Create the object to manage infra
    quiet_infra = QuietInfra(region=region, profile=profile)
    # Verify that the infrastructure exists first. We want to make the user explicitly create the infra instead of just randomly creating shit in their account
    quiet_infra.verify_exists()

    # Create the thread manager
    thread_manager = ThreadManager(quiet_infra=quiet_infra, wordlist=wordlist, thread_count=thread_count)
    # Scan all the things
    results = thread_manager.scan_with_threads(print_statistics=True)
    if output_file:
        write_file_by_lines(file=output_file, lines=results)
