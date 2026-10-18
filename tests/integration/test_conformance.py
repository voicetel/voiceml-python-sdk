"""Response-shape conformance against the private fixture corpus.

SKIPPED (with a visible reason) unless ``VOICEML_CONFORMANCE_FIXTURES`` points at
a fixture corpus emitted by callBroadcast's ``cmd/twilio-conformance-fixtures``.
The harness loads each canonical response example from the corpus and validates
it against the matching Pydantic model. If validation fails, the SDK's model has
drifted from the documented shape — fix the SDK, not the fixture.

The public, always-on equivalent is ``tests/contract``: it validates every SDK
method against the vendored OpenAPI document.

Run:

.. code-block:: shell

   VOICEML_CONFORMANCE_FIXTURES=/path/to/callBroadcast/cmd/twilio-conformance-fixtures/fixtures \\
     pytest tests/integration/test_conformance.py -v
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from voiceml.models import (
    Account,
    Application,
    ApplicationList,
    Balance,
    Call,
    CallList,
    CallPayment,
    CallTranscription,
    Conference,
    ConferenceList,
    EventsList,
    IncomingPhoneNumber,
    IncomingPhoneNumberList,
    Media,
    MediaList,
    Message,
    MessageList,
    Notification,
    NotificationsList,
    OutgoingCallerId,
    OutgoingCallerIdList,
    Participant,
    ParticipantList,
    Queue,
    QueueList,
    QueueMember,
    QueueMemberList,
    Recording,
    RecordingList,
    RecordingTranscription,
    RecordingTranscriptionList,
    SipAuthMappingList,
    SipCredential,
    SipCredentialList,
    SipCredentialListList,
    SipCredentialListMappingList,
    SipCredentialListPage,
    SipDomain,
    SipDomainList,
    SipDomainMapping,
    SipIpAccessControlList,
    SipIpAccessControlListList,
    SipIpAccessControlListMappingList,
    SipIpAddress,
    SipIpAddressList,
    SiprecSession,
    Stream,
    ValidationRequest,
)


class _RawJsonObject(BaseModel):
    """Permissive container for resources the SDK does not model.

    Equivalent to the Go SDK conformance harness's ``map[string]any``
    target — confirms the wire payload is a valid JSON object and lets
    the harness still pluck ``sid`` / ``account_sid`` from the extras
    map for key-field assertions when present.
    """

    model_config = ConfigDict(extra="allow")


FIXTURES_ENV = "VOICEML_CONFORMANCE_FIXTURES"


def _index_path() -> Path | None:
    root = os.environ.get(FIXTURES_ENV)
    if not root:
        return None
    p = Path(root) / "index.json"
    if not p.exists():
        return None
    return p


def _load_entries() -> list[dict[str, Any]]:
    path = _index_path()
    if path is None:
        return []
    return json.loads(path.read_text())


_OP_TO_MODEL: dict[str, type[BaseModel]] = {
    "CreateCall": Call,
    "FetchCall": Call,
    "UpdateCall": Call,
    "ListCall": CallList,
    "FetchConference": Conference,
    "UpdateConference": Conference,
    "ListConference": ConferenceList,
    "CreateParticipant": Participant,
    "FetchParticipant": Participant,
    "UpdateParticipant": Participant,
    "ListParticipant": ParticipantList,
    "CreateQueue": Queue,
    "FetchQueue": Queue,
    "UpdateQueue": Queue,
    "ListQueue": QueueList,
    "FetchMember": QueueMember,
    "UpdateMember": QueueMember,
    "ListMember": QueueMemberList,
    "CreateApplication": Application,
    "FetchApplication": Application,
    "UpdateApplication": Application,
    "ListApplication": ApplicationList,
    "CreateCallRecording": Recording,
    "FetchCallRecording": Recording,
    "UpdateCallRecording": Recording,
    "FetchRecording": Recording,
    "FetchConferenceRecording": Recording,
    "UpdateConferenceRecording": Recording,
    "ListCallRecording": RecordingList,
    "ListRecording": RecordingList,
    "ListConferenceRecording": RecordingList,
    "CreateIncomingPhoneNumber": IncomingPhoneNumber,
    "CreateIncomingPhoneNumberLocal": IncomingPhoneNumber,
    "CreateIncomingPhoneNumberMobile": IncomingPhoneNumber,
    "CreateIncomingPhoneNumberTollFree": IncomingPhoneNumber,
    "FetchIncomingPhoneNumber": IncomingPhoneNumber,
    "UpdateIncomingPhoneNumber": IncomingPhoneNumber,
    "ListIncomingPhoneNumber": IncomingPhoneNumberList,
    "ListIncomingPhoneNumberLocal": IncomingPhoneNumberList,
    "ListIncomingPhoneNumberMobile": IncomingPhoneNumberList,
    "ListIncomingPhoneNumberTollFree": IncomingPhoneNumberList,
    "CreateStream": Stream,
    "UpdateStream": Stream,
    "CreateSiprec": SiprecSession,
    "UpdateSiprec": SiprecSession,
    "CreateRealtimeTranscription": CallTranscription,
    "UpdateRealtimeTranscription": CallTranscription,
    # Messages — Twilio-compatible /Messages REST surface modelled in this SDK.
    "CreateMessage": Message,
    "FetchMessage": Message,
    "UpdateMessage": Message,
    "ListMessage": MessageList,
    # Call diagnostics — Events + Notifications expose compat-stub list envelopes.
    "ListCallEvent": EventsList,
    "ListCallNotification": NotificationsList,
    "ListNotification": NotificationsList,
    # Payments — REST companion to the ``<Pay>`` TwiML verb.
    "CreatePayments": CallPayment,
    "UpdatePayments": CallPayment,
    # SIP Trunking — Domains / CredentialLists / IpAccessControlLists +
    # the four mapping namespaces (historical + Auth/Calls + Auth/Registrations).
    "CreateSipDomain": SipDomain,
    "FetchSipDomain": SipDomain,
    "UpdateSipDomain": SipDomain,
    "ListSipDomain": SipDomainList,
    "CreateSipCredentialList": SipCredentialList,
    "FetchSipCredentialList": SipCredentialList,
    "UpdateSipCredentialList": SipCredentialList,
    "ListSipCredentialList": SipCredentialListList,
    "CreateSipCredential": SipCredential,
    "FetchSipCredential": SipCredential,
    "UpdateSipCredential": SipCredential,
    "ListSipCredential": SipCredentialListPage,
    "CreateSipIpAccessControlList": SipIpAccessControlList,
    "FetchSipIpAccessControlList": SipIpAccessControlList,
    "UpdateSipIpAccessControlList": SipIpAccessControlList,
    "ListSipIpAccessControlList": SipIpAccessControlListList,
    "CreateSipIpAddress": SipIpAddress,
    "FetchSipIpAddress": SipIpAddress,
    "UpdateSipIpAddress": SipIpAddress,
    "ListSipIpAddress": SipIpAddressList,
    # Historical (no-Auth) mapping namespaces.
    "CreateSipCredentialListMapping": SipDomainMapping,
    "FetchSipCredentialListMapping": SipDomainMapping,
    "ListSipCredentialListMapping": SipCredentialListMappingList,
    "CreateSipIpAccessControlListMapping": SipDomainMapping,
    "FetchSipIpAccessControlListMapping": SipDomainMapping,
    "ListSipIpAccessControlListMapping": SipIpAccessControlListMappingList,
    # Modern Auth/Calls and Auth/Registrations mapping namespaces.
    "CreateSipAuthCallsCredentialListMapping": SipDomainMapping,
    "FetchSipAuthCallsCredentialListMapping": SipDomainMapping,
    "ListSipAuthCallsCredentialListMapping": SipAuthMappingList,
    "CreateSipAuthCallsIpAccessControlListMapping": SipDomainMapping,
    "FetchSipAuthCallsIpAccessControlListMapping": SipDomainMapping,
    "ListSipAuthCallsIpAccessControlListMapping": SipAuthMappingList,
    "CreateSipAuthRegistrationsCredentialListMapping": SipDomainMapping,
    "FetchSipAuthRegistrationsCredentialListMapping": SipDomainMapping,
    "ListSipAuthRegistrationsCredentialListMapping": SipAuthMappingList,
    "FetchAccount": Account,
    "UpdateAccount": Account,
    "FetchBalance": Balance,
    "FetchCallNotification": Notification,
    "FetchNotification": Notification,
    # UserDefinedMessages is a 501 stub on the server; validate the error body shape.
    "CreateUserDefinedMessage": _RawJsonObject,
    "FetchOutgoingCallerId": OutgoingCallerId,
    "ListOutgoingCallerId": OutgoingCallerIdList,
    "UpdateOutgoingCallerId": OutgoingCallerId,
    "CreateValidationRequest": ValidationRequest,
    "FetchMedia": Media,
    "ListMedia": MediaList,
    # Recording transcriptions (``TR…``) are distinct from the live CallTranscription
    # resource started with ``calls.start_transcription``.
    "FetchRecordingTranscription": RecordingTranscription,
    "ListRecordingTranscription": RecordingTranscriptionList,
    "FetchTranscription": RecordingTranscription,
    "ListTranscription": RecordingTranscriptionList,
}


pytestmark = pytest.mark.skipif(
    _index_path() is None,
    reason=(
        f"private conformance corpus not available: set {FIXTURES_ENV} to the "
        "callBroadcast cmd/twilio-conformance-fixtures/fixtures directory"
    ),
)


@pytest.mark.parametrize(
    "entry",
    _load_entries(),
    ids=lambda e: f"{e['resource']}/{e['operation_id']}/{e.get('example_name', '')}",
)
def test_fixture_decodes(entry: dict[str, Any]) -> None:
    op_id = entry["operation_id"]
    if op_id not in _OP_TO_MODEL:
        pytest.fail(
            f"no model mapped for operation {op_id} — extend _OP_TO_MODEL "
            "(use _RawJsonObject for compat surfaces the SDK does not model)"
        )
    model = _OP_TO_MODEL[op_id]

    root = Path(os.environ[FIXTURES_ENV])
    body = (root / entry["file"]).read_text()

    try:
        instance = model.model_validate_json(body)
    except ValidationError as exc:
        pytest.fail(f"{op_id} fixture failed pydantic validation: {exc}\nbody: {body[:400]}")

    # Per-model key-field assertions mirroring the Go harness's
    # assertKeyFields. Skipped for list envelopes (they only carry the
    # paginated container; the inner items can be empty).
    sid_attr = getattr(instance, "sid", None)
    account_sid_attr = getattr(instance, "account_sid", None)
    if sid_attr is not None:
        assert sid_attr, f"{op_id}: sid empty"
    if account_sid_attr is not None and not _is_list_envelope(instance):
        assert account_sid_attr, f"{op_id}: account_sid empty"


def _is_list_envelope(instance: BaseModel) -> bool:
    """True for the paginated *List envelopes — their sid/account_sid
    are envelope-level, not resource-level, and we don't enforce them."""
    return instance.__class__.__name__.endswith("List")
