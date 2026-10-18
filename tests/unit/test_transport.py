"""Transport behaviour: retry policy, Retry-After, error mapping, URL building."""

from __future__ import annotations

import asyncio
import email.utils
from collections.abc import Callable

import httpx
import pytest

import voiceml._http as http_mod
from voiceml import (
    APIConnectionError,
    ApiError,
    APITimeoutError,
    AsyncClient,
    AuthenticationError,
    Client,
    ConfigurationError,
    ConflictError,
    RateLimitError,
    ServerError,
)
from voiceml.models import Call, CreateCallRequest

ACCOUNT_SID = "AC" + "a" * 32
API_KEY = "transport-test-key"
CALLS = f"/2010-04-01/Accounts/{ACCOUNT_SID}/Calls.json"

CALL_JSON = {
    "sid": "CA" + "1" * 32,
    "account_sid": ACCOUNT_SID,
    "status": "queued",
    "direction": "outbound-api",
}


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record backoff sleeps instead of sleeping; make jitter return its upper bound."""
    recorded: list[float] = []
    monkeypatch.setattr(http_mod, "_sleep", recorded.append)

    async def fake_async_sleep(delay: float) -> None:
        recorded.append(delay)

    monkeypatch.setattr(http_mod, "_async_sleep", fake_async_sleep)
    monkeypatch.setattr(http_mod, "_jitter", lambda low, high: high)
    return recorded


def make_client(
    handler: Callable[[httpx.Request], httpx.Response], *, max_retries: int = 2
) -> tuple[Client, list[httpx.Request]]:
    seen: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return handler(request)

    client = Client(
        account_sid=ACCOUNT_SID,
        api_key=API_KEY,
        http_client=httpx.Client(transport=httpx.MockTransport(record)),
        max_retries=max_retries,
    )
    return client, seen


def scripted(*steps: httpx.Response | Exception) -> Callable[[httpx.Request], httpx.Response]:
    queue = list(steps)

    def handler(request: httpx.Request) -> httpx.Response:
        step = queue.pop(0)
        if isinstance(step, Exception):
            raise step
        return step

    return handler


def create_call(client: Client) -> Call:
    return client.calls.create(
        CreateCallRequest(to="+14155550100", from_="+14155550101", url="https://example.com/a")
    )


# --- POST / PATCH are never replayed after the request may have been received ---


@pytest.mark.parametrize("status", [500, 502, 503, 504])
def test_post_is_not_retried_on_5xx(status: int, sleeps: list[float]) -> None:
    client, seen = make_client(scripted(httpx.Response(status, json={"message": "boom"})))
    with pytest.raises(ServerError):
        create_call(client)
    assert len(seen) == 1
    assert sleeps == []


@pytest.mark.parametrize(
    "exc",
    [
        httpx.ReadTimeout("read timed out"),
        httpx.WriteTimeout("write timed out"),
        httpx.ReadError("connection reset by peer"),
        httpx.RemoteProtocolError("server disconnected without sending a response"),
    ],
)
def test_post_is_not_retried_after_send_failures(exc: Exception, sleeps: list[float]) -> None:
    client, seen = make_client(scripted(exc))
    with pytest.raises(APIConnectionError) as info:
        create_call(client)
    assert len(seen) == 1
    assert sleeps == []
    assert info.value.__cause__ is exc
    assert info.value.status_code == 0


def test_post_is_retried_on_429(sleeps: list[float]) -> None:
    client, seen = make_client(
        scripted(
            httpx.Response(429, json={"message": "slow down"}),
            httpx.Response(201, json=CALL_JSON),
        )
    )
    call = create_call(client)
    assert call.sid == CALL_JSON["sid"]
    assert len(seen) == 2
    assert seen[0].content == seen[1].content
    assert sleeps == [0.5]


@pytest.mark.parametrize(
    "exc",
    [
        httpx.ConnectError("[Errno 111] Connection refused"),
        httpx.ConnectTimeout("connect timed out"),
    ],
)
def test_post_is_retried_when_connection_was_never_established(
    exc: Exception, sleeps: list[float]
) -> None:
    client, seen = make_client(scripted(exc, httpx.Response(201, json=CALL_JSON)))
    create_call(client)
    assert len(seen) == 2
    assert sleeps == [0.5]


def test_patch_follows_the_post_policy(sleeps: list[float]) -> None:
    transport = http_mod.Transport(
        account_sid=ACCOUNT_SID,
        api_key=API_KEY,
        http_client=httpx.Client(transport=httpx.MockTransport(scripted(httpx.Response(503)))),
    )
    with pytest.raises(ServerError):
        transport.request("PATCH", "/x")
    assert sleeps == []


# --- idempotent methods are retried ---


@pytest.mark.parametrize("status", [429, 500, 502, 503, 504])
def test_get_is_retried_on_retryable_status(status: int, sleeps: list[float]) -> None:
    client, seen = make_client(
        scripted(httpx.Response(status), httpx.Response(200, json=CALL_JSON))
    )
    client.calls.get(CALL_JSON["sid"])
    assert len(seen) == 2
    assert sleeps == [0.5]


@pytest.mark.parametrize(
    "exc",
    [httpx.ReadTimeout("read timed out"), httpx.ReadError("reset"), httpx.ConnectError("x")],
)
def test_get_is_retried_on_transport_errors(exc: Exception, sleeps: list[float]) -> None:
    client, seen = make_client(scripted(exc, httpx.Response(200, json=CALL_JSON)))
    client.calls.get(CALL_JSON["sid"])
    assert len(seen) == 2


def test_delete_is_retried_and_gives_up_after_max_retries(sleeps: list[float]) -> None:
    client, seen = make_client(
        scripted(httpx.Response(503), httpx.Response(503), httpx.Response(503))
    )
    with pytest.raises(ServerError):
        client.calls.delete(CALL_JSON["sid"])
    assert len(seen) == 3  # 1 + max_retries (2)
    assert sleeps == [0.5, 1.0]


def test_backoff_is_exponential_with_full_jitter_and_capped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bounds: list[tuple[float, float]] = []

    def fake_jitter(low: float, high: float) -> float:
        bounds.append((low, high))
        return 0.0

    monkeypatch.setattr(http_mod, "_jitter", fake_jitter)
    for attempt in range(7):
        http_mod.backoff_delay(attempt)
    assert bounds == [
        (0.0, 0.5),
        (0.0, 1.0),
        (0.0, 2.0),
        (0.0, 4.0),
        (0.0, 8.0),
        (0.0, 8.0),
        (0.0, 8.0),
    ]


def test_max_retries_zero_disables_retries(sleeps: list[float]) -> None:
    client, seen = make_client(scripted(httpx.Response(503)), max_retries=0)
    with pytest.raises(ServerError):
        client.calls.get(CALL_JSON["sid"])
    assert len(seen) == 1


# --- Retry-After ---


def test_retry_after_seconds_is_honoured(sleeps: list[float]) -> None:
    client, _ = make_client(
        scripted(
            httpx.Response(429, headers={"Retry-After": "3"}),
            httpx.Response(200, json=CALL_JSON),
        )
    )
    client.calls.get(CALL_JSON["sid"])
    assert sleeps == [3.0]


def test_retry_after_http_date_is_honoured(
    sleeps: list[float], monkeypatch: pytest.MonkeyPatch
) -> None:
    now = 1_800_000_000.0
    monkeypatch.setattr(http_mod, "_now", lambda: now)
    when = email.utils.formatdate(now + 7, usegmt=True)
    client, _ = make_client(
        scripted(
            httpx.Response(503, headers={"Retry-After": when}),
            httpx.Response(200, json=CALL_JSON),
        )
    )
    client.calls.get(CALL_JSON["sid"])
    assert sleeps == [pytest.approx(7.0)]


def test_retry_after_in_the_past_retries_immediately(
    sleeps: list[float], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(http_mod, "_now", lambda: 1_800_000_000.0)
    past = email.utils.formatdate(1_700_000_000.0, usegmt=True)
    client, _ = make_client(
        scripted(
            httpx.Response(429, headers={"Retry-After": past}),
            httpx.Response(200, json=CALL_JSON),
        )
    )
    client.calls.get(CALL_JSON["sid"])
    assert sleeps == [0.0]


def test_retry_after_above_cap_raises_immediately(sleeps: list[float]) -> None:
    client, seen = make_client(
        scripted(httpx.Response(429, headers={"Retry-After": "3600"}, json={"code": 20429}))
    )
    with pytest.raises(RateLimitError) as info:
        client.calls.get(CALL_JSON["sid"])
    assert len(seen) == 1
    assert sleeps == []
    assert info.value.retry_after == 3600.0
    assert info.value.code == 20429


def test_retry_after_is_exposed_once_retries_are_exhausted(sleeps: list[float]) -> None:
    client, seen = make_client(
        scripted(*[httpx.Response(429, headers={"Retry-After": "1"}) for _ in range(3)])
    )
    with pytest.raises(RateLimitError) as info:
        client.calls.get(CALL_JSON["sid"])
    assert len(seen) == 3
    assert info.value.retry_after == 1.0


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0", 0.0),
        ("2.5", 2.5),
        ("-4", 0.0),
        ("soon", None),
        ("", None),
        (None, None),
        ("nan", None),
    ],
)
def test_parse_retry_after(value: str | None, expected: float | None) -> None:
    assert http_mod.parse_retry_after(value) == expected


# --- async behaviour + cancellation ---


async def test_async_post_is_not_retried_on_5xx(sleeps: list[float]) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(502)

    async with AsyncClient(
        account_sid=ACCOUNT_SID,
        api_key=API_KEY,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    ) as client:
        with pytest.raises(ServerError):
            await client.messages.create(to="+14155550100", body="hi")
    assert len(seen) == 1


async def test_async_get_retries_429(sleeps: list[float]) -> None:
    async with AsyncClient(
        account_sid=ACCOUNT_SID,
        api_key=API_KEY,
        http_client=httpx.AsyncClient(
            transport=httpx.MockTransport(
                scripted(
                    httpx.Response(429, headers={"Retry-After": "2"}),
                    httpx.Response(200, json=CALL_JSON),
                )
            )
        ),
    ) as client:
        await client.calls.get(CALL_JSON["sid"])
    assert sleeps == [2.0]


async def test_async_cancellation_propagates_and_is_not_retried() -> None:
    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        await asyncio.sleep(3600)
        return httpx.Response(200, json=CALL_JSON)

    async with AsyncClient(
        account_sid=ACCOUNT_SID,
        api_key=API_KEY,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    ) as client:
        task = asyncio.create_task(client.calls.get(CALL_JSON["sid"]))
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert attempts == 1


# --- error mapping ---


def test_timeout_surfaces_as_sdk_timeout_error_with_cause(sleeps: list[float]) -> None:
    exc = httpx.ReadTimeout("read timed out")
    client, _ = make_client(scripted(exc, exc, exc))
    with pytest.raises(APITimeoutError) as info:
        client.calls.get(CALL_JSON["sid"])
    assert isinstance(info.value, APIConnectionError)
    assert isinstance(info.value, ApiError)
    assert info.value.__cause__ is exc
    assert "after 3 attempts" in str(info.value)


def test_non_json_error_body_still_raises_typed_error() -> None:
    client, _ = make_client(
        scripted(
            httpx.Response(401, text="<html>nope</html>", headers={"content-type": "text/html"})
        )
    )
    with pytest.raises(AuthenticationError) as info:
        client.calls.get(CALL_JSON["sid"])
    assert info.value.body == "<html>nope</html>"
    assert info.value.code is None
    assert info.value.message.startswith("HTTP 401")


def test_error_envelope_is_parsed() -> None:
    client, _ = make_client(
        scripted(
            httpx.Response(
                409,
                json={
                    "code": 20409,
                    "message": "modified concurrently",
                    "more_info": "https://www.twilio.com/docs/errors/20409",
                    "status": 409,
                },
            )
        )
    )
    with pytest.raises(ConflictError) as info:
        client.accounts.update(friendly_name="x")
    err = info.value
    assert (err.status_code, err.code, err.message) == (409, 20409, "modified concurrently")
    assert err.more_info == "https://www.twilio.com/docs/errors/20409"
    assert str(err) == "modified concurrently"


def test_success_body_that_is_not_json_says_could_not_decode() -> None:
    client, _ = make_client(
        scripted(httpx.Response(200, text="<Response/>", headers={"content-type": "text/xml"}))
    )
    with pytest.raises(ApiError) as info:
        client.calls.get(CALL_JSON["sid"])
    assert "could not decode" in str(info.value)
    assert "text/xml" in str(info.value)
    assert isinstance(info.value.__cause__, ValueError)


def test_string_error_code_is_normalised_to_int() -> None:
    client, _ = make_client(scripted(httpx.Response(400, json={"code": "21211", "message": "bad"})))
    with pytest.raises(ApiError) as info:
        client.calls.get(CALL_JSON["sid"])
    assert info.value.code == 21211


# --- URL building / configuration ---


def test_injected_http_client_base_url_never_overrides_configured_base_url() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"queues": [], "page": 0, "page_size": 50})

    injected = httpx.Client(
        base_url="https://voiceml.voicetel.com", transport=httpx.MockTransport(handler)
    )
    with Client(
        account_sid=ACCOUNT_SID,
        api_key=API_KEY,
        base_url="https://staging.example.com",
        http_client=injected,
    ) as client:
        client.queues.list()
        client.messaging_v1.services.list()
    assert [str(r.url).split("?")[0] for r in seen] == [
        f"https://staging.example.com/2010-04-01/Accounts/{ACCOUNT_SID}/Queues.json",
        "https://staging.example.com/v1/Services",
    ]
    assert client.base_url == "https://staging.example.com"


def test_user_agent_and_accept_headers() -> None:
    client, seen = make_client(scripted(httpx.Response(200, json=CALL_JSON)))
    client.calls.get(CALL_JSON["sid"])
    assert seen[0].headers["user-agent"].startswith("voiceml-python/")
    assert seen[0].headers["accept"] == "application/json"


@pytest.mark.parametrize("bad", ["voiceml.voicetel.com", "ftp://x.example.com", "https://"])
def test_invalid_base_url_is_a_configuration_error(bad: str) -> None:
    with pytest.raises(ConfigurationError):
        Client(account_sid=ACCOUNT_SID, api_key=API_KEY, base_url=bad)


def test_negative_max_retries_is_a_configuration_error() -> None:
    with pytest.raises(ConfigurationError):
        Client(account_sid=ACCOUNT_SID, api_key=API_KEY, max_retries=-1)


def test_account_sid_without_key_is_a_configuration_error() -> None:
    with pytest.raises(ConfigurationError):
        Client(account_sid=ACCOUNT_SID)
    with pytest.raises(ConfigurationError):
        Client(api_key=API_KEY)
