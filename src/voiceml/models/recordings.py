"""Recording resource — both call-scoped and account-scoped lists."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request
from .calls import RecordingStatusCallbackEvent
from .common import Page

RecordingStatus = Literal[
    "in-progress", "paused", "stopped", "processing", "completed", "absent", "deleted"
]
RecordingSource = Literal[
    "OutboundAPI",
    "RecordVerb",
    "DialVerb",
    "Conference",
    "Trunking",
    "StartCallRecordingAPI",
    "StartConferenceRecordingAPI",
]
RecordingUpdateStatus = Literal["stopped", "paused", "in-progress"]


class Recording(_Base):
    sid: str | None = None
    account_sid: str | None = None
    call_sid: str | None = None
    conference_sid: str | None = None
    status: RecordingStatus | str
    source: RecordingSource | str | None = None
    channels: int | None = None
    duration: str | None = None
    track: str | None = None
    api_version: str | None = None
    uri: str | None = None
    media_url: str | None = None
    error_code: int | None = None
    date_created: str | None = None
    date_updated: str | None = None
    start_time: str | None = None
    price: str | None = None
    price_unit: str | None = None
    encryption_details: dict[str, object] | None = None
    subresource_uris: dict[str, object] | None = None


class RecordingList(Page[Recording]):
    """Recordings list response (account-, call- and conference-scoped)."""

    recordings: list[Recording] = Field(default_factory=list)


class StartRecordingRequest(_Request):
    """Body for ``POST /Calls/{sid}/Recordings``."""

    recording_max_duration: int | None = Field(default=None, alias="RecordingMaxDuration")
    recording_channels: Literal["mono", "dual"] | None = Field(
        default=None, alias="RecordingChannels"
    )
    recording_track: Literal["inbound", "outbound", "both"] | None = Field(
        default=None, alias="RecordingTrack"
    )
    play_beep: bool | None = Field(default=None, alias="PlayBeep")
    recording_status_callback: str | None = Field(default=None, alias="RecordingStatusCallback")
    recording_status_callback_method: str | None = Field(
        default=None, alias="RecordingStatusCallbackMethod"
    )
    recording_status_callback_event: list[RecordingStatusCallbackEvent] | None = Field(
        default=None, alias="RecordingStatusCallbackEvent"
    )


class UpdateRecordingRequest(_Request):
    """Body for ``POST /Calls/{sid}/Recordings/{rsid}`` — stop / pause / resume.

    ``pause_behavior`` applies with ``status="paused"``: ``"skip"`` leaves the paused
    span out of the recording, ``"silence"`` (the server default) keeps it as silence.
    Conference recordings accept ``status`` only.
    """

    status: RecordingUpdateStatus = Field(alias="Status")
    pause_behavior: str | None = Field(default=None, alias="PauseBehavior")


class UpdateConferenceRecordingRequest(_Request):
    """Body for ``POST /Conferences/{sid}/Recordings/{rsid}`` — stop / pause / resume."""

    status: RecordingUpdateStatus = Field(alias="Status")


class StartConferenceRecordingRequest(_Request):
    """Body for ``POST /Conferences/{sid}/Recordings`` — start recording a conference.

    ``recording_status_callback_event`` takes ``in-progress`` / ``completed`` /
    ``absent``, one value per repeated key.
    """

    recording_status_callback: str | None = Field(default=None, alias="RecordingStatusCallback")
    recording_status_callback_method: str | None = Field(
        default=None, alias="RecordingStatusCallbackMethod"
    )
    recording_status_callback_event: list[RecordingStatusCallbackEvent] | None = Field(
        default=None, alias="RecordingStatusCallbackEvent"
    )


class RecordingAudio(_Base):
    """Result of fetching ``GET /Recordings/{sid}.wav``.

    ``content`` is the WAV bytes (after following any S3 redirect). ``content_type`` is
    whatever the server (or S3) declared — typically ``audio/wav`` but pass through what
    we got rather than assuming. ``via_redirect`` is ``True`` when the server answered
    with a redirect (archived audio) that the SDK followed.
    """

    sid: str
    content: bytes
    content_type: str
    via_redirect: bool

    def __repr__(self) -> str:
        return (
            f"RecordingAudio(sid={self.sid!r}, content_type={self.content_type!r}, "
            f"bytes={len(self.content)}, via_redirect={self.via_redirect})"
        )
