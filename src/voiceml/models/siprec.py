"""SIPREC-session resource (REST equivalent of `<Start><Siprec>`)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import Page

SiprecStatus = Literal["in-progress", "stopped"]
TrackSelector = Literal["inbound_track", "outbound_track", "both_tracks"]


class SiprecSession(_Base):
    sid: str
    account_sid: str
    call_sid: str
    name: str | None = None
    connector_name: str | None = None
    status: SiprecStatus
    api_version: str | None = None
    uri: str
    date_created: str | None = None
    date_updated: str | None = None


class SiprecList(Page[SiprecSession]):
    siprec: list[SiprecSession] = Field(default_factory=list)


class StartSiprecRequest(_Base):
    """Body for ``POST /Calls/{sid}/Siprec``."""

    name: str | None = Field(default=None, alias="Name")
    connector_name: str | None = Field(default=None, alias="ConnectorName")
    track: TrackSelector | None = Field(default=None, alias="Track")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: str | None = Field(default=None, alias="StatusCallbackMethod")


class StopSiprecRequest(_Base):
    """Body for ``POST /Calls/{sid}/Siprec/{sid}``.

    Clears VoiceML's session tracking only — the SRS recording itself continues until
    call hangup (documented mod_siprec limitation).
    """

    status: Literal["stopped"] = Field(alias="Status")
