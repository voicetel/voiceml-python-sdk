"""Exact wire format and host routing for the operations added in this release."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

import pytest

from ..contract import _harness as H

A = f"/2010-04-01/Accounts/{H.ACCOUNT_SID}"
DEFAULT = H.DEFAULT_HOST
MESSAGING = H.MESSAGING_HOST


def _usage_window(name: str) -> Callable[[Any], Any]:
    def call(client: Any) -> Any:
        return getattr(client.usage_records, f"list_{name}")(page_size=1)

    return call


# (id, call, method, host, raw path, raw query, raw body)
CASES: list[tuple[str, Callable[[Any], Any], str, str, str, bytes, bytes]] = [
    ("accounts.fetch", lambda c: c.accounts.fetch(), "GET", DEFAULT, f"{A}.json", b"", b""),
    (
        "accounts.update",
        lambda c: c.accounts.update(friendly_name="Ops", voice_method="POST"),
        "POST",
        DEFAULT,
        f"{A}.json",
        b"",
        b"FriendlyName=Ops&VoiceMethod=POST",
    ),
    ("balance.fetch", lambda c: c.balance.fetch(), "GET", DEFAULT, f"{A}/Balance.json", b"", b""),
    (
        "outgoing_caller_ids.list",
        lambda c: c.outgoing_caller_ids.list(phone_number="+14155550100", page_size=5),
        "GET",
        DEFAULT,
        f"{A}/OutgoingCallerIds.json",
        b"PhoneNumber=%2B14155550100&PageSize=5",
        b"",
    ),
    (
        "outgoing_caller_ids.create",
        lambda c: c.outgoing_caller_ids.create(phone_number="+14155550100", friendly_name="Desk"),
        "POST",
        DEFAULT,
        f"{A}/OutgoingCallerIds.json",
        b"",
        b"PhoneNumber=%2B14155550100&FriendlyName=Desk",
    ),
    (
        "outgoing_caller_ids.fetch",
        lambda c: c.outgoing_caller_ids.get("PN1"),
        "GET",
        DEFAULT,
        f"{A}/OutgoingCallerIds/PN1.json",
        b"",
        b"",
    ),
    (
        "outgoing_caller_ids.update",
        lambda c: c.outgoing_caller_ids.update("PN1", friendly_name="Desk 2"),
        "POST",
        DEFAULT,
        f"{A}/OutgoingCallerIds/PN1.json",
        b"",
        b"FriendlyName=Desk+2",
    ),
    (
        "outgoing_caller_ids.delete",
        lambda c: c.outgoing_caller_ids.delete("PN1"),
        "DELETE",
        DEFAULT,
        f"{A}/OutgoingCallerIds/PN1.json",
        b"",
        b"",
    ),
    (
        "media.list",
        lambda c: c.messages.list_media("SM1", date_created_gt="2026-07-01"),
        "GET",
        DEFAULT,
        f"{A}/Messages/SM1/Media.json",
        b"DateCreated%3E=2026-07-01",
        b"",
    ),
    (
        "media.fetch",
        lambda c: c.messages.get_media("SM1", "ME1"),
        "GET",
        DEFAULT,
        f"{A}/Messages/SM1/Media/ME1.json",
        b"",
        b"",
    ),
    (
        "media.delete",
        lambda c: c.messages.delete_media("SM1", "ME1"),
        "DELETE",
        DEFAULT,
        f"{A}/Messages/SM1/Media/ME1.json",
        b"",
        b"",
    ),
    ("exports.list", lambda c: c.exports.list(), "GET", DEFAULT, f"{A}/Exports.json", b"", b""),
    (
        "exports.download",
        lambda c: c.exports.download("2026-07-01"),
        "GET",
        DEFAULT,
        f"{A}/Exports/2026-07-01",
        b"",
        b"",
    ),
    (
        "transcriptions.listAccount",
        lambda c: c.transcriptions.list(page_size=10),
        "GET",
        DEFAULT,
        f"{A}/Transcriptions.json",
        b"PageSize=10",
        b"",
    ),
    (
        "transcription.fetch",
        lambda c: c.transcriptions.get("TR1"),
        "GET",
        DEFAULT,
        f"{A}/Transcriptions/TR1.json",
        b"",
        b"",
    ),
    (
        "transcription.delete",
        lambda c: c.transcriptions.delete("TR1"),
        "DELETE",
        DEFAULT,
        f"{A}/Transcriptions/TR1.json",
        b"",
        b"",
    ),
    (
        "recording.transcriptions.list",
        lambda c: c.recordings.list_transcriptions("RE1"),
        "GET",
        DEFAULT,
        f"{A}/Recordings/RE1/Transcriptions.json",
        b"",
        b"",
    ),
    (
        "recording.transcription.fetch",
        lambda c: c.recordings.get_transcription("RE1", "TR1"),
        "GET",
        DEFAULT,
        f"{A}/Recordings/RE1/Transcriptions/TR1.json",
        b"",
        b"",
    ),
    (
        "recording.transcription.delete",
        lambda c: c.recordings.delete_transcription("RE1", "TR1"),
        "DELETE",
        DEFAULT,
        f"{A}/Recordings/RE1/Transcriptions/TR1.json",
        b"",
        b"",
    ),
    (
        "conferenceRecordings.create",
        lambda c: c.conferences.start_recording("CF1"),
        "POST",
        DEFAULT,
        f"{A}/Conferences/CF1/Recordings.json",
        b"",
        b"",
    ),
    (
        "openapi.yaml",
        lambda c: c.diagnostics.openapi_yaml(),
        "GET",
        DEFAULT,
        "/openapi.yaml",
        b"",
        b"",
    ),
    (
        "openapi.yml",
        lambda c: c.diagnostics.openapi_yml(),
        "GET",
        DEFAULT,
        "/openapi.yml",
        b"",
        b"",
    ),
    (
        "usageRecords.list",
        lambda c: c.usage_records.list(category="calls", start_date=date(2026, 7, 1)),
        "GET",
        DEFAULT,
        f"{A}/Usage/Records.json",
        b"Category=calls&StartDate=2026-07-01",
        b"",
    ),
    *[
        (
            f"usageRecords.list{wire}",
            _usage_window(name),
            "GET",
            DEFAULT,
            f"{A}/Usage/Records/{wire}.json",
            b"PageSize=1",
            b"",
        )
        for name, wire in [
            ("all_time", "AllTime"),
            ("daily", "Daily"),
            ("last_month", "LastMonth"),
            ("monthly", "Monthly"),
            ("this_month", "ThisMonth"),
            ("today", "Today"),
            ("yearly", "Yearly"),
            ("yesterday", "Yesterday"),
        ]
    ],
    (
        "sip_registrations.list",
        lambda c: c.sip.registrations.list(page_size=20),
        "GET",
        DEFAULT,
        f"{A}/SIP/Registrations.json",
        b"PageSize=20",
        b"",
    ),
    (
        "messaging.v1.services.phoneNumbers.list",
        lambda c: c.messaging_v1.services.phone_numbers("MG1").list(page_size=5),
        "GET",
        MESSAGING,
        "/v1/Services/MG1/PhoneNumbers",
        b"PageSize=5",
        b"",
    ),
    (
        "messaging.v1.services.phoneNumbers.create",
        lambda c: c.messaging_v1.services.phone_numbers("MG1").create(phone_number_sid="PN1"),
        "POST",
        MESSAGING,
        "/v1/Services/MG1/PhoneNumbers",
        b"",
        b"PhoneNumberSid=PN1",
    ),
    (
        "messaging.v1.services.phoneNumbers.fetch",
        lambda c: c.messaging_v1.services.phone_numbers("MG1").fetch("PN1"),
        "GET",
        MESSAGING,
        "/v1/Services/MG1/PhoneNumbers/PN1",
        b"",
        b"",
    ),
    (
        "messaging.v1.services.phoneNumbers.delete",
        lambda c: c.messaging_v1.services.phone_numbers("MG1").delete("PN1"),
        "DELETE",
        MESSAGING,
        "/v1/Services/MG1/PhoneNumbers/PN1",
        b"",
        b"",
    ),
]


@pytest.mark.parametrize(
    ("op_id", "call", "method", "host", "raw_path", "query", "body"),
    CASES,
    ids=[c[0] for c in CASES],
)
def test_new_operation_wire_format(
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
    assert op is not None and op.op_id == op_id
    assert ("authorization" in sent.headers) is op.auth


def test_all_36_added_operations_are_listed() -> None:
    assert len(CASES) == 36
    assert len({c[0] for c in CASES}) == 36
