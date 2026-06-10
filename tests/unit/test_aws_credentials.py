"""Unit tests for AWS credentials / ARN handling."""

import pytest

from quiet_riot.aws_credentials import ARNParseError, AWSCredentialsManager


@pytest.fixture
def mgr():
    return AWSCredentialsManager()


def test_parse_role_arn(mgr):
    info = mgr.parse_arn("arn:aws:iam::123456789012:role/MyRole")
    assert info["partition"] == "aws"
    assert info["service"] == "iam"
    assert info["account_id"] == "123456789012"
    assert info["resource_type"] == "role"
    assert info["resource_name"] == "MyRole"


def test_parse_nested_role_path(mgr):
    info = mgr.parse_arn("arn:aws:iam::123456789012:role/path/to/MyRole")
    assert info["resource_type"] == "role"
    assert info["resource_name"] == "path/to/MyRole"


def test_parse_invalid_arn_raises(mgr):
    with pytest.raises(ARNParseError):
        mgr.parse_arn("not-an-arn")


def test_is_arn_true_false(mgr):
    assert mgr.is_arn("arn:aws:iam::123456789012:role/MyRole") is True
    assert mgr.is_arn("my-profile") is False


def test_validate_session_with_moto(mgr, moto_session):
    is_valid, arn = mgr.validate_session(moto_session)
    assert is_valid is True
    assert arn is not None
