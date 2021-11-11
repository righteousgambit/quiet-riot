"""Enumerate every AWS account in existence"""
import os
import sys
import logging
import click
from click_option_group import optgroup
from quiet_riot.shared.utils import set_log_level
logger = logging.getLogger(__name__)


@click.command(
    name="global_enum",
    short_help="Enumerate every AWS account in existence",
)
@optgroup.group("Other Options", help="")
@optgroup.option("-v", "--verbose", "verbosity", help="Log verbosity level.", count=True)
def global_enum(verbosity: int):
    """Enumerate every AWS account in existence"""
    set_log_level(verbosity)

