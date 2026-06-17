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
    CreateParticipantRequest,
    CreateQueueRequest,
    IncomingPhoneNumber,
    IncomingPhoneNumberList,
    Participant,
    Queue,
    Recording,
    StartStreamRequest,
    UpdateCallRequest,
    UpdateParticipantRequest,
)

ACCOUNT_SID = "AC" + "f" * 32
API_KEY = "secret-key-1234"
BASE = "https://voiceml.voicetel.com"


def test_version_is_set():
    assert __version__ == "0.8.1"


def test_client_requires_credentials():
    with pytest.raises(ConfigurationError):
        Client(account_sid="", api_key=API_KEY)
    with pytest.raises(ConfigurationError):
        Client(account_sid=ACCOUNT_SID, api_key="")
    # auth_token=... is accepted as an alias for api_key=...; passing both is an error.
    with pytest.raises(ConfigurationError):
        Client(account_sid=ACCOUNT_SID, api_key=API_KEY, auth_token=API_KEY)
    # Neither api_key nor auth_token → ConfigurationError.
    with pytest.raises(ConfigurationError):
        Client(account_sid=ACCOUNT_SID)


def test_auth_token_alias_works_like_api_key(httpx_mock: HTTPXMock):
    """``auth_token=`` (Twilio name) and ``api_key=`` (VoiceML name) wire to the same Basic auth."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Calls\.json(\?.*)?$"),
        json={
            "calls": [_call_payload()],
            "page": 0,
            "page_size": 50,
            "total": 1,
            "next_page_uri": None,
            "uri": "/x",
        },
    )
    with Client(account_sid=ACCOUNT_SID, auth_token=API_KEY) as c:
        c.calls.list()
    sent = httpx_mock.get_request()
    assert sent is not None
    expected_auth = "Basic " + base64.b64encode(f"{ACCOUNT_SID}:{API_KEY}".encode()).decode()
    assert sent.headers["Authorization"] == expected_auth


def test_resource_groups_wired_up():
    c = Client(account_sid=ACCOUNT_SID, api_key=API_KEY)
    try:
        assert c.calls is not None
        assert c.conferences is not None
        assert c.queues is not None
        assert c.applications is not None
        assert c.recordings is not None
        assert c.incoming_phone_numbers is not None
        assert c.notifications is not None
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
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls.json",
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
    # Twilio-compatible: every REST path ends with `.json` (closes audit CC-1).
    assert sent.url.path.endswith("/Calls.json")
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
        url=re.compile(r".*/Calls\.json(\?.*)?$"),
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


def test_calls_list_sends_page_token(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Calls\.json(\?.*)?$"),
        json={
            "calls": [],
            "page": 0,
            "page_size": 50,
            "total": 0,
            "next_page_uri": None,
            "uri": "/Calls",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.calls.list(page_token="abc123")
    sent = httpx_mock.get_request()
    assert sent is not None
    assert "PageToken=abc123" in sent.url.query.decode()


def test_calls_update_terminate(httpx_mock: HTTPXMock):
    call_sid = "CA" + "1" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}.json",
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
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Conferences/{cf_sid}.json",
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
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Queues.json",
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
        url=re.compile(r".*/Participants/CA.+\.json$"),
        json={
            "call_sid": "CA" + "4" * 32,
            "conference_sid": "CF" + "5" * 32,
            "account_sid": ACCOUNT_SID,
            "muted": True,
            "hold": False,
            "coaching": False,
            "queue_time": "0",
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
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}/Streams.json",
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
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/CA" + "8" * 32 + ".json",
        json={
            "code": 20003,
            "message": "Authentication Error",
            "more_info": "https://www.twilio.com/docs/errors/20003",
            "status": 401,
        },
        status_code=401,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        with pytest.raises(AuthenticationError) as exc:
            c.calls.get("CA" + "8" * 32)
    assert exc.value.status_code == 401
    assert exc.value.code == 20003
    # `.more_info` carries the docs URL Twilio includes in every error (closes audit CC-6).
    assert exc.value.more_info == "https://www.twilio.com/docs/errors/20003"


def test_more_info_is_none_when_absent(httpx_mock: HTTPXMock):
    """If the server doesn't include `more_info`, the attribute is `None` (not missing)."""
    sid = "CA" + "d" * 32
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{sid}.json",
        json={"code": 20404, "message": "Not Found", "status": 404},
        status_code=404,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        with pytest.raises(NotFoundError) as exc:
            c.calls.get(sid)
    assert exc.value.more_info is None


