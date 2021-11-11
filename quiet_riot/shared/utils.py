import os
import logging
import boto3
from botocore.config import Config
from colorama import Fore

logger = logging.getLogger(__name__)
END = "\033[0m"
GREY = "\33[90m"


def set_stream_logger(name="quiet_riot", level=logging.DEBUG, format_string=None):  # pylint: disable=redefined-outer-name
    """
    Add a stream handler for the given name and level to the logging module.
    By default, this logs all messages to ``stdout``.
    :type name: string
    :param name: Log name
    :type level: int
    :param level: Logging level, e.g. ``logging.INFO``
    :type format_string: str
    :param format_string: Log message format
    """
    # remove existing handlers. since NullHandler is added by default
    handlers = logging.getLogger(name).handlers
    for handler in handlers:  # pylint: disable=redefined-outer-name
        logging.getLogger(name).removeHandler(handler)
    if format_string is None:
        # format_string = "%(asctime)s %(name)s [%(levelname)s] %(message)s"
        format_string = "[%(levelname)s] %(message)s"
    logger = logging.getLogger(name)  # pylint: disable=redefined-outer-name
    logger.setLevel(level)
    handler = logging.StreamHandler()  # pylint: disable=redefined-outer-name
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)  # pylint: disable=redefined-outer-name
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def set_log_level(verbose: int):
    """
    Set Log Level based on click's count argument.

    Default log level to critical; otherwise, set to: warning for -v, info for -vv, debug for -vvv

    :param verbose: integer for verbosity count.
    :return:
    """
    if verbose == 1:
        set_stream_logger(level=getattr(logging, "WARNING"))
    elif verbose == 2:
        set_stream_logger(level=getattr(logging, "INFO"))
    elif verbose >= 3:
        set_stream_logger(level=getattr(logging, "DEBUG"))
    else:
        set_stream_logger(level=getattr(logging, "CRITICAL"))


def print_red(string):
    print(f"{Fore.RED}{string}{END}")


def print_yellow(string):
    print(f"{Fore.YELLOW}{string}{END}")


def print_green(string):
    print(f"{Fore.GREEN}{string}{END}")


def print_grey(string):
    print(f"{GREY}{string}{END}")
    # Color code from here: https://stackoverflow.com/a/39452138


def print_blue(string):
    print(f"{Fore.BLUE}{string}{END}")


def get_boto3_client(service: str, profile: str = None, region: str = "us-east-1", max_attempts: int = 7) -> boto3.Session.client:
    """Get a boto3 client for a given service"""
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('boto3').setLevel(logging.CRITICAL)
    session_data = {"region_name": region}
    if profile:
        session_data["profile_name"] = profile
    session = boto3.Session(**session_data)

    config = Config(connect_timeout=5, retries={"max_attempts": max_attempts})
    client = session.client(service, config=config)
    return client


def get_current_account_id(sts_client: boto3.Session.client) -> str:
    """Get the current account ID"""
    response = sts_client.get_caller_identity()
    current_account_id = response.get("Account")
    return current_account_id


def get_current_account_id_with_profile(profile: str) -> str:
    """Mostly used for testing purposes so I don't have to create a client every time"""
    sts_client = get_boto3_client(service="sts", profile=profile, region="us-east-1")
    account_id = get_current_account_id(sts_client=sts_client)
    return account_id


def read_file(file: str) -> str:
    with open(file, "r") as f:
        content = f.read()
    return content


def read_file_by_lines(file: str) -> list:
    """Read a file by line in a list"""
    with open(file) as f:
        content = f.read().splitlines()
    return content


def write_file_by_lines(file: str, lines: list):
    # Add newline to the results
    lines = map(lambda x: x + '\n', lines)
    with open(file, "a") as f:
        f.writelines(lines)
