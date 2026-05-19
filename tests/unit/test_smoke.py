"""Smoke tests — verify the SDK imports, classes wire up, and request paths look right.

Hits no network; uses pytest-httpx to intercept httpx calls.
"""

from __future__ import annotations

import base64
import re

import pytest
from pytest_httpx import HTTPXMock

from voiceml import (
    ApiError,
    AsyncClient,
    AuthenticationError,
    Client,
    ConfigurationError,
    NotFoundError,
    NotImplementedAPIError,
    RateLimitError,
    __version__,
)
from voiceml.models import (
    Call,
    CallList,
    Conference,
    CreateCallRequest,
    CreateQueueRequest,
    EndConferenceRequest,
    Queue,
    StartStreamRequest,
    UpdateCallRequest,
    UpdateParticipantRequest,
)

ACCOUNT_SID = "AC" + "f" * 32
API_KEY = "secret-key-1234"
BASE = "https://voiceml.voicetel.com"


def test_version_is_set():
    assert __version__ == "0.4.0"


def test_client_requires_credentials():
    with pytest.raises(ConfigurationError):
        Client(account_sid="", api_key=API_KEY)
    with pytest.raises(ConfigurationError):
        Client(account_sid=ACCOUNT_SID, api_key="")


def test_resource_groups_wired_up():
    c = Client(account_sid=ACCOUNT_SID, api_key=API_KEY)
    try:
        assert c.calls is not None
        assert c.conferences is not None
        assert c.queues is not None
        assert c.applications is not None
        assert c.recordings is not None
        assert c.diagnostics is not None
        assert c.account_sid == ACCOUNT_SID
        assert c.base_url == BASE
    finally:
        c.close()


def _call_payload(sid: str = "CA" + "0" * 32) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "api_version": "2010-04-01",
        "status": "queued",
        "direction": "outbound-api",
        "date_created": "Mon, 19 May 2026 12:00:00 +0000",
        "date_updated": "Mon, 19 May 2026 12:00:00 +0000",
        "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{sid}.json",
    }


