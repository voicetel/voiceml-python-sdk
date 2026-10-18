"""Media-stream resource (REST equivalent of `<Connect><Stream>` / `<Start><Stream>`)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request

StreamStatus = Literal["in-progress", "stopped"]
TrackSelector = Literal["inbound_track", "outbound_track", "both_tracks"]


class Stream(_Base):
    """A media stream started on a live call.

    ``api_version`` and ``date_created`` are deprecated: the server no longer emits
    them, so they are always ``None``.
    """

    sid: str | None = None
    account_sid: str | None = None
    call_sid: str | None = None
    name: str | None = None
    status: StreamStatus | str
    api_version: str | None = None
    uri: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class StartStreamRequest(_Request):
    """Body for ``POST /Calls/{sid}/Streams``. ``url`` is the wss:// endpoint."""

    url: str = Field(alias="Url")
    track: TrackSelector | None = Field(default=None, alias="Track")
    name: str | None = Field(default=None, alias="Name")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: str | None = Field(default=None, alias="StatusCallbackMethod")


class StopStreamRequest(_Request):
    status: Literal["stopped"] = Field(alias="Status")
