"""Recording resource — both call-scoped and account-scoped lists."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base

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
]
RecordingUpdateStatus = Literal["stopped", "paused", "in-progress"]


class Recording(_Base):
    sid: str
    account_sid: str
    call_sid: str
    conference_sid: str | None = None
    status: RecordingStatus
    source: RecordingSource | None = None
    channels: int | None = None
    duration: str | None = None
    api_version: str | None = None
    uri: str | None = None
    media_url: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    start_time: str | None = None
    price: str | None = None
    price_unit: str | None = None
    encryption_details: dict[str, object] | None = None
    subresource_uris: dict[str, object] | None = None


class RecordingList(_Base):
    """Recordings list response.

    The account-scoped endpoint (``GET /Recordings``) returns the canonical Twilio fields
    (``recordings/page/page_size/total``). Per-call (``GET /Calls/{sid}/Recordings``) and
    per-conference (``GET /Conferences/{sid}/Recordings``) endpoints currently return only
    ``recordings`` — the other pagination fields will be ``None``.
    """

    recordings: list[Recording] = Field(default_factory=list)
    page: int | None = None
    page_size: int | None = None
    total: int | None = None
    num_pages: int | None = None
    first_page_uri: str | None = None
    next_page_uri: str | None = None
    previous_page_uri: str | None = None
    uri: str | None = None


class StartRecordingRequest(_Base):
    """Body for ``POST /Calls/{sid}/Recordings``."""

    recording_max_duration: int | None = Field(default=None, alias="RecordingMaxDuration")
    recording_channels: Literal["mono", "dual"] | None = Field(
        default=None, alias="RecordingChannels"
    )
    play_beep: bool | None = Field(default=None, alias="PlayBeep")
    recording_status_callback: str | None = Field(default=None, alias="RecordingStatusCallback")
    recording_status_callback_method: str | None = Field(
        default=None, alias="RecordingStatusCallbackMethod"
    )
    recording_status_callback_event: str | None = Field(
        default=None, alias="RecordingStatusCallbackEvent"
    )


class UpdateRecordingRequest(_Base):
    """Body for ``POST /Calls/{sid}/Recordings/{rsid}`` — stop / pause / resume."""

    status: RecordingUpdateStatus = Field(alias="Status")


class RecordingAudio(_Base):
    """Result of fetching ``GET /Recordings/{sid}.wav``.

    ``content`` is the WAV bytes (after following any S3 redirect). ``content_type`` is
    whatever the server (or S3) declared — typically ``audio/wav`` but pass through what
    we got rather than assuming.
    """

    sid: str
    content: bytes
    content_type: str
    via_redirect: bool
