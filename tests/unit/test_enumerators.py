"""Unit tests for the low-level AWS principal enumerators.

These are the regression tests for the ``app_app_config`` NameError bug that
silently disabled the ECR-Public (~75% of load) and S3-ACL (root-email) paths.
Each enumerator is exercised with a fake session so no real AWS is required.
"""

import importlib
import importlib.util

import pytest

from quiet_riot.core.enumeration import (
    ecrprivenum,
    ecrpubenum,
    s3aclenum,
    snsenum,
)
from tests.helpers import configure_scan, fail_client, make_fake_session, pass_client

# (module, checker_attr, client_service, client_method)
ENUMERATORS = [
    (ecrpubenum, "ecr_princ_checker", "ecr-public", "set_repository_policy"),
    (ecrprivenum, "ecr_princ_checker", "ecr", "put_registry_policy"),
    (snsenum, "sns_princ_checker", "sns", "set_topic_attributes"),
]


@pytest.mark.parametrize("module, attr, service, method", ENUMERATORS)
def test_valid_principal_returns_pass(module, attr, service, method):
    configure_scan()
    session = make_fake_session(pass_client(service, method))
    checker = getattr(module, attr)
    assert checker("211125621822", session) == "Pass"


@pytest.mark.parametrize("module, attr, service, method", ENUMERATORS)
def test_invalid_principal_returns_fail(module, attr, service, method):
    configure_scan()
    session = make_fake_session(fail_client(service, method))
    checker = getattr(module, attr)
    assert checker("000000000000", session) == "Fail"


def test_s3acl_valid_email_returns_pass():
    configure_scan()
    session = make_fake_session(pass_client("s3", "put_bucket_acl"))
    assert s3aclenum.s3_acl_princ_checker("root@example.com", session) == "Pass"


def test_s3acl_invalid_email_returns_fail():
    configure_scan()
    session = make_fake_session(fail_client("s3", "put_bucket_acl", code="UnsupportedArgument"))
    assert s3aclenum.s3_acl_princ_checker("nope@example.com", session) == "Fail"


@pytest.mark.parametrize(
    "module_name",
    [
        "quiet_riot.core.enumeration.ecrpubenum",
        "quiet_riot.core.enumeration.ecrprivenum",
        "quiet_riot.core.enumeration.snsenum",
        "quiet_riot.core.enumeration.s3aclenum",
    ],
)
def test_no_undefined_app_app_config_regression(module_name):
    """Guard against the double-substitution typo reappearing.

    Modules that reference config must expose the ``app_config`` alias and must
    NOT contain the string ``app_app_config`` in their source.
    """
    module = importlib.import_module(module_name)
    origin = importlib.util.find_spec(module_name).origin
    with open(origin) as f:
        text = f.read()
    if ".get_config()" in text:
        assert hasattr(module, "app_config"), f"{module_name} missing app_config import"
    assert "app_app_config" not in text, f"{module_name} still references undefined app_app_config"
