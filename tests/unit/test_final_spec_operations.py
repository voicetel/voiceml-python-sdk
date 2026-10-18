"""Exact wire format, host routing and redaction for the four final-spec operations."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

import pytest

from voiceml.models import AccountWithKey, MonitorV1Alert

from ..contract import _harness as H

A = f"/2010-04-01/Accounts/{H.ACCOUNT_SID}"
DEFAULT = H.DEFAULT_HOST

SECRET = "sk-rotated-0123456789abcdef"

# (id, call, method, host, raw path, raw query, raw body)
CASES: list[tuple[str, Callable[[Any], Any], str, str, str, bytes, bytes]] = [
    (
        "monitor.v1.alerts.list",
        lambda c: c.monitor_v1.alerts.list(
            log_level="error", start_date="2026-10-01", end_date="2026-10-02", page_size=50
        ),
        "GET",
        DEFAULT,
        "/v1/Alerts",
        b"LogLevel=error&StartDate=2026-10-01&EndDate=2026-10-02&PageSize=50",
        b"",
    ),
    (
        "monitor.v1.alerts.list-minimal",
        lambda c: c.monitor_v1.alerts.list(),
        "GET",
        DEFAULT,
        "/v1/Alerts",
        b"",
        b"",
    ),
    (
        "monitor.v1.alerts.fetch",
        lambda c: c.monitor_v1.alerts.fetch("NO00000000000000000000000000000000aa"),
        "GET",
        DEFAULT,
        "/v1/Alerts/NO00000000000000000000000000000000aa",
        b"",
        b"",
    ),
    (
        "messages.feedback.create",
        lambda c: c.messages.create_feedback(
            "SM00000000000000000000000000000000aa", outcome="confirmed"
        ),
        "POST",
        DEFAULT,
        f"{A}/Messages/SM00000000000000000000000000000000aa/Feedback.json",
        b"",
        b"Outcome=confirmed",
    ),
    (
        "messages.feedback.create-no-outcome",
        lambda c: c.messages.create_feedback("SM00000000000000000000000000000000aa"),
        "POST",
        DEFAULT,
        f"{A}/Messages/SM00000000000000000000000000000000aa/Feedback.json",
        b"",
        b"",
    ),
    (
        "accounts.rotateKey",
        lambda c: c.accounts.rotate_key(),
        "POST",
        DEFAULT,
        f"{A}/RotateKey.json",
        b"",
        b"",
    ),
]


@pytest.mark.parametrize(
    ("op_id", "call", "method", "host", "raw_path", "query", "body"),
    CASES,
    ids=[c[0] for c in CASES],
)
def test_final_spec_operation_wire_format(
    op_id: str,
    call: Callable[[Any], Any],
    method: str,
    host: str,
    raw_path: str,
    query: bytes,
    body: bytes,
) -> None:
    recorder = H.Recorder()
    client, _ = H.make_clients(recorder)
    call(client)
    assert len(recorder.requests) == 1
    sent = recorder.requests[0]
    assert sent.method == method
    assert sent.url.host == host
    assert sent.url.raw_path.split(b"?")[0] == raw_path.encode()
    assert sent.url.query == query
    assert sent.content == body
    op = H.match_op(method, raw_path)
    assert op is not None and op.op_id == op_id.split("-")[0]
    assert ("authorization" in sent.headers) is op.auth


@pytest.mark.parametrize("which", ["sync", "async"])
def test_monitor_alerts_iter_is_lazy_and_terminates(which: str) -> None:
    """The alerts envelope is a single page today; iter() must stop after it."""
    recorder = H.Recorder()
    client, aclient = H.make_clients(recorder)
    if which == "sync":
        alerts = list(client.monitor_v1.alerts.iter(log_level="warning"))
        assert len(recorder.requests) == 1
        assert recorder.requests[0].url.query == b"LogLevel=warning"
        assert alerts  # synthesized page carries one row
    else:

        async def run() -> list[object]:
            return [a async for a in aclient.monitor_v1.alerts.iter()]

        asyncio.run(run())
        assert len(recorder.requests) == 1


def test_monitor_alerts_next_page_is_none_on_single_page() -> None:
    recorder = H.Recorder()
    client, _ = H.make_clients(recorder)
    page = client.monitor_v1.alerts.list()
    assert client.monitor_v1.alerts.next_page(page) is None


def test_rotated_api_key_is_hidden_from_repr() -> None:
    account = AccountWithKey.model_validate(
        {
            "sid": H.ACCOUNT_SID,
            "api_key": SECRET,
            "sip_username": "sip-user",
            "phone_regions": ["US"],
            "allow_cidr": [],
            "disabled": False,
            "stt_http_token_set": False,
            "tts_http_token_set": False,
            "stripe_secret_key_set": False,
            "pay_enabled": False,
            "sms_allowed_providers": [],
            "stt_allowed_providers": [],
            "aws_secret_access_key_set": False,
            "created_at": "2026-10-18T00:00:00Z",
            "updated_at": "2026-10-18T00:00:00Z",
        }
    )
    assert account.api_key == SECRET
    assert SECRET not in repr(account)
    assert SECRET not in str(account)


def test_monitor_alert_model_tolerates_unknown_enum_and_missing_detail() -> None:
    alert = MonitorV1Alert.model_validate(
        {
            "sid": "NO00000000000000000000000000000000aa",
            "account_sid": H.ACCOUNT_SID,
            "alert_text": "boom",
            "error_code": "11200",
            "log_level": "zz-new-value",
            "more_info": "https://example.com/errors/11200",
            "request_method": "POST",
            "request_url": "https://voiceml.voicetel.com/v1/Messages",
            "url": "/v1/Alerts/NO00000000000000000000000000000000aa",
            "date_created": "2026-10-18T00:00:00Z",
            "date_generated": "2026-10-18T00:00:00Z",
            "date_updated": "2026-10-18T00:00:00Z",
        }
    )
    assert alert.log_level == "zz-new-value"
    assert alert.request_headers is None
