"""Unit tests for the retry/backoff decorator and classifier."""

from botocore.exceptions import ClientError

from quiet_riot.core.enumeration.retry_handler import (
    is_retryable_exception,
    retry_with_backoff,
)


def _client_error(code):
    return ClientError({"Error": {"Code": code, "Message": code}}, "Op")


def test_throttling_is_retryable():
    assert is_retryable_exception(_client_error("Throttling")) is True
    assert is_retryable_exception(_client_error("TooManyRequestsException")) is True


def test_invalid_parameter_is_not_retryable():
    assert is_retryable_exception(_client_error("InvalidParameterException")) is False
    assert is_retryable_exception(_client_error("AccessDenied")) is False


def test_retry_exhausts_then_raises(monkeypatch):
    sleeps = []
    monkeypatch.setattr(
        "quiet_riot.core.enumeration.retry_handler.time.sleep",
        lambda s: sleeps.append(s),
    )
    calls = {"n": 0}

    @retry_with_backoff(max_retries=3, base_delay=0.01)
    def always_throttled():
        calls["n"] += 1
        raise _client_error("Throttling")

    try:
        always_throttled()
        raise AssertionError("expected ClientError to propagate")
    except ClientError:
        pass

    assert calls["n"] == 4  # initial + 3 retries
    assert len(sleeps) == 3


def test_non_retryable_fails_fast(monkeypatch):
    sleeps = []
    monkeypatch.setattr(
        "quiet_riot.core.enumeration.retry_handler.time.sleep",
        lambda s: sleeps.append(s),
    )
    calls = {"n": 0}

    @retry_with_backoff(max_retries=3, base_delay=0.01)
    def invalid():
        calls["n"] += 1
        raise _client_error("InvalidParameterException")

    try:
        invalid()
        raise AssertionError("expected ClientError to propagate")
    except ClientError:
        pass

    assert calls["n"] == 1  # no retries
    assert sleeps == []


def test_success_returns_immediately():
    @retry_with_backoff(max_retries=3, base_delay=0.01)
    def ok():
        return "Pass"

    assert ok() == "Pass"
