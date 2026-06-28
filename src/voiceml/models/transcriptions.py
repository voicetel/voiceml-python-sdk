"""Real-time call-transcription resource (REST equivalent of `<Start><Transcription>`)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import Page

TranscriptionStatus = Literal["in-progress", "stopped"]
TranscriptionEngine = Literal["deepgram", "google", "aws", "azure"]
TrackSelector = Literal["inbound_track", "outbound_track", "both_tracks"]


class CallTranscription(_Base):
    """Live per-call transcription. Events stream via StatusCallback."""

    sid: str
    account_sid: str
    call_sid: str
    name: str | None = None
    language_code: str | None = None
    transcription_engine: TranscriptionEngine | None = None
    status: TranscriptionStatus
    api_version: str | None = None
    uri: str
    date_created: str | None = None
    date_updated: str | None = None


class TranscriptionList(Page[CallTranscription]):
    transcriptions: list[CallTranscription] = Field(default_factory=list)


class StartTranscriptionRequest(_Base):
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


class StopTranscriptionRequest(_Base):
    status: Literal["stopped"] = Field(alias="Status")
