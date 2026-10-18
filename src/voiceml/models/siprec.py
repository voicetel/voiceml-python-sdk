"""SIPREC-session resource (REST equivalent of `<Start><Siprec>`)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request

SiprecStatus = Literal["in-progress", "stopped"]
TrackSelector = Literal["inbound_track", "outbound_track", "both_tracks"]


class SiprecSession(_Base):
    """A SIPREC session started on a live call.

    ``connector_name``, ``api_version`` and ``date_created`` are deprecated: the server
    no longer emits them, so they are always ``None``.
    """

    sid: str | None = None
    account_sid: str | None = None
    call_sid: str | None = None
    name: str | None = None
    connector_name: str | None = None
    status: SiprecStatus | str
    api_version: str | None = None
    uri: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class StartSiprecRequest(_Request):
    """Body for ``POST /Calls/{sid}/Siprec``."""

    name: str | None = Field(default=None, alias="Name")
    connector_name: str | None = Field(default=None, alias="ConnectorName")
    track: TrackSelector | None = Field(default=None, alias="Track")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: str | None = Field(default=None, alias="StatusCallbackMethod")


class StopSiprecRequest(_Request):
    """Body for ``POST /Calls/{sid}/Siprec/{sid}``.

    Clears VoiceML's session tracking only — the SRS recording itself continues until
    call hangup (documented mod_siprec limitation).
    """

    status: Literal["stopped"] = Field(alias="Status")