def test_calls_create_sends_form_and_basic_auth(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls",
        json=_call_payload(),
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        call = c.calls.create(
            CreateCallRequest(
                To="+18005551234", From="+18005550000", Url="https://example.com/twiml"
            )
        )
    assert call.sid.startswith("CA")
    assert call.status == "queued"

    sent = httpx_mock.get_request()
    assert sent is not None
    # Basic auth: base64(account_sid:api_key)
    expected_auth = "Basic " + base64.b64encode(f"{ACCOUNT_SID}:{API_KEY}".encode()).decode()
    assert sent.headers["Authorization"] == expected_auth
    # Form encoded
    assert sent.headers["Content-Type"].startswith("application/x-www-form-urlencoded")
    body = sent.content.decode()
    assert "To=%2B18005551234" in body
    assert "From=%2B18005550000" in body
    assert "Url=https%3A%2F%2Fexample.com%2Ftwiml" in body


def test_calls_list_sends_twilio_shape_filter_params(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Calls(\?.*)?$"),
        json={
            "calls": [_call_payload()],
            "page": 0,
            "page_size": 50,
            "total": 1,
            "next_page_uri": None,
            "uri": "/Calls",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        result = c.calls.list(
            status="completed",
            start_time_gte="2026-01-01",
            start_time_lte="2026-12-31",
            page_size=10,
        )
    assert isinstance(result, CallList)
    assert len(result.calls) == 1

    sent = httpx_mock.get_request()
    assert sent is not None
    query = sent.url.query.decode()
    # Twilio uses literal `StartTime>=` / `StartTime<=` query names — they should round-trip.
    assert "Status=completed" in query
    assert "StartTime%3E%3D=2026-01-01" in query
    assert "StartTime%3C%3D=2026-12-31" in query
    assert "PageSize=10" in query


def test_calls_update_terminate(httpx_mock: HTTPXMock):
    call_sid = "CA" + "1" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}",
        json={**_call_payload(call_sid), "status": "completed"},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        result = c.calls.update(call_sid, UpdateCallRequest(Status="completed"))
    assert isinstance(result, Call)
    assert result.status == "completed"


def test_conference_end_default_status(httpx_mock: HTTPXMock):
    cf_sid = "CF" + "2" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Conferences/{cf_sid}",
        json={
            "sid": cf_sid,
            "account_sid": ACCOUNT_SID,
            "friendly_name": "x",
            "status": "completed",
            "api_version": "2010-04-01",
            "uri": "/x",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        result = c.conferences.end(cf_sid)
    assert isinstance(result, Conference)
    assert result.status == "completed"
    sent = httpx_mock.get_request()
    assert b"Status=completed" in sent.content


def test_queue_create(httpx_mock: HTTPXMock):
    qu_sid = "QU" + "3" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Queues",
        json={
            "sid": qu_sid,
            "account_sid": ACCOUNT_SID,
            "friendly_name": "support",
            "current_size": 0,
            "max_size": 100,
            "average_wait_time": 0,
            "date_created": "x",
            "date_updated": "x",
            "uri": "/x",
        },
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        q = c.queues.create(CreateQueueRequest(FriendlyName="support", MaxSize=200))
    assert isinstance(q, Queue)
    sent = httpx_mock.get_request()
    body = sent.content.decode()
    assert "FriendlyName=support" in body
    assert "MaxSize=200" in body


def test_stream_start_sends_boolean_as_string(httpx_mock: HTTPXMock):
    # No bool in StartStreamRequest, but use UpdateParticipantRequest to verify bool encoding.
    httpx_mock.add_response(
        method="POST",
        url=re.compile(r".*/Participants/CA.+"),
        json={
            "call_sid": "CA" + "4" * 32,
            "conference_sid": "CF" + "5" * 32,
            "account_sid": ACCOUNT_SID,
            "muted": True,
            "hold": False,
            "start_conference_on_enter": True,
            "end_conference_on_exit": False,
            "status": "connected",
            "api_version": "2010-04-01",
            "uri": "/x",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.conferences.update_participant(
            "CF" + "5" * 32,
            "CA" + "4" * 32,
            UpdateParticipantRequest(Muted=True, Hold=False),
        )
    sent = httpx_mock.get_request()
    body = sent.content.decode()
    assert "Muted=true" in body
    assert "Hold=false" in body


def test_stream_start_form_body(httpx_mock: HTTPXMock):
    call_sid = "CA" + "6" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}/Streams",
        json={
            "sid": "MZ" + "7" * 32,
            "account_sid": ACCOUNT_SID,
            "call_sid": call_sid,
            "status": "in-progress",
            "api_version": "2010-04-01",
            "uri": "/x",
        },
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.calls.start_stream(
            call_sid,
            StartStreamRequest(Url="wss://example.com/ws", Track="both_tracks", Name="ws-1"),
        )
    sent = httpx_mock.get_request()
    body = sent.content.decode()
    assert "Url=wss%3A%2F%2Fexample.com%2Fws" in body
    assert "Track=both_tracks" in body
    assert "Name=ws-1" in body


def test_401_raises_authentication_error(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/CA" + "8" * 32,
        json={"code": 20003, "message": "Authentication Error", "status": 401},
        status_code=401,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        with pytest.raises(AuthenticationError) as exc:
            c.calls.get("CA" + "8" * 32)
    assert exc.value.status_code == 401
    assert exc.value.code == 20003


def test_404_raises_not_found(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/CA" + "9" * 32,
        json={"code": 20404, "message": "Not Found", "status": 404},
        status_code=404,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        with pytest.raises(NotFoundError):
            c.calls.get("CA" + "9" * 32)


def test_429_raises_rate_limit(httpx_mock: HTTPXMock):
    sid = "CA" + "a" * 32
    # max_retries=0 so we don't retry the 429 — we just want to see the exception.
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{sid}",
        json={"code": 20429, "message": "Too Many Requests", "status": 429},
        status_code=429,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY, max_retries=0) as c:
        with pytest.raises(RateLimitError):
            c.calls.get(sid)


def test_501_user_defined_messages(httpx_mock: HTTPXMock):
    sid = "CA" + "b" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{sid}/UserDefinedMessages",
        json={"code": 20501, "message": "Not Implemented", "status": 501},
        status_code=501,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        with pytest.raises(NotImplementedAPIError):
            c.calls.send_user_defined_message(sid, {"hello": "world"})


def test_api_error_base_catches_all(httpx_mock: HTTPXMock):
    sid = "CA" + "c" * 32
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Queues/{sid}",
        json={"code": 20409, "message": "Queue still has waiting members", "status": 409},
        status_code=409,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        with pytest.raises(ApiError) as exc:
            c.queues.delete(sid)
    assert exc.value.status_code == 409


async def test_async_client_works(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Calls(\?.*)?$"),
        json={
            "calls": [_call_payload()],
            "page": 0,
            "page_size": 50,
            "total": 1,
            "next_page_uri": None,
            "uri": "/x",
        },
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        result = await c.calls.list()
    assert len(result.calls) == 1
