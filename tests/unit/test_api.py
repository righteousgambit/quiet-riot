"""Unit tests for the FastAPI app: auth gating, non-blocking scans, email cap.

Uses Starlette's TestClient (no real AWS; the global scanner is mocked).
"""

from datetime import datetime
import threading
import time
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


def test_start_scan_is_nonblocking_and_reaches_completed(client, monkeypatch):
    """Prove the scan runs off the event loop: POST returns 202 *while the scan is
    still blocked*, /health stays responsive, and the job later reaches completed."""
    monkeypatch.setattr(server, "API_TOKEN", None)
    monkeypatch.setattr(server, "credentials_required", False)
    monkeypatch.setattr(server, "scanner", mock.Mock())  # provides effective_session

    started = threading.Event()
    release = threading.Event()

    def blocking_run(scan_config, cleanup=False):
        started.set()
        if not release.wait(timeout=10):
            raise AssertionError("scan was never released")
        return ScanResult(
            scan_id="internal",
            scan_type=ScanType.MICROSOFT_365_DOMAINS,
            status="completed",
            valid_principals=[],
            total_scanned=1,
            start_time=datetime.now(),
            end_time=datetime.now(),
        )

    fake_scanner = mock.Mock()
    fake_scanner.run_scan.side_effect = blocking_run
    fake_scanner.resource_mgr.resources_created = False
    # Scanner is constructed inside _execute; patch the class to our fake.
    monkeypatch.setattr(server, "Scanner", lambda session: fake_scanner)

    r = client.post("/api/scans", json={"scan_type": 2, "domain_name": "example.com"})
    assert r.status_code == 202
    job = r.json()["scan_id"]
    assert r.json()["status"] == "running"

    # The scan actually began in a worker thread...
    assert started.wait(timeout=5), "background scan never started"
    # ...and the server is NOT blocked while it runs.
    assert client.get("/health").status_code == 200
    assert client.get(f"/api/scans/{job}").json()["status"] == "running"

    # Let the scan finish and confirm the lifecycle write-back to "completed".
    release.set()
    final = "running"
    for _ in range(50):
        final = client.get(f"/api/scans/{job}").json()["status"]
        if final == "completed":
            break
        time.sleep(0.1)
    assert final == "completed"
