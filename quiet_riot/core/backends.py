"""Pluggable execution backends for principal validation.

See ``docs/distributed-architecture.md``. Both backends consume the same
wordlist and return the same ``list[str]`` of validated principals, so the CLI,
API, and library work unchanged regardless of which backend runs the scan.
"""

import logging
import os
from typing import Protocol, runtime_checkable

from .enumeration import loadbalancer

logger = logging.getLogger(__name__)


@runtime_checkable
class ExecutionBackend(Protocol):
    """Validates the principals in a wordlist and returns the ones that exist."""

    name: str

    def run(self, wordlist_path: str, session, threads: int) -> list[str]: ...


class LocalThreadPoolBackend:
    """Single-account, multi-threaded validation (the default backend).

    Wraps the existing load-balanced thread-pool checker. Throughput is bounded
    by one account's AWS API throttling budget (~1,100 checks/sec).
    """

    name = "local"

    def run(self, wordlist_path: str, session, threads: int) -> list[str]:
        results_file = loadbalancer.threader(
            loadbalancer.getter(thread=threads, wordlist=wordlist_path),
            session=session,
        )
        valid: list[str] = []
        if results_file and os.path.exists(results_file):
            with open(results_file) as f:
                valid = [line.strip() for line in f if line.strip()]
        return valid


class DistributedBackend:
    """Multi-account fan-out over SQS to per-account Lambda workers.

    Not yet implemented — see ``docs/distributed-architecture.md`` for the
    design and build sequence. Scales past the single-account ceiling by giving
    each worker account its own throttling budget.
    """

    name = "distributed"

    def run(self, wordlist_path: str, session, threads: int) -> list[str]:
        raise NotImplementedError(
            "The distributed multi-account backend is not implemented yet. "
            "See docs/distributed-architecture.md. Use QUIET_RIOT_BACKEND=local "
            "(the default) for single-account scans."
        )


_BACKENDS: dict[str, type[ExecutionBackend]] = {
    LocalThreadPoolBackend.name: LocalThreadPoolBackend,
    DistributedBackend.name: DistributedBackend,
}


def get_backend(name: str | None = None) -> ExecutionBackend:
    """Return the configured backend (env ``QUIET_RIOT_BACKEND``, default ``local``)."""
    resolved = (name or os.getenv("QUIET_RIOT_BACKEND") or "local").lower()
    backend_cls = _BACKENDS.get(resolved)
    if backend_cls is None:
        raise ValueError(f"Unknown backend '{resolved}'. Available: {sorted(_BACKENDS)}")
    return backend_cls()
