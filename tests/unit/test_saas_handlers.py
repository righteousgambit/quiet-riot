"""Unit tests for the SaaS (M365 / Google Workspace) detection logic.

These mock the HTTP layer so the parsing/branching is covered without network.
The live equivalents (tests/live/test_live_saas.py) verify against real endpoints.
"""

import pytest

from quiet_riot.core import enumeration_handlers
from quiet_riot.core.enumeration_handlers import EnumerationHandler, ThrottlingError


class FakeResponse:
    def __init__(self, text="", status_code=200, cookies=None):
        self.text = text
        self.status_code = status_code
        self.cookies = cookies if cookies is not None else []


@pytest.fixture
def handler():
    return EnumerationHandler(session=None)


# --- Microsoft 365 user ---
def test_m365_user_valid(handler, monkeypatch):
    monkeypatch.setattr(enumeration_handlers.requests, "post", lambda *a, **k: FakeResponse('"IfExistsResult":0,'))
    valid, checked = handler.scan_microsoft_365_user("real@tenant.com")
    assert valid == ["real@tenant.com"]
    assert checked == 1


def test_m365_user_invalid(handler, monkeypatch):
    monkeypatch.setattr(enumeration_handlers.requests, "post", lambda *a, **k: FakeResponse('"IfExistsResult":1,'))
    valid, _ = handler.scan_microsoft_365_user("nope@tenant.com")
    assert valid == []


def test_m365_user_throttling_raises(handler, monkeypatch):
    # Throttling must propagate (ThrottlingError), not be swallowed as a negative.
    monkeypatch.setattr(enumeration_handlers.requests, "post", lambda *a, **k: FakeResponse('"ThrottleStatus":1'))
    with pytest.raises(ThrottlingError):
        handler.scan_microsoft_365_user("x@tenant.com")


# --- Microsoft 365 domain ---
def test_m365_domain_managed(handler, monkeypatch):
    monkeypatch.setattr(
        enumeration_handlers.requests, "get", lambda *a, **k: FakeResponse('"NameSpaceType":"Managed",')
    )
    valid, _ = handler.scan_microsoft_365_domain("tenant.com")
    assert valid == ["tenant.com"]


def test_m365_domain_absent(handler, monkeypatch):
    monkeypatch.setattr(
        enumeration_handlers.requests, "get", lambda *a, **k: FakeResponse('"NameSpaceType":"Unknown",')
    )
    valid, _ = handler.scan_microsoft_365_domain("nope.invalid")
    assert valid == []


# --- Google Workspace (gxlu) ---
def test_google_workspace_gxlu_204_returns_empty(handler, monkeypatch):
    # The real-world state: Google returns 204 with no cookies for everyone.
    monkeypatch.setattr(enumeration_handlers.requests, "get", lambda *a, **k: FakeResponse(status_code=204, cookies=[]))
    valid, checked = handler.scan_google_workspace_user("anyone@workspace.com")
    assert valid == []
    assert checked == 1


def test_google_workspace_legacy_success_path_still_works(handler, monkeypatch):
    # If Google ever re-enables the single-cookie signal, the success path holds.
    monkeypatch.setattr(
        enumeration_handlers.requests, "get", lambda *a, **k: FakeResponse(status_code=200, cookies=["one"])
    )
    valid, _ = handler.scan_google_workspace_user("real@workspace.com")
    assert valid == ["real@workspace.com"]
