"""Public model surface — every request and response shape exposed by the SDK.

Naming follows the OpenAPI spec, with form-encoded request fields modelled in
PascalCase (matching the wire) via Pydantic ``alias=…``. Response fields stay
snake_case (also matching the wire). Call ``.to_form()`` on any request model
to produce the dict the transport sends.
"""

from __future__ import annotations

from .applications import (
    Application,
    ApplicationList,
    CreateApplicationRequest,
    UpdateApplicationRequest,
)
from .calls import (
    AnsweredBy,
    Call,
    CallDirection,
    CallList,
    CallStatus,
    CallStatusCallbackEvent,
    CreateCallRequest,
    HttpMethod,
    MachineDetectionMode,
    RecordingChannelsLayout,
    RecordingTrack,
    TrimMode,
    UpdateCallRequest,
    UpdateCallStatus,
)
from .common import ErrorBody, HealthFailure, Page
from .conferences import (
    Conference,
    ConferenceList,
    ConferenceStatus,
    CreateParticipantRequest,
    EndConferenceRequest,
    Participant,
    ParticipantList,
    ParticipantStatus,
    UpdateParticipantRequest,
)
from .diagnostics import EventsList, HealthStatus, NotificationsList
from .incoming_phone_numbers import (
    CreateIncomingPhoneNumberRequest,
    IncomingPhoneNumber,
    IncomingPhoneNumberCapabilities,
    IncomingPhoneNumberList,
    UpdateIncomingPhoneNumberRequest,
)
from .queues import (
    CreateQueueRequest,
    DequeueRequest,
    Queue,
    QueueList,
    QueueMember,
    QueueMemberList,
    UpdateQueueRequest,
)
from .recordings import (
    Recording,
    RecordingAudio,
    RecordingList,
    RecordingSource,
    RecordingStatus,
    RecordingUpdateStatus,
    StartRecordingRequest,
    UpdateRecordingRequest,
)
from .siprec import (
    SiprecList,
    SiprecSession,
    SiprecStatus,
    StartSiprecRequest,
    StopSiprecRequest,
)
from .streams import StartStreamRequest, StopStreamRequest, Stream, StreamList, StreamStatus
from .transcriptions import (
    CallTranscription,
    StartTranscriptionRequest,
    StopTranscriptionRequest,
    TranscriptionEngine,
    TranscriptionList,
    TranscriptionStatus,
)

__all__ = [
    "AnsweredBy",
    "Application",
    "ApplicationList",
    "Call",
    "CallDirection",
    "CallList",
    "CallStatus",
    "CallStatusCallbackEvent",
    "CallTranscription",
    "Conference",
    "ConferenceList",
    "ConferenceStatus",
    "CreateApplicationRequest",
    "CreateCallRequest",
    "CreateIncomingPhoneNumberRequest",
    "CreateParticipantRequest",
    "CreateQueueRequest",
    "DequeueRequest",
    "EndConferenceRequest",
    "ErrorBody",
    "EventsList",
    "HealthFailure",
    "HealthStatus",
    "HttpMethod",
    "IncomingPhoneNumber",
    "IncomingPhoneNumberCapabilities",
    "IncomingPhoneNumberList",
    "MachineDetectionMode",
    "NotificationsList",
    "Page",
    "Participant",
    "ParticipantList",
    "ParticipantStatus",
    "Queue",
    "QueueList",
    "QueueMember",
    "QueueMemberList",
    "Recording",
    "RecordingAudio",
    "RecordingChannelsLayout",
    "RecordingList",
    "RecordingSource",
    "RecordingStatus",
    "RecordingTrack",
    "RecordingUpdateStatus",
    "SiprecList",
    "SiprecSession",
    "SiprecStatus",
    "StartRecordingRequest",
    "StartSiprecRequest",
    "StartStreamRequest",
    "StartTranscriptionRequest",
    "StopSiprecRequest",
    "StopStreamRequest",
    "StopTranscriptionRequest",
    "Stream",
    "StreamList",
    "StreamStatus",
    "TranscriptionEngine",
    "TranscriptionList",
    "TranscriptionStatus",
    "TrimMode",
    "UpdateApplicationRequest",
    "UpdateCallRequest",
    "UpdateCallStatus",
    "UpdateIncomingPhoneNumberRequest",
    "UpdateParticipantRequest",
    "UpdateQueueRequest",
    "UpdateRecordingRequest",
]
