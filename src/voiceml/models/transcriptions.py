"""Real-time call-transcription resource (REST equivalent of `<Start><Transcription>`)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request
from .common import Page

TranscriptionStatus = Literal["in-progress", "stopped"]
TranscriptionEngine = Literal["deepgram", "google", "aws", "azure"]
TrackSelector = Literal["inbound_track", "outbound_track", "both_tracks"]


class CallTranscription(_Base):
    """Live per-call transcription. Events stream via StatusCallback.

    ``language_code``, ``transcription_engine``, ``api_version`` and ``date_created``
    are deprecated: the server no longer emits them, so they are always ``None``.
    """

    sid: str | None = None
    account_sid: str | None = None
    call_sid: str | None = None
    name: str | None = None
    language_code: str | None = None
    transcription_engine: TranscriptionEngine | None = None
    status: TranscriptionStatus | str
    api_version: str | None = None
    uri: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


RecordingTranscriptionStatus = Literal["in-progress", "completed", "failed"]


class RecordingTranscription(_Base):
    """A transcription of a stored recording (``TR…``), as listed under
    ``/Transcriptions`` and ``/Recordings/{RecordingSid}/Transcriptions``."""

    sid: str | None = None
    account_sid: str | None = None
    status: RecordingTranscriptionStatus | str | None = None
    recording_sid: str | None = None
    duration: str | None = None
    transcription_text: str | None = None
    type: str | None = None
    price: str | None = None
    price_unit: str | None = None
    api_version: str | None = None
    uri: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class RecordingTranscriptionList(Page[RecordingTranscription]):
    transcriptions: list[RecordingTranscription] = Field(default_factory=list)


class StartTranscriptionRequest(_Request):
    """Body for ``POST /Calls/{sid}/Transcriptions``."""

    name: str | None = Field(default=None, alias="Name")
    track: TrackSelector | None = Field(default=None, alias="Track")
    language_code: str | None = Field(default=None, alias="LanguageCode")
    transcription_engine: TranscriptionEngine | None = Field(
        default=None, alias="TranscriptionEngine"
    )
    profanity_filter: bool | None = Field(default=None, alias="ProfanityFilter")
    partial_results: bool | None = Field(default=None, alias="PartialResults")
    hints: str | None = Field(default=None, alias="Hints")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: str | None = Field(default=None, alias="StatusCallbackMethod")
    status_callback_events: str | None = Field(default=None, alias="StatusCallbackEvents")


class StopTranscriptionRequest(_Request):
    status: Literal["stopped"] = Field(alias="Status")
