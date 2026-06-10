"""Pytest configuration, fixtures, and live-test gating for Quiet Riot."""

import os

import boto3
import pytest

_LIVE_ENV = os.environ.get("QR_LIVE", "").lower() in ("1", "true", "yes")


def pytest_addoption(parser):
    parser.addoption(
        "--run-live",
        action="store_true",
        default=False,
        help="run live tests that hit real AWS / SaaS endpoints (also enabled by QR_LIVE=1)",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "live: requires real AWS credentials / network access")
    config.addinivalue_line("markers", "integration: integration-level test")


def _live_enabled(config) -> bool:
    return bool(config.getoption("--run-live") or _LIVE_ENV)


def pytest_collection_modifyitems(config, items):
    if _live_enabled(config):
        return
    skip_live = pytest.mark.skip(reason="live test; pass --run-live or set QR_LIVE=1")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture(autouse=True)
def _reset_config_singleton():
    """Reset the Config singleton so global state never leaks between tests."""
    from quiet_riot import config as _config

    _config.Config._instance = None
    _config.Config._initialized = False
    yield
    _config.Config._instance = None
    _config.Config._initialized = False


@pytest.fixture
def aws_region() -> str:
    return os.environ.get("AWS_REGION", "us-east-1")


@pytest.fixture
def moto_session(aws_region):
    """A boto3 Session wrapped in moto's mock_aws (no real AWS calls)."""
    from moto import mock_aws

    with mock_aws():
        yield boto3.Session(
            region_name=aws_region,
            aws_access_key_id="testing",
            aws_secret_access_key="testing",
        )


@pytest.fixture
def live_session(aws_region):
    """A real boto3 Session from ambient credentials; skips if none are available."""
    session = boto3.Session(region_name=aws_region)
    try:
        ident = session.client("sts").get_caller_identity()
    except Exception as exc:  # noqa: BLE001 - we want any failure to skip, not error
        pytest.skip(f"no live AWS credentials available: {exc}")
    # Expose account id for tests that need a known-valid principal.
    session._qr_account_id = ident["Account"]  # type: ignore[attr-defined]
    return session
