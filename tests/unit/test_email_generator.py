"""Unit tests for the API email-generator endpoint logic.

Importing the server module also smoke-tests that the FastAPI app builds.
"""

import asyncio

from quiet_riot.api import server


def test_generate_emails_combination_pattern():
    res = asyncio.run(server.generate_emails(domain="ExAmple.com", pattern="firstname.lastname", max_emails=5))
    assert res["count"] == 5
    assert res["domain"] == "example.com"
    assert all(e.endswith("@example.com") for e in res["emails"])
    assert all("." in e.split("@")[0] for e in res["emails"])


def test_generate_emails_respects_max():
    res = asyncio.run(server.generate_emails(domain="x.com", pattern="firstnamelastname", max_emails=12))
    assert res["count"] == 12
    assert len(res["emails"]) == 12


def test_generate_emails_single_name_pattern():
    res = asyncio.run(server.generate_emails(domain="x.com", pattern="firstname", max_emails=10))
    assert res["count"] == 10
    assert all("@x.com" in e for e in res["emails"])
