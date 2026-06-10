"""Unit tests for the FastAPI app: auth gating, non-blocking scans, email cap.

Uses Starlette's TestClient (no real AWS; the global scanner is mocked).
"""

from datetime import datetime
from unittest import mock

from fastapi.testclient import TestClient
import pytest

from quiet_riot.api import server
from quiet_riot.core.models import ScanResult, ScanType


@pytest.fixture
def client():
    with TestClient(server.app) as c:
        yield c
    server.active_scans.clear()
    server.infrastructure_resources.clear()


def test_health_is_open(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


def test_scan_types_is_open(client):
    r = client.get("/api/scan-types")
    assert r.status_code == 200
    assert len(r.json()["scan_types"]) == 7


def test_generate_emails_is_capped(client, monkeypatch):
    monkeypatch.setattr(server, "API_TOKEN", None)
    monkeypatch.setattr(server, "MAX_EMAIL_RESPONSE", 10)
    r = client.get(
        "/api/generate-emails",
        params={"domain": "x.com", "pattern": "firstname.lastname", "max_emails": 5_000_000},
    )
    assert r.status_code == 200
    assert r.json()["count"] <= 10


def test_auth_enforced_when_token_set(client, monkeypatch):
    monkeypatch.setattr(server, "API_TOKEN", "s3cret")
    assert client.get("/api/scans").status_code == 401
    assert client.get("/api/scans", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.get("/api/scans", headers={"Authorization": "Bearer s3cret"}).status_code == 200
    # Open endpoints stay open regardless of token.
    assert client.get("/health").status_code == 200


def test_auth_disabled_by_default(client, monkeypatch):
    monkeypatch.setattr(server, "API_TOKEN", None)
    assert client.get("/api/scans").status_code == 200


def test_start_scan_returns_202_running_immediately(client, monkeypatch):
    monkeypatch.setattr(server, "API_TOKEN", None)
    monkeypatch.setattr(server, "credentials_required", False)
    fake = mock.Mock()
    fake.run_scan.return_value = ScanResult(
        scan_id="internal",
        scan_type=ScanType.MICROSOFT_365_DOMAINS,
        status="completed",
        valid_principals=[],
        total_scanned=1,
        start_time=datetime.now(),
        end_time=datetime.now(),
    )
    fake.resource_mgr.resources_created = False
    monkeypatch.setattr(server, "scanner", fake)

    r = client.post("/api/scans", json={"scan_type": 2, "domain_name": "example.com"})
    assert r.status_code == 202
    body = r.json()
    assert body["status"] == "running"
    assert "scan_id" in body
