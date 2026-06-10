"""Live SaaS integration tests — Microsoft 365 and Google Workspace.

These hit external identity endpoints (no AWS required) and are gated behind
``--run-live`` / ``QR_LIVE=1``. They validate the non-AWS enumeration paths.
"""

import os
import time

import pytest

from quiet_riot.core.enumeration_handlers import EnumerationHandler, ThrottlingError

pytestmark = pytest.mark.live

# Known-real accounts/domains for CI canaries, injected via GitHub secrets so the
# values are never committed and are masked in CI logs. Tests skip if unset.
M365_REAL_EMAIL = os.environ.get("QR_TEST_M365_EMAIL")
M365_REAL_DOMAIN = os.environ.get("QR_TEST_M365_DOMAIN")
GOOGLE_REAL_EMAIL = os.environ.get("QR_TEST_GOOGLE_EMAIL")


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


# --------------------------------------------------------------------------- #
# Real-account canaries (CI only — driven by GitHub secrets). These continuously
# verify detection against a known-real account so a silent regression (or, for
# Google, a revival) is caught.
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(not M365_REAL_DOMAIN, reason="QR_TEST_M365_DOMAIN not set")
def test_live_m365_real_domain_detected(handler):
    valid, checked = handler.scan_microsoft_365_domain(M365_REAL_DOMAIN)
    assert checked == 1
    assert valid == [M365_REAL_DOMAIN], "known-real M365 domain should be detected"


@pytest.mark.skipif(not M365_REAL_EMAIL, reason="QR_TEST_M365_EMAIL not set")
def test_live_m365_real_user_detected_as_valid(handler):
    """A known-real M365 user must resolve as VALID (skips if O365 throttles)."""
    for _ in range(4):
        try:
            valid, checked = handler.scan_microsoft_365_user(M365_REAL_EMAIL)
        except ThrottlingError:
            time.sleep(15)
            continue
        assert checked == 1
        assert valid == [M365_REAL_EMAIL], "known-real M365 user should resolve as valid"
        return
    pytest.skip("O365 throttled every attempt")


@pytest.mark.skipif(not GOOGLE_REAL_EMAIL, reason="QR_TEST_GOOGLE_EMAIL not set")
def test_live_google_real_user_canary_confirms_gxlu_dead(handler):
    """Canary: gxlu is dead, so even a known-real Workspace account returns [].
    If this FAILS (returns the user), Google re-enabled gxlu and scan 7 can be
    revived — a wanted signal, not a flaky test."""
    valid, checked = handler.scan_google_workspace_user(GOOGLE_REAL_EMAIL)
    assert checked == 1
    assert valid == [], "gxlu still dead; failure here means Google re-enabled it (revive scan 7)"
