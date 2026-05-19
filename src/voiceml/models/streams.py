"""Media-stream resource (REST equivalent of `<Connect><Stream>` / `<Start><Stream>`)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import Page

StreamStatus = Literal["in-progress", "stopped"]
TrackSelector = Literal["inbound_track", "outbound_track", "both_tracks"]


class Stream(_Base):
    sid: str
    account_sid: str
    call_sid: str
    name: str | None = None
    status: StreamStatus
    api_version: str
    uri: str
    date_created: str | None = None
    date_updated: str | None = None


class StreamList(Page[Stream]):
    streams: list[Stream] = Field(default_factory=list)


class StartStreamRequest(_Base):
    """Body for ``POST /Calls/{sid}/Streams``. ``url`` is the wss:// endpoint."""

    url: str = Field(alias="Url")
    track: TrackSelector | None = Field(default=None, alias="Track")
    name: str | None = Field(default=None, alias="Name")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: str | None = Field(default=None, alias="StatusCallbackMethod")


class StopStreamRequest(_Base):
    status: Literal["stopped"] = Field(alias="Status")
