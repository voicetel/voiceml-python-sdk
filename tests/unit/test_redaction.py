"""Secrets never appear in default string / repr / serialisation output."""

from __future__ import annotations

import httpx
import pytest

from voiceml import AsyncClient, AuthenticationError, Client, RequestValidator
from voiceml._http import AsyncTransport, Transport
from voiceml.models import UpdateAccountRequest

ACCOUNT_SID = "AC" + "d" * 32
SECRET = "sk-super-secret-api-key-value"


def _objects(client: Client) -> list[object]:
    return [
        client,
        client._transport,
        client.calls,
        client.messaging_v1.services,
        client.conversations_v1.conversations("CH1"),
        client.sip.domains,
        client.diagnostics,
        client.accounts,
    ]


def test_client_transport_and_resources_hide_the_api_key() -> None:
    with Client(account_sid=ACCOUNT_SID, api_key=SECRET) as client:
        for obj in _objects(client):
            assert SECRET not in repr(obj), type(obj).__name__
            assert SECRET not in str(obj), type(obj).__name__
        assert ACCOUNT_SID in repr(client)


def test_auth_token_alias_is_hidden_too() -> None:
    with Client(account_sid=ACCOUNT_SID, auth_token=SECRET) as client:
        assert SECRET not in repr(client)


async def test_async_client_hides_the_api_key() -> None:
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=SECRET) as client:
        assert SECRET not in repr(client)
        assert SECRET not in repr(client._transport)
        assert SECRET not in repr(client.calls)


def test_transports_hide_the_api_key() -> None:
    assert SECRET not in repr(Transport(account_sid=ACCOUNT_SID, api_key=SECRET))
    assert SECRET not in repr(AsyncTransport(account_sid=ACCOUNT_SID, api_key=SECRET))


def test_api_errors_do_not_echo_credentials() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"code": 20003, "message": "Authenticate", "status": 401})

    with Client(
        account_sid=ACCOUNT_SID,
        api_key=SECRET,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    ) as client:
        with pytest.raises(AuthenticationError) as info:
            client.calls.list()
    err = info.value
    for text in (str(err), repr(err), repr(err.body)):
        assert SECRET not in text


def test_account_update_secrets_are_hidden_from_repr() -> None:
    req = UpdateAccountRequest(
        aws_secret_access_key=SECRET, tts_http_token=SECRET, stt_http_token=SECRET
    )
    assert SECRET not in repr(req)
    assert SECRET not in str(req)
    # They are still sent on the wire.
    assert req.to_form()["AwsSecretAccessKey"] == SECRET


def test_request_validator_hides_the_api_key() -> None:
    assert SECRET not in repr(RequestValidator(SECRET))
