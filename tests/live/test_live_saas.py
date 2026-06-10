"""Live SaaS integration tests — Microsoft 365 and Google Workspace.

These hit external identity endpoints (no AWS required) and are gated behind
``--run-live`` / ``QR_LIVE=1``. They validate the non-AWS enumeration paths.
"""

import pytest

from quiet_riot.core.enumeration_handlers import EnumerationHandler

pytestmark = pytest.mark.live


@pytest.fixture
def handler():
    # The SaaS paths never touch the boto session.
    return EnumerationHandler(session=None)


def test_live_m365_domain_known_tenant(handler):
    """microsoft.com is a real M365 tenant and should validate."""
    valid, checked = handler.scan_microsoft_365_domain("microsoft.com")
    assert checked == 1
    assert valid == ["microsoft.com"]


def test_live_m365_domain_nonexistent(handler):
    valid, checked = handler.scan_microsoft_365_domain("this-domain-does-not-exist-quietriot-test.invalid")
    assert checked == 1
    assert valid == []


def test_live_m365_user_invalid_does_not_crash(handler):
    """An obviously-invalid user returns cleanly, OR (when O365 is rate-limiting us)
    raises ThrottlingError — which is the correct, non-silent throttle behavior."""
    from quiet_riot.core.enumeration_handlers import ThrottlingError

    try:
        valid, checked = handler.scan_microsoft_365_user("not-a-real-user@example.invalid")
    except ThrottlingError:
        pytest.skip("O365 is throttling right now; throttling correctly raised instead of being swallowed")
    assert checked == 1
    assert isinstance(valid, list)


def test_live_google_workspace_gxlu_is_deprecated(handler):
    """Google disabled the gxlu oracle (verified: HTTP 204, no cookies, for a known
    real Workspace account AND a fake one), so this scan can no longer detect
    anyone. Assert the known-dead state instead of pretending it works."""
    valid, checked = handler.scan_google_workspace_user("not-a-real-user@example.invalid")
    assert checked == 1
    assert valid == []
