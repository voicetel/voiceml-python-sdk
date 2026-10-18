"""Diagnostic surfaces — ``/health`` and the OpenAPI document endpoints.

These are mounted at the server root, outside ``/2010-04-01/Accounts/{AccountSid}/…``,
and the spec marks them ``security: []``. They go through the client's normal
transport — so an injected ``http_client``, the timeout, proxies and the SDK
User-Agent all apply — but without the ``Authorization`` header. A client created
without credentials (``Client()``) can call them.
"""

from __future__ import annotations

from typing import Any

from .._http import AsyncTransport, Transport
from ..exceptions import ApiError
from ..models import HealthStatus

_YAML_ACCEPT = "application/yaml, application/x-yaml, text/yaml, */*"


def _text(content: bytes, path: str) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ApiError(f"could not decode {path} as UTF-8: {exc}", status_code=200) from exc


class DiagnosticsResource:
    """Sync diagnostics. Never sends credentials."""

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def __repr__(self) -> str:
        return "<DiagnosticsResource>"

    def health(self) -> HealthStatus:
        """``GET /health``. 200 = all hard checks pass; 503 raises
        :class:`voiceml.ServerError` with the failure list on ``error.body``.
        """
        return HealthStatus.model_validate(self._t.request("GET", "/health", auth=False))

    def openapi_json(self) -> Any:
        """``GET /openapi.json`` — the OpenAPI document, parsed."""
        return self._t.request("GET", "/openapi.json", auth=False)

    def openapi_yaml(self) -> str:
        """``GET /openapi.yaml`` — the OpenAPI document as YAML text."""
        result = self._t.fetch_bytes("/openapi.yaml", accept=_YAML_ACCEPT, auth=False)
        return _text(result.content, "/openapi.yaml")

    def openapi_yml(self) -> str:
        """``GET /openapi.yml`` — alias of :meth:`openapi_yaml` served at ``.yml``."""
        result = self._t.fetch_bytes("/openapi.yml", accept=_YAML_ACCEPT, auth=False)
        return _text(result.content, "/openapi.yml")


class DiagnosticsAsyncResource:
    """Async diagnostics. Never sends credentials."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    def __repr__(self) -> str:
        return "<DiagnosticsAsyncResource>"

    async def health(self) -> HealthStatus:
        return HealthStatus.model_validate(await self._t.request("GET", "/health", auth=False))

    async def openapi_json(self) -> Any:
        return await self._t.request("GET", "/openapi.json", auth=False)

    async def openapi_yaml(self) -> str:
        result = await self._t.fetch_bytes("/openapi.yaml", accept=_YAML_ACCEPT, auth=False)
        return _text(result.content, "/openapi.yaml")

    async def openapi_yml(self) -> str:
        result = await self._t.fetch_bytes("/openapi.yml", accept=_YAML_ACCEPT, auth=False)
        return _text(result.content, "/openapi.yml")