def test_404_raises_not_found(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/CA" + "9" * 32 + ".json",
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
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{sid}.json",
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
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{sid}/UserDefinedMessages.json",
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
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Queues/{sid}.json",
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
        url=re.compile(r".*/Calls\.json(\?.*)?$"),
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


# --- IncomingPhoneNumbers (v0.5.0) ---


PN_SID = "PN" + "0" * 32


def _ipn_payload(sid: str = PN_SID, phone_number: str = "+18005551234") -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "phone_number": phone_number,
        "friendly_name": "",
        "api_version": "2010-04-01",
        "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/IncomingPhoneNumbers/{sid}.json",
        "voice_url": "https://example.com/twiml",
        "voice_method": "POST",
        "voice_fallback_url": "",
        "voice_fallback_method": "POST",
        "capabilities": {"voice": True, "sms": False, "mms": False, "fax": False},
        "date_created": "Mon, 19 May 2026 12:00:00 +0000",
        "date_updated": "Mon, 19 May 2026 12:00:00 +0000",
    }


def test_incoming_phone_numbers_list_path_has_json(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/IncomingPhoneNumbers\.json(\?.*)?$"),
        json={
            "incoming_phone_numbers": [_ipn_payload()],
            "page": 0,
            "page_size": 50,
            "total": 1,
            "next_page_uri": None,
            "uri": "/x",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        result = c.incoming_phone_numbers.list(phone_number="+18005551234", page_size=10)
    assert isinstance(result, IncomingPhoneNumberList)
    assert len(result.incoming_phone_numbers) == 1
    assert result.incoming_phone_numbers[0].sid == PN_SID
    assert result.incoming_phone_numbers[0].phone_number == "+18005551234"
    sent = httpx_mock.get_request()
    assert sent is not None
    assert sent.url.path.endswith("/IncomingPhoneNumbers.json")
    query = sent.url.query.decode()
    assert "PhoneNumber=%2B18005551234" in query
    assert "PageSize=10" in query


def test_incoming_phone_numbers_create_form_body(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/IncomingPhoneNumbers.json",
        json=_ipn_payload(),
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ipn = c.incoming_phone_numbers.create(
            phone_number="+18005551234",
            voice_url="https://example.com/twiml",
            voice_method="POST",
        )
    assert isinstance(ipn, IncomingPhoneNumber)
    assert ipn.sid.startswith("PN")
    assert ipn.phone_number == "+18005551234"
    assert ipn.capabilities is not None and ipn.capabilities.voice is True
    sent = httpx_mock.get_request()
    body = sent.content.decode()
    assert "PhoneNumber=%2B18005551234" in body
    assert "VoiceUrl=https%3A%2F%2Fexample.com%2Ftwiml" in body
    assert "VoiceMethod=POST" in body


def test_incoming_phone_numbers_get_by_pn_sid(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/IncomingPhoneNumbers/{PN_SID}.json",
        json=_ipn_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ipn = c.incoming_phone_numbers.get(PN_SID)
    assert ipn.sid == PN_SID


def test_incoming_phone_numbers_get_by_e164_passthrough(httpx_mock: HTTPXMock):
    """Legacy E.164 sid is URL-encoded and forwarded — the server resolves it."""
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/IncomingPhoneNumbers/%2B18005551234.json",
        json=_ipn_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ipn = c.incoming_phone_numbers.get("+18005551234")
    # Response still carries the canonical PN-sid, regardless of how we looked it up.
    assert ipn.sid == PN_SID


def test_incoming_phone_numbers_update(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/IncomingPhoneNumbers/{PN_SID}.json",
        json={**_ipn_payload(), "voice_url": "https://example.com/new"},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ipn = c.incoming_phone_numbers.update(
            PN_SID, voice_url="https://example.com/new"
        )
    assert ipn.voice_url == "https://example.com/new"
    sent = httpx_mock.get_request()
    body = sent.content.decode()
    assert "VoiceUrl=https%3A%2F%2Fexample.com%2Fnew" in body
    # Only the field we set is sent — friendly_name is not touched.
    assert "FriendlyName" not in body


def test_incoming_phone_numbers_delete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/IncomingPhoneNumbers/{PN_SID}.json",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.incoming_phone_numbers.delete(PN_SID)


async def test_incoming_phone_numbers_async(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/IncomingPhoneNumbers\.json(\?.*)?$"),
        json={
            "incoming_phone_numbers": [_ipn_payload()],
            "page": 0,
            "page_size": 50,
            "total": 1,
            "next_page_uri": None,
            "uri": "/x",
        },
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        result = await c.incoming_phone_numbers.list()
    assert len(result.incoming_phone_numbers) == 1


def test_recording_audio_path_ends_with_wav_not_json(httpx_mock: HTTPXMock):
    """The `.wav` audio endpoint must NOT get a `.json` suffix appended (recordings.py)."""
    re_sid = "RE" + "e" * 32
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Recordings/{re_sid}.wav",
        content=b"RIFF\x00\x00\x00\x00WAVE",
        headers={"content-type": "audio/wav"},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        audio = c.recordings.get_audio(re_sid)
    assert audio.content.startswith(b"RIFF")
    sent = httpx_mock.get_request()
    assert sent.url.path.endswith(f"/Recordings/{re_sid}.wav")
    # Defensive: should not contain `.json` anywhere on the path.
    assert ".json" not in sent.url.path


# --- spec v0.6.2 deltas ---


def test_recording_deserializes_media_url_when_present():
    """D5 (spec v0.6.2): Recording.media_url carries the audio URL when the server sets it."""
    re_sid = "RE" + "f" * 32
    payload = {
        "sid": re_sid,
        "account_sid": ACCOUNT_SID,
        "call_sid": "CA" + "0" * 32,
        "status": "completed",
        "media_url": f"https://api.voicetel.com/2010-04-01/Accounts/{ACCOUNT_SID}/Recordings/{re_sid}.wav",
    }
    rec = Recording.model_validate(payload)
    assert rec.media_url == payload["media_url"]


def test_recording_deserializes_without_media_url_for_backward_compat():
    """Older (<v0.6.2) servers don't emit media_url — the field must be optional/None."""
    re_sid = "RE" + "a" * 32
    payload = {
        "sid": re_sid,
        "account_sid": ACCOUNT_SID,
        "call_sid": "CA" + "1" * 32,
        "status": "completed",
    }
    rec = Recording.model_validate(payload)
    assert rec.media_url is None


def test_incoming_phone_number_deserializes_type_field():
    """D6 (spec v0.6.2): IncomingPhoneNumber.type round-trips the Twilio number-class enum."""
    payload = {**_ipn_payload(), "type": "local"}
    ipn = IncomingPhoneNumber.model_validate(payload)
    assert ipn.type == "local"
    # VoiceML emits empty by default — also accept "" / None.
    ipn_empty = IncomingPhoneNumber.model_validate({**_ipn_payload(), "type": ""})
    assert ipn_empty.type == ""
    ipn_absent = IncomingPhoneNumber.model_validate(_ipn_payload())
    assert ipn_absent.type is None


# --- spec v0.6.3 deltas ---


def test_participant_coaching_fields_round_trip():
    payload = {
        "call_sid": "CA" + "d" * 32,
        "conference_sid": "CF" + "c" * 32,
        "account_sid": ACCOUNT_SID,
        "muted": False,
        "hold": False,
        "coaching": True,
        "call_sid_to_coach": "CA" + "e" * 32,
        "queue_time": "12",
        "start_conference_on_enter": True,
        "end_conference_on_exit": False,
        "status": "connected",
        "api_version": "2010-04-01",
        "uri": "/x",
    }
    p = Participant.model_validate(payload)
    assert p.coaching is True
    assert p.call_sid_to_coach == payload["call_sid_to_coach"]
    assert p.queue_time == "12"


def test_recording_error_code_and_conference_source():
    payload = {
        "sid": "RE" + "b" * 32,
        "account_sid": ACCOUNT_SID,
        "call_sid": "CA" + "0" * 32,
        "status": "completed",
        "source": "StartConferenceRecordingAPI",
        "error_code": None,
    }
    rec = Recording.model_validate(payload)
    assert rec.source == "StartConferenceRecordingAPI"
    assert rec.error_code is None


def test_calls_list_emits_v063_start_time_filters(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Calls\.json(\?.*)?$"),
        json={"calls": [], "page": 0, "page_size": 50, "total": 0, "uri": "/x"},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.calls.list(start_time="2026-05-21", start_time_gt="2026-05-20", end_time_lt="2026-05-22")
    sent = httpx_mock.get_request()
    assert sent is not None
    q = str(sent.url.query)
    assert "StartTime=2026-05-21" in q
    assert "StartTime%3E=2026-05-20" in q
    assert "EndTime%3C=2026-05-22" in q


def test_create_queue_allows_max_size_zero(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=re.compile(r".*/Queues\.json$"),
        json={
            "sid": "QU" + "0" * 32,
            "account_sid": ACCOUNT_SID,
            "friendly_name": "support",
            "current_size": 0,
            "max_size": 0,
            "average_wait_time": 0,
            "date_created": "Mon, 21 May 2026 00:00:00 +0000",
            "date_updated": "Mon, 21 May 2026 00:00:00 +0000",
            "uri": "/x",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        q = c.queues.create(CreateQueueRequest(FriendlyName="support", MaxSize=0))
    assert q.max_size == 0
    sent = httpx_mock.get_request()
    assert sent is not None
    assert b"MaxSize=0" in sent.content


# --- spec v0.6.6 deltas ---


def test_conferences_create_participant_sends_from_to(httpx_mock: HTTPXMock):
    cf_sid = "CF" + "f" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Conferences/{cf_sid}/Participants.json",
        json={
            "call_sid": "CA" + "f" * 32,
            "conference_sid": cf_sid,
            "account_sid": ACCOUNT_SID,
            "muted": False,
            "hold": False,
            "coaching": False,
            "queue_time": "0",
            "start_conference_on_enter": True,
            "end_conference_on_exit": False,
            "status": "queued",
            "api_version": "2010-04-01",
            "uri": "/x",
        },
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        p = c.conferences.create_participant(
            cf_sid,
            CreateParticipantRequest(From="+18005550000", To="+18005551234"),
        )
    assert isinstance(p, Participant)
    sent = httpx_mock.get_request()
    body = sent.content.decode()
    assert "From=%2B18005550000" in body
    assert "To=%2B18005551234" in body


def test_calls_list_notifications_sends_filter_params(httpx_mock: HTTPXMock):
    call_sid = "CA" + "f" * 32
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf".*/Calls/{call_sid}/Notifications\.json(\?.*)?$"
        ),
        json={
            "notifications": [],
            "page": 0,
            "page_size": 50,
            "total": 0,
            "uri": "/x",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.calls.list_notifications(
            call_sid,
            log=1,
            message_date="2026-05-01",
            message_date_lt="2026-05-02",
            message_date_gt="2026-04-30",
        )
    sent = httpx_mock.get_request()
    assert sent is not None
    q = sent.url.query.decode()
    assert "Log=1" in q
    assert "MessageDate=2026-05-01" in q
    assert "MessageDate%3C=2026-05-02" in q
    assert "MessageDate%3E=2026-04-30" in q


def test_recordings_list_sends_include_soft_deleted(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Recordings\.json(\?.*)?$"),
        json={
            "recordings": [],
            "page": 0,
            "page_size": 50,
            "total": 0,
            "uri": "/x",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.recordings.list(include_soft_deleted=True)
    sent = httpx_mock.get_request()
    assert sent is not None
    assert "IncludeSoftDeleted=true" in sent.url.query.decode()


def test_recordings_get_sends_include_soft_deleted(httpx_mock: HTTPXMock):
    re_sid = "RE" + "c" * 32
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf".*/Recordings/{re_sid}\.json(\?.*)?$"),
        json={
            "sid": re_sid,
            "account_sid": ACCOUNT_SID,
            "call_sid": "CA" + "0" * 32,
            "status": "completed",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.recordings.get(re_sid, include_soft_deleted=True)
    sent = httpx_mock.get_request()
    assert sent is not None
    assert "IncludeSoftDeleted=true" in sent.url.query.decode()


# --- iter() auto-pagination ---


def _conference_payload(sid: str) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "friendly_name": "room-1",
        "status": "in-progress",
        "api_version": "2010-04-01",
        "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Conferences/{sid}.json",
    }


def _recording_payload(sid: str) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "call_sid": "CA" + "0" * 32,
        "status": "completed",
    }


def _queue_payload(sid: str) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "friendly_name": "support",
        "current_size": 0,
        "max_size": 100,
        "average_wait_time": 0,
        "date_created": "Mon, 26 May 2026 00:00:00 +0000",
        "date_updated": "Mon, 26 May 2026 00:00:00 +0000",
        "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Queues/{sid}.json",
    }


def test_calls_iter_two_pages(httpx_mock: HTTPXMock):
    """iter() follows next_page_uri across 2 pages and returns all items."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Calls\.json(\?.*)?$"),
        json={
            "calls": [_call_payload("CA" + "1" * 32), _call_payload("CA" + "2" * 32)],
            "page": 0,
            "page_size": 2,
            "next_page_uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Calls.json?Page=1&PageSize=2",
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Calls.json",
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Calls\.json(\?.*)?$"),
        json={
            "calls": [_call_payload("CA" + "3" * 32)],
            "page": 1,
            "page_size": 2,
            "next_page_uri": None,
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Calls.json?Page=1",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        results = c.calls.iter(page_size=2)
    assert len(results) == 3
    assert results[0].sid == "CA" + "1" * 32
    assert results[1].sid == "CA" + "2" * 32
    assert results[2].sid == "CA" + "3" * 32
    requests = httpx_mock.get_requests()
    assert len(requests) == 2


def test_conferences_iter_two_pages(httpx_mock: HTTPXMock):
    """iter() follows next_page_uri across 2 pages for conferences."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Conferences\.json(\?.*)?$"),
        json={
            "conferences": [
                _conference_payload("CF" + "1" * 32),
                _conference_payload("CF" + "2" * 32),
            ],
            "page": 0,
            "page_size": 2,
            "next_page_uri": (
                f"/2010-04-01/Accounts/{ACCOUNT_SID}/Conferences.json?Page=1&PageSize=2"
            ),
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Conferences.json",
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Conferences\.json(\?.*)?$"),
        json={
            "conferences": [_conference_payload("CF" + "3" * 32)],
            "page": 1,
            "page_size": 2,
            "next_page_uri": None,
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Conferences.json?Page=1",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        results = c.conferences.iter(page_size=2)
    assert len(results) == 3
    assert results[0].sid == "CF" + "1" * 32
    assert results[1].sid == "CF" + "2" * 32
    assert results[2].sid == "CF" + "3" * 32
    requests = httpx_mock.get_requests()
    assert len(requests) == 2


def test_recordings_iter_two_pages(httpx_mock: HTTPXMock):
    """iter() follows next_page_uri across 2 pages for recordings."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Recordings\.json(\?.*)?$"),
        json={
            "recordings": [
                _recording_payload("RE" + "1" * 32),
                _recording_payload("RE" + "2" * 32),
            ],
            "page": 0,
            "page_size": 2,
            "next_page_uri": (
                f"/2010-04-01/Accounts/{ACCOUNT_SID}/Recordings.json?Page=1&PageSize=2"
            ),
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Recordings.json",
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Recordings\.json(\?.*)?$"),
        json={
            "recordings": [_recording_payload("RE" + "3" * 32)],
            "page": 1,
            "page_size": 2,
            "next_page_uri": None,
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Recordings.json?Page=1",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        results = c.recordings.iter(page_size=2)
    assert len(results) == 3
    assert results[0].sid == "RE" + "1" * 32
    assert results[1].sid == "RE" + "2" * 32
    assert results[2].sid == "RE" + "3" * 32
    requests = httpx_mock.get_requests()
    assert len(requests) == 2


def test_queues_iter_two_pages(httpx_mock: HTTPXMock):
    """iter() follows next_page_uri across 2 pages for queues."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Queues\.json(\?.*)?$"),
        json={
            "queues": [
                _queue_payload("QU" + "1" * 32),
                _queue_payload("QU" + "2" * 32),
            ],
            "page": 0,
            "page_size": 2,
            "next_page_uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Queues.json?Page=1&PageSize=2",
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Queues.json",
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Queues\.json(\?.*)?$"),
        json={
            "queues": [_queue_payload("QU" + "3" * 32)],
            "page": 1,
            "page_size": 2,
            "next_page_uri": None,
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Queues.json?Page=1",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        results = c.queues.iter(page_size=2)
    assert len(results) == 3
    assert results[0].sid == "QU" + "1" * 32
    assert results[1].sid == "QU" + "2" * 32
    assert results[2].sid == "QU" + "3" * 32
    requests = httpx_mock.get_requests()
    assert len(requests) == 2


def test_calls_iter_single_page(httpx_mock: HTTPXMock):
    """iter() with only 1 page makes exactly 1 HTTP request."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Calls\.json(\?.*)?$"),
        json={
            "calls": [_call_payload("CA" + "a" * 32), _call_payload("CA" + "b" * 32)],
            "page": 0,
            "page_size": 50,
            "next_page_uri": None,
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Calls.json",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        results = c.calls.iter()
    assert len(results) == 2
    assert results[0].sid == "CA" + "a" * 32
    assert results[1].sid == "CA" + "b" * 32
    requests = httpx_mock.get_requests()
    assert len(requests) == 1
