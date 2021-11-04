"""
    Metabadger is an AWS Security Tool used for discovering and hardening the Instance Metadata service.
"""
import click
from quiet_riot.command.infra import infra
from quiet_riot.command.footprint import footprint
from quiet_riot.command.global_enum import global_enum
from quiet_riot.command.enum import enum
from quiet_riot.bin.version import __version__


@click.group()
@click.version_option(version=__version__)
def quiet_riot():
    """
    Unauthenticated enumeration of services, roles, and users in an AWS account or by every AWS account in existence.
    """


quiet_riot.add_command(enum)
quiet_riot.add_command(global_enum)
quiet_riot.add_command(footprint)
quiet_riot.add_command(infra)


def main():
    """Unauthenticated enumeration of services, roles, and users in an AWS account or by every AWS account in existence."""
    quiet_riot()


if __name__ == "__main__":
    quiet_riot()
