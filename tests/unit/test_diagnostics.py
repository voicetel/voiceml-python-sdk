"""Diagnostics go through the normal transport, without credentials."""

from __future__ import annotations

import httpx
import pytest

from voiceml import AsyncClient, Client, ConfigurationError, ServerError


class Server:
    def __init__(self, response: httpx.Response) -> None:
        self.response = response
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.response


def test_health_works_without_credentials_and_sends_no_auth() -> None:
    server = Server(httpx.Response(200, json={"ok": True}))
    with Client(http_client=httpx.Client(transport=httpx.MockTransport(server))) as c:
        health = c.diagnostics.health()
    assert health.ok is True
    assert health.warnings == [] and health.failures == []
    sent = server.requests[0]
    assert str(sent.url) == "https://voiceml.voicetel.com/health"
    assert "authorization" not in sent.headers
    assert sent.headers["user-agent"].startswith("voiceml-python/")


def test_health_never_sends_credentials_even_when_configured() -> None:
    server = Server(httpx.Response(200, json={"ok": True, "warnings": None}))
    with Client(
        account_sid="AC" + "1" * 32,
        api_key="secret",
        base_url="https://pbx.example.com",
        http_client=httpx.Client(transport=httpx.MockTransport(server)),
    ) as c:
        c.diagnostics.health()
        c.diagnostics.openapi_json()
    assert [str(r.url) for r in server.requests] == [
        "https://pbx.example.com/health",
        "https://pbx.example.com/openapi.json",
    ]
    assert all("authorization" not in r.headers for r in server.requests)


def test_health_503_raises_server_error_with_failures() -> None:
    body = {"ok": False, "failures": [{"check": "db", "detail": "down"}]}
    server = Server(httpx.Response(503, json=body))
    with (
        Client(http_client=httpx.Client(transport=httpx.MockTransport(server)), max_retries=0) as c,
        pytest.raises(ServerError) as info,
    ):
        c.diagnostics.health()
    assert info.value.body == body


def test_openapi_yaml_and_yml_return_text() -> None:
    server = Server(httpx.Response(200, text="openapi: 3.1.0\n"))
    with Client(http_client=httpx.Client(transport=httpx.MockTransport(server))) as c:
        assert c.diagnostics.openapi_yaml() == "openapi: 3.1.0\n"
        assert c.diagnostics.openapi_yml() == "openapi: 3.1.0\n"
    assert [r.url.path for r in server.requests] == ["/openapi.yaml", "/openapi.yml"]
    assert all("authorization" not in r.headers for r in server.requests)


def test_credential_less_client_refuses_authenticated_calls() -> None:
    server = Server(httpx.Response(200, json={}))
    with Client(http_client=httpx.Client(transport=httpx.MockTransport(server))) as c:
        with pytest.raises(ConfigurationError, match="diagnostics"):
            c.calls.list()
        with pytest.raises(ConfigurationError):
            c.messaging_v1.services.list()
    assert server.requests == []


async def test_async_health_without_credentials() -> None:
    server = Server(
        httpx.Response(200, text='{"ok":true}', headers={"content-type": "application/json"})
    )
    async with AsyncClient(
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(server))
    ) as c:
        assert (await c.diagnostics.health()).ok is True
        assert await c.diagnostics.openapi_yaml() == '{"ok":true}'
    assert all("authorization" not in r.headers for r in server.requests)
