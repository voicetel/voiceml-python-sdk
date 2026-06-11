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
from pydantic import BaseModel, ValidationError

from voiceml.models import (
    Application,
    ApplicationList,
    Call,
    CallList,
    Conference,
    ConferenceList,
    IncomingPhoneNumber,
    IncomingPhoneNumberList,
    Participant,
    ParticipantList,
    Queue,
    QueueList,
    QueueMember,
    QueueMemberList,
    Recording,
    RecordingList,
    SiprecSession,
    Stream,
)

# CallTranscription lives on the calls module; importable via the models surface.
try:
    from voiceml.models import CallTranscription  # noqa: F401  (re-exported alias)
except ImportError:
    CallTranscription = None  # type: ignore[assignment,misc]


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


_OP_TO_MODEL: dict[str, type[BaseModel] | None] = {
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
    # Compat stubs / unmodelled — the Go SDK uses raw map[string]any;
    # in Python we just skip rather than test a permissive container.
    "ListCallEvent": None,
    "ListCallNotification": None,
    "FetchCallNotification": None,
    "ListNotification": None,
    "FetchNotification": None,
    "CreateUserDefinedMessage": None,
    # Messages — not yet modelled in this SDK.
    "CreateMessage": None,
    "FetchMessage": None,
    "ListMessage": None,
    "UpdateMessage": None,
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
    model = _OP_TO_MODEL.get(op_id)
    if model is None:
        pytest.skip(f"no model mapped for operation {op_id}")

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
