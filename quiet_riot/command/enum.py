import os
import sys
import logging
import click
from click_option_group import optgroup
from quiet_riot.shared.utils import set_log_level
logger = logging.getLogger(__name__)


@click.command(
    name="enum",
    short_help="Enumerate IAM principals (roles or users) in an AWS account.",
)
@optgroup.group("Other Options", help="")
@optgroup.option("-v", "--verbose", "verbosity", help="Log verbosity level.", count=True)
def enum(verbosity: int):
    """Enumerate IAM principals (roles or users) in an AWS account."""
    set_log_level(verbosity)

