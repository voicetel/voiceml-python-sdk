"""Test-suite guard rails.

No test may reach the network: every HTTP exchange goes through ``pytest-httpx`` or an
``httpx.MockTransport``. Opening a socket or resolving a host name fails the test
immediately, so a code path that bypasses the transport (as diagnostics once did)
cannot silently call a real server.
"""

from __future__ import annotations

import socket
from typing import Any

import pytest


class NetworkAccessError(AssertionError):
    pass


def _refuse(*args: Any, **kwargs: Any) -> Any:
    raise NetworkAccessError(f"tests must not touch the network: {args!r}")


@pytest.fixture(autouse=True)
def _no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(socket.socket, "connect", _refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", _refuse)
    monkeypatch.setattr(socket, "getaddrinfo", _refuse)
    monkeypatch.setattr(socket, "create_connection", _refuse)
