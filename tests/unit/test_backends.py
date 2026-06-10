"""Unit tests for the pluggable execution-backend seam (Phase 4)."""

import pytest

from quiet_riot.core import backends
from quiet_riot.core.backends import (
    DistributedBackend,
    ExecutionBackend,
    LocalThreadPoolBackend,
    get_backend,
)


def test_default_backend_is_local(monkeypatch):
    monkeypatch.delenv("QUIET_RIOT_BACKEND", raising=False)
    assert isinstance(get_backend(), LocalThreadPoolBackend)


def test_backend_selected_by_env(monkeypatch):
    monkeypatch.setenv("QUIET_RIOT_BACKEND", "distributed")
    assert isinstance(get_backend(), DistributedBackend)


def test_unknown_backend_raises():
    with pytest.raises(ValueError, match="Unknown backend"):
        get_backend("does-not-exist")


def test_both_backends_satisfy_protocol():
    assert isinstance(LocalThreadPoolBackend(), ExecutionBackend)
    assert isinstance(DistributedBackend(), ExecutionBackend)


def test_distributed_backend_is_clear_about_being_unimplemented():
    with pytest.raises(NotImplementedError, match="distributed-architecture.md"):
        DistributedBackend().run("wl.txt", session=None, threads=1)


def test_local_backend_delegates_and_reads_results(monkeypatch, tmp_path):
    results = tmp_path / "valid.txt"
    results.write_text("123456789012\n210987654321\n")

    monkeypatch.setattr(backends.loadbalancer, "getter", lambda thread, wordlist: [["a"]])
    monkeypatch.setattr(backends.loadbalancer, "threader", lambda words, session: str(results))

    out = LocalThreadPoolBackend().run("wl.txt", session=object(), threads=10)
    assert out == ["123456789012", "210987654321"]
