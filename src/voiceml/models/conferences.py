"""Conference + participant resources."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import Page

ConferenceStatus = Literal["in-progress", "completed"]
ParticipantStatus = Literal[
    "queued", "connecting", "ringing", "connected", "on-hold", "completed"
]


class Conference(_Base):
    sid: str
    account_sid: str
    friendly_name: str
    status: ConferenceStatus
    region: str | None = None
    api_version: str
    uri: str
    date_created: str | None = None
    date_updated: str | None = None
    reason_conference_ended: str | None = None
    call_sid_ending_conference: str | None = None
    subresource_uris: dict[str, str] | None = None
    member_count: int | None = None


class ConferenceList(Page[Conference]):
    conferences: list[Conference] = Field(default_factory=list)


class Participant(_Base):
    call_sid: str
    conference_sid: str
    account_sid: str
    muted: bool
    hold: bool
    start_conference_on_enter: bool
    end_conference_on_exit: bool
    status: ParticipantStatus
    label: str | None = None
    api_version: str
    uri: str
    date_created: str | None = None
    date_updated: str | None = None


class ParticipantList(Page[Participant]):
    participants: list[Participant] = Field(default_factory=list)


class EndConferenceRequest(_Base):
    """v1 supports only ``Status=completed``."""

    status: Literal["completed"] = Field(alias="Status")


class UpdateParticipantRequest(_Base):
    """At least one of ``muted`` / ``hold`` must be set."""

    muted: bool | None = Field(default=None, alias="Muted")
    hold: bool | None = Field(default=None, alias="Hold")
