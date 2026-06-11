"""Unit tests for the Messages resource and Calls.Payments sub-resource.

Wire-shape assertions only — no network. Uses pytest-httpx like the rest of the
suite.
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs

import pytest
from pytest_httpx import HTTPXMock

from voiceml import AsyncClient, Client
from voiceml.models import (
    CallPayment,
    Message,
    MessageList,
    PaymentBankAccountType,
)

ACCOUNT_SID = "AC" + "f" * 32
API_KEY = "secret-key-1234"
BASE = "https://voiceml.voicetel.com"


def _message_payload(
    sid: str = "SM" + "0" * 32,
    *,
    to: str = "+18005551234",
    from_: str = "+18005550000",
    body: str = "hello",
    status: str = "sent",
    error_code: int | None = None,
    error_message: str | None = None,
    messaging_service_sid: str | None = None,
    date_sent: str | None = "Mon, 26 May 2026 12:00:00 +0000",
) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "api_version": "2010-04-01",
        "to": to,
        "from": from_,
        "body": body,
        "status": status,
        "num_segments": "1",
        "num_media": "0",
        "direction": "outbound-api",
        "price": None,
        "price_unit": None,
        "error_code": error_code,
        "error_message": error_message,
        "messaging_service_sid": messaging_service_sid,
        "date_created": "Mon, 26 May 2026 12:00:00 +0000",
        "date_updated": "Mon, 26 May 2026 12:00:00 +0000",
        "date_sent": date_sent,
        "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Messages/{sid}.json",
    }


def _form_body(content: bytes) -> dict[str, list[str]]:
    """Parse a form-encoded request body into a {key: [values]} dict."""
    return parse_qs(content.decode(), keep_blank_values=True)


# --- Messages: create / fetch / list / update / delete -------------------------


def test_messages_resource_is_wired_on_client():
    c = Client(account_sid=ACCOUNT_SID, api_key=API_KEY)
    try:
        assert c.messages is not None
    finally:
        c.close()


def test_messages_create_sends_form_and_basic_auth(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json",
        json=_message_payload(),
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        msg = c.messages.create(
            to="+18005551234",
            body="hello there",
            from_="+18005550000",
            status_callback="https://example.com/sms-status",
        )
    assert isinstance(msg, Message)
    assert msg.sid.startswith("SM")
    assert msg.status == "sent"
    # `from` is reserved so the model field is `from_` — make sure the alias round-trips.
    assert msg.from_ == "+18005550000"
    # Wire-shape: num_segments/num_media are strings, not ints (Twilio compat).
    assert msg.num_segments == "1"
    assert msg.num_media == "0"

    sent = httpx_mock.get_request()
    assert sent is not None
    assert sent.url.path.endswith("/Messages.json")
    assert sent.headers["Content-Type"].startswith("application/x-www-form-urlencoded")
    body = sent.content.decode()
    assert "To=%2B18005551234" in body
    # URL-encoded space inside Body.
    assert "Body=hello+there" in body or "Body=hello%20there" in body
    assert "From=%2B18005550000" in body
    assert (
        "StatusCallback=https%3A%2F%2Fexample.com%2Fsms-status" in body
    )


def test_messages_create_with_messaging_service_sid(httpx_mock: HTTPXMock):
    """When MessagingServiceSid is set, From may be omitted — both shapes are valid."""
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json",
        json=_message_payload(messaging_service_sid="MG" + "1" * 32),
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        msg = c.messages.create(
            to="+18005551234",
            body="hi",
            messaging_service_sid="MG" + "1" * 32,
        )
    assert msg.messaging_service_sid == "MG" + "1" * 32
    sent = httpx_mock.get_request()
    body = sent.content.decode()
    assert "MessagingServiceSid=MG" in body
    # When the caller omitted From, no From= key in the body.
    assert "From=" not in body


def test_messages_fetch(httpx_mock: HTTPXMock):
    sid = "SM" + "1" * 32
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Messages/{sid}.json",
        json=_message_payload(sid),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        msg = c.messages.fetch(sid)
    assert msg.sid == sid


def test_messages_list_sends_filter_params(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Messages\.json(\?.*)?$"),
        json={
            "messages": [_message_payload()],
            "page": 0,
            "page_size": 50,
            "total": 1,
            "next_page_uri": None,
            "uri": "/x",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        result = c.messages.list(
            to="+18005551234",
            from_="+18005550000",
            date_sent="2026-05-26",
            date_sent_lt="2026-05-27",
            date_sent_gt="2026-05-25",
            page_size=25,
        )
    assert isinstance(result, MessageList)
    assert len(result.messages) == 1
    sent = httpx_mock.get_request()
    assert sent is not None
    q = sent.url.query.decode()
    assert "To=%2B18005551234" in q
    assert "From=%2B18005550000" in q
    assert "DateSent=2026-05-26" in q
    # Twilio uses literal `DateSent<` / `DateSent>` operators in the query string.
    assert "DateSent%3C=2026-05-27" in q
    assert "DateSent%3E=2026-05-25" in q
    assert "PageSize=25" in q


def test_messages_list_pagination(httpx_mock: HTTPXMock):
    """``iter()`` walks ``next_page_uri`` and concatenates pages."""
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Messages\.json(\?.*)?$"),
        json={
            "messages": [
                _message_payload("SM" + "1" * 32),
                _message_payload("SM" + "2" * 32),
            ],
            "page": 0,
            "page_size": 2,
            "next_page_uri": (
                f"/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json?Page=1&PageSize=2"
            ),
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json",
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r".*/Messages\.json(\?.*)?$"),
        json={
            "messages": [_message_payload("SM" + "3" * 32)],
            "page": 1,
            "page_size": 2,
            "next_page_uri": None,
            "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json?Page=1",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        results = c.messages.iter(page_size=2)
    assert len(results) == 3
    assert results[0].sid == "SM" + "1" * 32
    assert results[2].sid == "SM" + "3" * 32
    requests = httpx_mock.get_requests()
    assert len(requests) == 2


def test_messages_update_body_redaction(httpx_mock: HTTPXMock):
    """``body=""`` redacts on the server; only the field the caller set is on the wire."""
    sid = "SM" + "4" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Messages/{sid}.json",
        json={**_message_payload(sid), "body": ""},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        msg = c.messages.update(sid, body="")
    assert msg.body == ""
    sent = httpx_mock.get_request()
    parsed = _form_body(sent.content)
    # Body is the empty string — must round-trip the wire key.
    assert parsed.get("Body") == [""]
    # Status was not set — must NOT appear in the request.
    assert "Status" not in parsed


def test_messages_update_status_canceled(httpx_mock: HTTPXMock):
    sid = "SM" + "5" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Messages/{sid}.json",
        json={**_message_payload(sid), "status": "canceled"},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        msg = c.messages.update(sid, status="canceled")
    assert msg.status == "canceled"
    sent = httpx_mock.get_request()
    parsed = _form_body(sent.content)
    assert parsed.get("Status") == ["canceled"]
    assert "Body" not in parsed


def test_messages_delete(httpx_mock: HTTPXMock):
    sid = "SM" + "6" * 32
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Messages/{sid}.json",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.messages.delete(sid)


def test_messages_model_handles_nullable_fields():
    """``error_code`` is nullable int; the other nullable fields are nullable strings."""
    payload = _message_payload(
        status="failed",
        error_code=30001,
        error_message="upstream gateway failure",
        date_sent=None,
    )
    msg = Message.model_validate(payload)
    assert msg.error_code == 30001
    assert msg.error_message == "upstream gateway failure"
    assert msg.date_sent is None
    assert msg.price is None
    assert msg.price_unit is None


async def test_messages_async_create(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json",
        json=_message_payload(),
        status_code=201,
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        msg = await c.messages.create(to="+18005551234", body="async hello")
    assert msg.sid.startswith("SM")


# --- Payments: start / update -------------------------------------------------


def _payment_payload(
    sid: str = "PY" + "0" * 32, call_sid: str = "CA" + "0" * 32
) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "call_sid": call_sid,
        "api_version": "2010-04-01",
        "date_created": "Mon, 26 May 2026 12:00:00 +0000",
        "date_updated": "Mon, 26 May 2026 12:00:00 +0000",
        "uri": (
            f"/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}/Payments/{sid}.json"
        ),
    }


def test_calls_start_payment_path_and_form(httpx_mock: HTTPXMock):
    call_sid = "CA" + "a" * 32
    expected_path = (
        f"/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}/Payments.json"
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}{expected_path}",
        json=_payment_payload(call_sid=call_sid),
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        payment = c.calls.start_payment(
            call_sid,
            idempotency_key="abc-123",
            status_callback="https://example.com/pay-status",
            bank_account_type="consumer-checking",
            charge_amount="9.99",
            currency="USD",
            description="Order #42",
            input="dtmf",
            min_postal_code_length=5,
            parameter="custom=1",
            payment_connector="Stripe_Connector_1",
            payment_method="credit-card",
            postal_code=True,
            security_code=False,
            timeout=15,
            token_type="reusable",
            valid_card_types="visa mastercard",
            require_matching_inputs="security-code postal-code",
            confirmation=True,
        )
    assert isinstance(payment, CallPayment)
    assert payment.sid.startswith("PY")
    assert payment.call_sid == call_sid

    sent = httpx_mock.get_request()
    assert sent is not None
    # Path must match exactly — confirms the Twilio-compatible ``.json`` suffix on the
    # sub-resource path.
    assert sent.url.path == expected_path
    parsed = _form_body(sent.content)
    assert parsed["IdempotencyKey"] == ["abc-123"]
    assert parsed["StatusCallback"] == ["https://example.com/pay-status"]
    assert parsed["BankAccountType"] == ["consumer-checking"]
    assert parsed["ChargeAmount"] == ["9.99"]
    assert parsed["Currency"] == ["USD"]
    assert parsed["Description"] == ["Order #42"]
    assert parsed["Input"] == ["dtmf"]
    assert parsed["MinPostalCodeLength"] == ["5"]
    assert parsed["Parameter"] == ["custom=1"]
    assert parsed["PaymentConnector"] == ["Stripe_Connector_1"]
    assert parsed["PaymentMethod"] == ["credit-card"]
    # Booleans wire as the strings "true" / "false" — Twilio convention.
    assert parsed["PostalCode"] == ["true"]
    assert parsed["SecurityCode"] == ["false"]
    assert parsed["Timeout"] == ["15"]
    assert parsed["TokenType"] == ["reusable"]
    assert parsed["ValidCardTypes"] == ["visa mastercard"]
    assert parsed["RequireMatchingInputs"] == ["security-code postal-code"]
    assert parsed["Confirmation"] == ["true"]


def test_calls_start_payment_omits_unset_fields(httpx_mock: HTTPXMock):
    """Only the fields the caller passed must hit the wire."""
    call_sid = "CA" + "b" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}/Payments.json",
        json=_payment_payload(call_sid=call_sid),
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.calls.start_payment(call_sid, charge_amount="1.00", currency="USD")
    sent = httpx_mock.get_request()
    parsed = _form_body(sent.content)
    assert parsed == {"ChargeAmount": ["1.00"], "Currency": ["USD"]}


def test_calls_update_payment_status_complete(httpx_mock: HTTPXMock):
    call_sid = "CA" + "c" * 32
    payment_sid = "PY" + "1" * 32
    expected_path = (
        f"/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}/Payments/{payment_sid}.json"
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}{expected_path}",
        json=_payment_payload(payment_sid, call_sid),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        payment = c.calls.update_payment(call_sid, payment_sid, status="complete")
    assert payment.sid == payment_sid
    sent = httpx_mock.get_request()
    assert sent.url.path == expected_path
    parsed = _form_body(sent.content)
    assert parsed == {"Status": ["complete"]}


def test_calls_update_payment_capture_security_code(httpx_mock: HTTPXMock):
    call_sid = "CA" + "d" * 32
    payment_sid = "PY" + "2" * 32
    httpx_mock.add_response(
        method="POST",
        url=(
            f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}"
            f"/Payments/{payment_sid}.json"
        ),
        json=_payment_payload(payment_sid, call_sid),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.calls.update_payment(call_sid, payment_sid, capture="security-code")
    sent = httpx_mock.get_request()
    parsed = _form_body(sent.content)
    assert parsed == {"Capture": ["security-code"]}


def test_calls_update_payment_cancel(httpx_mock: HTTPXMock):
    call_sid = "CA" + "e" * 32
    payment_sid = "PY" + "3" * 32
    httpx_mock.add_response(
        method="POST",
        url=(
            f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}"
            f"/Payments/{payment_sid}.json"
        ),
        json=_payment_payload(payment_sid, call_sid),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.calls.update_payment(
            call_sid,
            payment_sid,
            status="cancel",
            idempotency_key="cancel-1",
        )
    sent = httpx_mock.get_request()
    parsed = _form_body(sent.content)
    assert parsed == {"Status": ["cancel"], "IdempotencyKey": ["cancel-1"]}


async def test_calls_start_payment_async(httpx_mock: HTTPXMock):
    call_sid = "CA" + "f" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}/Payments.json",
        json=_payment_payload(call_sid=call_sid),
        status_code=201,
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        payment = await c.calls.start_payment(
            call_sid, charge_amount="2.00", currency="USD"
        )
    assert payment.call_sid == call_sid


# --- Enum-literal hygiene -----------------------------------------------------


@pytest.mark.parametrize(
    "bank_type",
    ["consumer-checking", "consumer-savings", "commercial-checking"],
)
def test_start_payment_accepts_all_bank_account_types(
    httpx_mock: HTTPXMock, bank_type: PaymentBankAccountType
):
    """Every documented BankAccountType enum value must round-trip without rejection."""
    call_sid = "CA" + "0" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/Calls/{call_sid}/Payments.json",
        json=_payment_payload(call_sid=call_sid),
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.calls.start_payment(call_sid, bank_account_type=bank_type)
    sent = httpx_mock.get_request()
    parsed = _form_body(sent.content)
    assert parsed["BankAccountType"] == [bank_type]
