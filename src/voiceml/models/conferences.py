"""Conference + participant resources."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request
from .calls import CallStatusCallbackEvent
from .common import Page

ConferenceStatus = Literal["init", "in-progress", "completed"]
ParticipantStatus = Literal[
    "queued",
    "connecting",
    "ringing",
    "connected",
    "on-hold",
    "complete",
    "failed",
    "completed",
]


class Conference(_Base):
    sid: str | None = None
    account_sid: str | None = None
    friendly_name: str | None = None
    status: ConferenceStatus | str
    region: str | None = None
    api_version: str | None = None
    uri: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    reason_conference_ended: str | None = None
    call_sid_ending_conference: str | None = None
    subresource_uris: dict[str, str] | None = None
    member_count: int | None = None


class ConferenceList(Page[Conference]):
    conferences: list[Conference] = Field(default_factory=list)


class Participant(_Base):
    """A conference participant. ``api_version`` is deprecated (no longer emitted)."""

    call_sid: str | None = None
    conference_sid: str | None = None
    account_sid: str | None = None
    muted: bool | None = None
    hold: bool | None = None
    coaching: bool | None = None
    call_sid_to_coach: str | None = None
    queue_time: str | None = None
    start_conference_on_enter: bool | None = None
    end_conference_on_exit: bool | None = None
    status: ParticipantStatus | str
    label: str | None = None
    api_version: str | None = None
    uri: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class ParticipantList(Page[Participant]):
    participants: list[Participant] = Field(default_factory=list)


class EndConferenceRequest(_Request):
    """v1 supports only ``Status=completed``."""

    status: Literal["completed"] = Field(alias="Status")


class UpdateParticipantRequest(_Request):
    """At least one of ``muted`` / ``hold`` must be set."""

    muted: bool | None = Field(default=None, alias="Muted")
    hold: bool | None = Field(default=None, alias="Hold")


class CreateParticipantRequest(_Request):
    """``POST /Conferences/{sid}/Participants`` — ``From`` and ``To`` are required."""

    from_: str = Field(alias="From")
    to: str = Field(alias="To")
    label: str | None = Field(default=None, alias="Label")
    muted: bool | None = Field(default=None, alias="Muted")
    start_conference_on_enter: bool | None = Field(default=None, alias="StartConferenceOnEnter")
    end_conference_on_exit: bool | None = Field(default=None, alias="EndConferenceOnExit")
    timeout: int | None = Field(default=None, alias="Timeout")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: Literal["GET", "POST"] | None = Field(
        default=None, alias="StatusCallbackMethod"
    )
    status_callback_event: list[CallStatusCallbackEvent] | None = Field(
        default=None, alias="StatusCallbackEvent"
    )
    conference_status_callback: str | None = Field(default=None, alias="ConferenceStatusCallback")
    conference_status_callback_method: Literal["GET", "POST"] | None = Field(
        default=None, alias="ConferenceStatusCallbackMethod"
    )
    conference_status_callback_event: str | None = Field(
        default=None, alias="ConferenceStatusCallbackEvent"
    )
