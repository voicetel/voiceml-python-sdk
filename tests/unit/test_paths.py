"""Path building: every caller-supplied segment is percent-encoded and the ``.json``
suffix comes from the route, not from the shape of the last segment."""

from __future__ import annotations

import httpx
import pytest

from voiceml import Client
from voiceml.models import UpdateRecordingRequest
from voiceml.resources._base import account_path, path, seg

ACCOUNT_SID = "AC" + "c" * 32
ROOT = f"/2010-04-01/Accounts/{ACCOUNT_SID}"


@pytest.mark.parametrize(
    ("raw", "encoded"),
    [
        ("CA0123abc", "CA0123abc"),
        ("a-b.c_d~e", "a-b.c_d~e"),
        ("+14155550100", "%2B14155550100"),
        ("a b", "a%20b"),
        ("a/b", "a%2Fb"),
        ("a?b", "a%3Fb"),
        ("a#b", "a%23b"),
        ("100%", "100%25"),
        ("../..", "..%2F.."),
        ("é", "%C3%A9"),
    ],
)
def test_seg_keeps_only_unreserved_characters(raw: str, encoded: str) -> None:
    assert seg(raw) == encoded


def test_account_path_suffix_comes_from_the_route() -> None:
    assert account_path("AC1", "Calls", "CA1") == "/2010-04-01/Accounts/AC1/Calls/CA1.json"
    assert (
        account_path("AC1", "Calls", "CA1", "Recordings", "Twilio.CURRENT")
        == "/2010-04-01/Accounts/AC1/Calls/CA1/Recordings/Twilio.CURRENT.json"
    )
    assert account_path("AC1", "Exports", "2026-07-01", suffix="") == (
        "/2010-04-01/Accounts/AC1/Exports/2026-07-01"
    )
    assert account_path("AC1", "Recordings", "RE1", suffix=".wav") == (
        "/2010-04-01/Accounts/AC1/Recordings/RE1.wav"
    )
    assert path("v1", "Services", "MG 1") == "/v1/Services/MG%201"


class Recorder:
    def __init__(self, body: object) -> None:
        self.body = body
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(200, json=self.body)

    def client(self) -> Client:
        return Client(
            account_sid=ACCOUNT_SID,
            api_key="k",
            http_client=httpx.Client(transport=httpx.MockTransport(self)),
        )


def test_twilio_current_recording_update_keeps_json_suffix() -> None:
    recorder = Recorder({"status": "stopped"})
    with recorder.client() as c:
        c.calls.update_recording("CA1", "Twilio.CURRENT", UpdateRecordingRequest(status="stopped"))
    assert recorder.requests[0].url.raw_path == (
        f"{ROOT}/Calls/CA1/Recordings/Twilio.CURRENT.json".encode()
    )
    assert recorder.requests[0].content == b"Status=stopped"


def test_traversal_and_query_injection_stay_inside_the_segment() -> None:
    recorder = Recorder({"status": "queued"})
    with recorder.client() as c:
        c.calls.get("../../../../health")
        c.calls.get("CA1?x=1#")
    assert recorder.requests[0].url.raw_path == (
        f"{ROOT}/Calls/..%2F..%2F..%2F..%2Fhealth.json".encode()
    )
    assert recorder.requests[1].url.raw_path == f"{ROOT}/Calls/CA1%3Fx%3D1%23.json".encode()
    assert recorder.requests[1].url.query == b""


def test_e164_identifiers_are_encoded_once() -> None:
    recorder = Recorder({})
    with recorder.client() as c:
        c.incoming_phone_numbers.get("+14155550100")
        c.routes_v2.phone_numbers.fetch("+14155550100")
        c.pricing.v2.voice.numbers.fetch("+14155550100")
    raw = [r.url.raw_path for r in recorder.requests]
    assert raw[0] == f"{ROOT}/IncomingPhoneNumbers/%2B14155550100.json".encode()
    assert raw[1] == b"/v2/PhoneNumbers/%2B14155550100"
    assert raw[2] == b"/v2/Voice/Numbers/%2B14155550100"


def test_v1_paths_encode_every_segment() -> None:
    recorder = Recorder({})
    with recorder.client() as c:
        c.conversations_v1.conversations("CH 1/2").messages.fetch("IM?1")
        c.voice_v1.byoc_trunks.fetch("BY#1")
        c.assistants_v1.assistants("aia asst").tools.detach("t/1")
    raw = [r.url.raw_path for r in recorder.requests]
    assert raw[0] == b"/v1/Conversations/CH%201%2F2/Messages/IM%3F1"
    assert raw[1] == b"/v1/ByocTrunks/BY%231"
    assert raw[2] == b"/v1/Assistants/aia%20asst/Tools/t%2F1"
