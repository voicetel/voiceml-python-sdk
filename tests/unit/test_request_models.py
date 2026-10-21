"""Request models are strict and serialise exactly as the API expects."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, timedelta, timezone

import httpx
import pytest
from pydantic import ValidationError

from voiceml import Client
from voiceml.models import (
    CreateApplicationRequest,
    CreateCallRequest,
    CreateIncomingPhoneNumberRequest,
    CreateMessageRequest,
    CreateOutgoingCallerIdRequest,
    CreateTypedIncomingPhoneNumberRequest,
    UpdateAccountRequest,
    UpdateConversationsV1ConversationRequest,
    UpdateIncomingPhoneNumberRequest,
)
from voiceml.models._base import form_value

ACCOUNT_SID = "AC" + "4" * 32
MESSAGES = f"/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json"


class Recorder:
    def __init__(self, body: object = None) -> None:
        self.body = body if body is not None else {}
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


MESSAGE_JSON = {
    "sid": "SM" + "1" * 32,
    "account_sid": ACCOUNT_SID,
    "api_version": "2010-04-01",
    "to": "+14155550100",
    "body": "",
    "status": "queued",
    "num_segments": "1",
    "num_media": "2",
    "direction": "outbound-api",
    "date_created": "Wed, 01 Jul 2026 00:00:00 +0000",
    "date_updated": "Wed, 01 Jul 2026 00:00:00 +0000",
    "uri": MESSAGES,
}


def test_misspelled_fields_are_rejected() -> None:
    with pytest.raises(ValidationError, match="urll"):
        CreateCallRequest(to="+14155550100", from_="+14155550101", urll="https://x")
    with pytest.raises(ValidationError, match="StatusCallBack"):
        CreateCallRequest(To="+14155550100", From="+14155550101", StatusCallBack="https://x")


def test_wire_aliases_and_field_names_are_both_accepted() -> None:
    a = CreateCallRequest(To="+14155550100", From="+14155550101", Url="https://x")
    b = CreateCallRequest(to="+14155550100", from_="+14155550101", url="https://x")
    assert (
        a.to_form()
        == b.to_form()
        == {
            "To": "+14155550100",
            "From": "+14155550101",
            "Url": "https://x",
        }
    )


@pytest.mark.parametrize(
    "build",
    [
        lambda: CreateApplicationRequest(voice_method="get"),
        lambda: CreateIncomingPhoneNumberRequest(phone_number="+14155550100", sms_method="PUT"),
        lambda: UpdateConversationsV1ConversationRequest(state="open"),
        lambda: CreateCallRequest(
            to="+14155550100", from_="+14155550101", status_callback_event=["queued"]
        ),
    ],
)
def test_enum_typed_request_fields_stay_constrained(build: Callable[[], object]) -> None:
    with pytest.raises(ValidationError):
        build()


def test_typed_number_creates_accept_only_their_three_fields() -> None:
    with pytest.raises(ValidationError):
        CreateTypedIncomingPhoneNumberRequest(
            phone_number="+14155550100", voice_fallback_url="https://x"
        )
    with pytest.raises(ValidationError):
        CreateIncomingPhoneNumberRequest(phone_number="+14155550100", friendly_name="x")


def test_sms_application_sid_is_validated() -> None:
    ok = CreateIncomingPhoneNumberRequest(
        phone_number="+14155550100", sms_application_sid="AP" + "a" * 32
    )
    assert ok.to_form()["SmsApplicationSid"] == "AP" + "a" * 32
    with pytest.raises(ValidationError):
        CreateIncomingPhoneNumberRequest(phone_number="+14155550100", sms_application_sid="AP1")


def test_voice_application_sid_is_validated() -> None:
    ok = UpdateIncomingPhoneNumberRequest(voice_application_sid="AP" + "a" * 32)
    assert ok.to_form()["VoiceApplicationSid"] == "AP" + "a" * 32
    with pytest.raises(ValidationError):
        UpdateIncomingPhoneNumberRequest(voice_application_sid="AP1")
    with pytest.raises(ValidationError):
        CreateIncomingPhoneNumberRequest(phone_number="+14155550100", voice_application_sid="AP1")


def test_incoming_phone_number_status_callback_serialises() -> None:
    form = UpdateIncomingPhoneNumberRequest(
        status_callback="https://example.com/inbound-status",
        status_callback_method="GET",
    ).to_form()
    assert form == {
        "StatusCallback": "https://example.com/inbound-status",
        "StatusCallbackMethod": "GET",
    }


def test_outgoing_caller_id_create_request_full_form() -> None:
    form = CreateOutgoingCallerIdRequest(
        phone_number="+14155550100",
        friendly_name="Desk",
        call_delay=30,
        extension="89",
        status_callback="https://example.com/verification",
        status_callback_method="POST",
    ).to_form()
    assert form == {
        "PhoneNumber": "+14155550100",
        "FriendlyName": "Desk",
        "CallDelay": 30,
        "Extension": "89",
        "StatusCallback": "https://example.com/verification",
        "StatusCallbackMethod": "POST",
    }
    with pytest.raises(ValidationError):
        CreateOutgoingCallerIdRequest(phone_number="+14155550100", call_delay=61)
    with pytest.raises(ValidationError):
        CreateOutgoingCallerIdRequest(phone_number="+14155550100", call_delay=-1)


def test_form_value_rendering() -> None:
    assert form_value(True) == "true"
    assert form_value(False) == "false"
    assert form_value(datetime(2026, 7, 1, 12, 30, tzinfo=timezone.utc)) == "2026-07-01T12:30:00Z"
    est = timezone(timedelta(hours=-5))
    assert form_value(datetime(2026, 7, 1, 7, 30, tzinfo=est)) == "2026-07-01T12:30:00Z"
    assert form_value(datetime(2026, 7, 1, 12, 30)) == "2026-07-01T12:30:00Z"
    assert form_value(date(2026, 7, 1)) == "2026-07-01"
    assert form_value({"a": 1, "b": [True, None]}) == '{"a":1,"b":[true,null]}'
    assert form_value([True, "x"]) == ["true", "x"]
    assert form_value("") == ""


def test_lists_are_sent_as_repeated_keys_exact_bytes() -> None:
    recorder = Recorder({"sid": "CA1", "status": "queued"})
    with recorder.client() as c:
        c.calls.create(
            CreateCallRequest(
                to="+14155550100",
                from_="+14155550101",
                url="https://example.com/a b",
                status_callback_event=["initiated", "completed"],
                record=False,
            )
        )
    assert recorder.requests[0].content == (
        b"To=%2B14155550100&From=%2B14155550101&Url=https%3A%2F%2Fexample.com%2Fa+b"
        b"&StatusCallbackEvent=initiated&StatusCallbackEvent=completed&Record=false"
    )
    assert recorder.requests[0].headers["content-type"] == "application/x-www-form-urlencoded"


def test_mms_sends_repeated_media_url_keys_and_no_body() -> None:
    recorder = Recorder(MESSAGE_JSON)
    with recorder.client() as c:
        c.messages.create(
            to="+14155550100",
            media_url=["https://example.com/1.png", "https://example.com/2.png"],
            validity_period=600,
            status_callback_method="POST",
        )
    assert recorder.requests[0].content == (
        b"To=%2B14155550100"
        b"&MediaUrl=https%3A%2F%2Fexample.com%2F1.png&MediaUrl=https%3A%2F%2Fexample.com%2F2.png"
        b"&ValidityPeriod=600&StatusCallbackMethod=POST"
    )


def test_message_needs_body_or_media_and_sends_nothing_otherwise() -> None:
    recorder = Recorder(MESSAGE_JSON)
    with recorder.client() as c, pytest.raises(ValidationError, match="Body or MediaUrl"):
        c.messages.create(to="+14155550100")
    assert recorder.requests == []
    with pytest.raises(ValidationError):
        CreateMessageRequest(to="+14155550100", body="x", validity_period=0)


def test_empty_body_redaction_round_trips() -> None:
    recorder = Recorder(MESSAGE_JSON)
    with recorder.client() as c:
        c.messages.update("SM1", body="")
    assert recorder.requests[0].content == b"Body="


def test_datetime_and_date_filters_are_serialised() -> None:
    recorder = Recorder({"calls": [], "usage_records": []})
    with recorder.client() as c:
        c.calls.list(start_time_gt=datetime(2026, 7, 1, tzinfo=timezone.utc))
        c.usage_records.list(
            start_date=date(2026, 7, 1), end_date="2026-07-31", include_subaccounts=False
        )
    assert recorder.requests[0].url.query == b"StartTime%3E=2026-07-01T00%3A00%3A00Z"
    assert recorder.requests[1].url.query == (
        b"StartDate=2026-07-01&EndDate=2026-07-31&IncludeSubaccounts=false"
    )


def test_account_allow_cidr_list_and_clear() -> None:
    assert UpdateAccountRequest(allow_cidr=["10.0.0.0/8", "192.0.2.0/24"]).to_form() == {
        "AllowCidr": ["10.0.0.0/8", "192.0.2.0/24"]
    }
    assert UpdateAccountRequest(allow_cidr=[]).to_form() == {"AllowCidr": ""}
    recorder = Recorder({"sid": ACCOUNT_SID})
    with recorder.client() as c:
        c.accounts.update(allow_cidr=[])
    assert recorder.requests[0].content == b"AllowCidr="


def test_json_bodies_drop_unset_and_none() -> None:
    recorder = Recorder({"id": "aia_asst_1"})
    with recorder.client() as c:
        c.assistants_v1.assistants.create(name="Ava", customer_ai={"perception_engine": True})
    sent = recorder.requests[0]
    assert sent.headers["content-type"] == "application/json"
    assert sent.content == b'{"name":"Ava","customer_ai":{"perception_engine":true}}'
