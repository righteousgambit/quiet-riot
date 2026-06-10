"""Unit tests for Scanner scan-type routing.

The enumeration handler and resource setup are stubbed so we test orchestration
logic only (no real AWS). The key regression here is that ``--scan 5``
(AWS_IAM_PRINCIPALS) is routed instead of raising "Unsupported scan type".
"""

from unittest import mock

import pytest

from quiet_riot.core.models import ScanConfig, ScanType
from quiet_riot.core.scanner import Scanner


@pytest.fixture
def scanner(moto_session, tmp_path):
    s = Scanner(moto_session)
    s.enumeration_handler = mock.Mock()
    s.enumeration_handler.scan_aws_account_ids.return_value = (["123456789012"], 1)
    s.enumeration_handler.scan_aws_services_footprint.return_value = ([], 1)
    s.enumeration_handler.scan_aws_iam_roles.return_value = (["role-hit"], 1)
    s.enumeration_handler.scan_aws_iam_users.return_value = (["user-hit"], 1)
    s.enumeration_handler.scan_microsoft_365_domain.return_value = (["example.com"], 1)
    # Stub real-AWS side effects.
    s._setup_resources = mock.Mock(return_value=None)
    s.resource_mgr.cleanup_all = mock.Mock(return_value=True)
    s.result_handler.save_results = mock.Mock(return_value=tmp_path / "out.txt")
    return s


@pytest.fixture
def wordlist(tmp_path):
    wl = tmp_path / "wl.txt"
    wl.write_text("admin\ndeploy\n")
    return str(wl)


def test_scan_account_ids_routes(scanner, wordlist):
    cfg = ScanConfig(scan_type=ScanType.AWS_ACCOUNT_IDS, wordlist_path=wordlist)
    result = scanner.run_scan(cfg, cleanup=False)
    assert result.status == "completed"
    scanner.enumeration_handler.scan_aws_account_ids.assert_called_once()


def test_scan_iam_principals_routes_to_both_roles_and_users(scanner, wordlist):
    """Regression: scan 5 must enumerate roles AND users, not raise."""
    cfg = ScanConfig(
        scan_type=ScanType.AWS_IAM_PRINCIPALS,
        wordlist_path=wordlist,
        account_id="123456789012",
    )
    result = scanner.run_scan(cfg, cleanup=False)
    assert result.status == "completed"
    scanner.enumeration_handler.scan_aws_iam_roles.assert_called_once()
    scanner.enumeration_handler.scan_aws_iam_users.assert_called_once()
    assert set(result.valid_principals) == {"role-hit", "user-hit"}
    assert result.total_scanned == 2


def test_scan_iam_principals_requires_account_id(scanner, wordlist):
    cfg = ScanConfig(scan_type=ScanType.AWS_IAM_PRINCIPALS, wordlist_path=wordlist)
    result = scanner.run_scan(cfg, cleanup=False)
    assert result.status == "failed"
    assert "account id" in (result.error or "").lower()


def test_scan_m365_domain_routes(scanner):
    cfg = ScanConfig(scan_type=ScanType.MICROSOFT_365_DOMAINS, domain_name="example.com")
    result = scanner.run_scan(cfg, cleanup=False)
    assert result.status == "completed"
    scanner.enumeration_handler.scan_microsoft_365_domain.assert_called_once_with("example.com")
    # M365 domain scans do not provision AWS resources.
    scanner._setup_resources.assert_not_called()


def test_cleanup_called_for_resource_scans(scanner, wordlist):
    cfg = ScanConfig(scan_type=ScanType.AWS_ACCOUNT_IDS, wordlist_path=wordlist)
    scanner.run_scan(cfg, cleanup=True)
    scanner.resource_mgr.cleanup_all.assert_called_once()
