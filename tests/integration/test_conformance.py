"""Twilio response-shape conformance tests (#256 Phase C).

SKIPPED unless ``VOICEML_CONFORMANCE_FIXTURES`` points at a fixture corpus
emitted by callBroadcast's ``cmd/twilio-conformance-fixtures``. The harness
loads each canonical Twilio response example from the corpus and validates
it against the matching Pydantic model. If validation fails, the SDK's
model has drifted from Twilio's documented shape — fix the SDK, not the
fixture.

Mirrors the Go SDK's ``conformance_test.go`` (voiceml-go-sdk@d6ac75c):
same fixture set, same operation-id → model mapping. The Go SDK passes
132/132; this harness should track the same denominator (modulo SDK
feature gaps — e.g. Messages isn't yet in this SDK, so those fixtures
are skipped rather than failed).

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
    Application,
    ApplicationList,
    Call,
    CallList,
    CallPayment,
    CallTranscription,
    Conference,
    ConferenceList,
    EventsList,
    IncomingPhoneNumber,
    IncomingPhoneNumberList,
    Message,
    MessageList,
    NotificationsList,
    Participant,
    ParticipantList,
    Queue,
    QueueList,
    QueueMember,
    QueueMemberList,
    Recording,
    RecordingList,
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
    # Compat surfaces the SDK does not field-model — validate as raw JSON
    # objects so the wire shape is at least confirmed valid, matching the
    # Go SDK's ``map[string]any`` posture for these operations.
    "FetchAccount": _RawJsonObject,
    "UpdateAccount": _RawJsonObject,
    "FetchBalance": _RawJsonObject,
    "FetchCallNotification": _RawJsonObject,
    "FetchNotification": _RawJsonObject,
    "CreateUserDefinedMessage": _RawJsonObject,
    "FetchOutgoingCallerId": _RawJsonObject,
    "ListOutgoingCallerId": _RawJsonObject,
    "UpdateOutgoingCallerId": _RawJsonObject,
    "CreateValidationRequest": _RawJsonObject,
    "FetchMedia": _RawJsonObject,
    "ListMedia": _RawJsonObject,
    # Recording-side transcriptions are a distinct resource from the live
    # CallTranscription (REST companion to ``<Start><Transcription>``)
    # the SDK exposes; the recording-transcription wire shape carries
    # ``duration``, ``transcription_text``, ``type`` and friends.
    "FetchRecordingTranscription": _RawJsonObject,
    "ListRecordingTranscription": _RawJsonObject,
    "FetchTranscription": _RawJsonObject,
    "ListTranscription": _RawJsonObject,
}


pytestmark = pytest.mark.skipif(
    _index_path() is None,
    reason=f"{FIXTURES_ENV} not set or fixture index missing",
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
