"""Unit tests for data models."""

from datetime import datetime, timedelta

from quiet_riot.core.models import ScanConfig, ScanResult, ScanType


def test_scan_type_values_match_cli_numbers():
    assert ScanType.AWS_ACCOUNT_IDS == "1"
    assert ScanType.MICROSOFT_365_DOMAINS == "2"
    assert ScanType.AWS_SERVICES_FOOTPRINTING == "3"
    assert ScanType.AWS_ROOT_USER_EMAIL == "4"
    assert ScanType.AWS_IAM_PRINCIPALS == "5"
    assert ScanType.MICROSOFT_365_USERS == "6"
    assert ScanType.GOOGLE_WORKSPACE_USERS == "7"


def test_scan_type_constructed_from_string():
    assert ScanType(str(5)) is ScanType.AWS_IAM_PRINCIPALS


def test_scan_config_defaults():
    cfg = ScanConfig(scan_type=ScanType.AWS_ACCOUNT_IDS)
    assert cfg.threads == 100
    assert cfg.cleanup is True
    assert cfg.aws_profile == "default"


def test_scan_result_success_rate():
    r = ScanResult(
        scan_id="x",
        scan_type=ScanType.AWS_ACCOUNT_IDS,
        status="completed",
        valid_principals=["a", "b"],
        total_scanned=10,
        start_time=datetime.now(),
    )
    assert r.success_rate == 20.0


def test_scan_result_success_rate_zero_division_safe():
    r = ScanResult(
        scan_id="x",
        scan_type=ScanType.AWS_ACCOUNT_IDS,
        status="completed",
        valid_principals=[],
        total_scanned=0,
        start_time=datetime.now(),
    )
    assert r.success_rate == 0.0


def test_scan_result_duration():
    start = datetime.now()
    r = ScanResult(
        scan_id="x",
        scan_type=ScanType.AWS_ACCOUNT_IDS,
        status="completed",
        valid_principals=[],
        total_scanned=0,
        start_time=start,
        end_time=start + timedelta(seconds=5),
    )
    assert r.duration_seconds == 5.0


def test_scan_result_duration_none_when_unfinished():
    r = ScanResult(
        scan_id="x",
        scan_type=ScanType.AWS_ACCOUNT_IDS,
        status="running",
        valid_principals=[],
        total_scanned=0,
        start_time=datetime.now(),
    )
    assert r.duration_seconds is None
