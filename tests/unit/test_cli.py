"""Unit tests for the CLI argument parser and scan-type mapping."""

import pytest

from quiet_riot.cli.main import create_parser, map_scan_type
from quiet_riot.core.models import ScanType


def test_parser_requires_scan():
    with pytest.raises(SystemExit):
        create_parser().parse_args([])


def test_parser_parses_scan_and_threads():
    args = create_parser().parse_args(["--scan", "1", "--threads", "50"])
    assert args.scan == 1
    assert args.threads == 50


def test_parser_rejects_out_of_range_scan():
    with pytest.raises(SystemExit):
        create_parser().parse_args(["--scan", "9"])


def test_parser_profile_and_arn():
    args = create_parser().parse_args(
        ["--scan", "5", "--profile", "p", "--arn", "arn:aws:iam::1:role/r", "--account-id", "123456789012"]
    )
    assert args.profile == "p"
    assert args.arn == "arn:aws:iam::1:role/r"
    assert args.account_id == "123456789012"


@pytest.mark.parametrize(
    "num, expected",
    [
        (1, ScanType.AWS_ACCOUNT_IDS),
        (2, ScanType.MICROSOFT_365_DOMAINS),
        (3, ScanType.AWS_SERVICES_FOOTPRINTING),
        (4, ScanType.AWS_ROOT_USER_EMAIL),
        (5, ScanType.AWS_IAM_PRINCIPALS),
        (6, ScanType.MICROSOFT_365_USERS),
        (7, ScanType.GOOGLE_WORKSPACE_USERS),
    ],
)
def test_map_scan_type(num, expected):
    assert map_scan_type(num) is expected
