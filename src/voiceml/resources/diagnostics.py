"""Diagnostic surfaces — ``/health`` and the OpenAPI doc endpoints.

These don't sit under ``/2010-04-01/Accounts/{AccountSid}/…``; they're mounted at the server
root and don't require auth (the spec marks them ``security: []``).
"""

from __future__ import annotations

from typing import Any

import httpx

from .._http import AsyncTransport, Transport
from ..models import HealthStatus


class DiagnosticsResource:
    """Sync diagnostics. Does NOT auth — the spec marks ``/health`` + spec endpoints as open."""

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def health(self) -> HealthStatus:
        """Hit ``/health``. 200 = all hard checks pass; 503 raises :class:`voiceml.ServerError`
        with the failure list on ``error.body``.
        """
        return HealthStatus.model_validate(self._unauth_request("GET", "/health"))

    def openapi_json(self) -> Any:
        """Fetch the OpenAPI spec as parsed JSON."""
        return self._unauth_request("GET", "/openapi.json")

    def _unauth_request(self, method: str, path: str) -> Any:
        with httpx.Client(base_url=self._t.base_url, timeout=10.0) as h:
            r = h.request(method, path, headers={"Accept": "application/json"})
            r.raise_for_status()
            return r.json()


class DiagnosticsAsyncResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def health(self) -> HealthStatus:
        return HealthStatus.model_validate(await self._unauth_request("GET", "/health"))

    async def openapi_json(self) -> Any:
        return await self._unauth_request("GET", "/openapi.json")

    async def _unauth_request(self, method: str, path: str) -> Any:
        async with httpx.AsyncClient(base_url=self._t.base_url, timeout=10.0) as h:
            r = await h.request(method, path, headers={"Accept": "application/json"})
            r.raise_for_status()
            return r.json()
