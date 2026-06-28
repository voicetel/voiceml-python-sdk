"""Application resource — persistent TwiML+callback bundles dispatched by `<Dial><Application>`."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import Page

HttpMethod = Literal["GET", "POST"]


class Application(_Base):
    sid: str
    account_sid: str
    friendly_name: str
    api_version: str
    voice_url: str | None = None
    voice_method: HttpMethod | None = None
    voice_fallback_url: str | None = None
    voice_fallback_method: HttpMethod | None = None
    voice_caller_id_lookup: bool
    status_callback: str | None = None
    status_callback_method: HttpMethod | None = None
    status_callback_event: str | None = None
    date_created: str
    date_updated: str
    uri: str


class ApplicationList(Page[Application]):
    applications: list[Application] = Field(default_factory=list)


class _ApplicationBody(_Base):
    """Shared form fields for create + update."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: HttpMethod | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: HttpMethod | None = Field(default=None, alias="VoiceFallbackMethod")
    voice_caller_id_lookup: bool | None = Field(default=None, alias="VoiceCallerIdLookup")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: HttpMethod | None = Field(default=None, alias="StatusCallbackMethod")
    status_callback_event: str | None = Field(default=None, alias="StatusCallbackEvent")


class CreateApplicationRequest(_ApplicationBody):
    """Body for ``POST /Applications``. All fields optional per spec."""


class UpdateApplicationRequest(_ApplicationBody):
    """Body for ``POST /Applications/{sid}``. Partial — only set fields are touched."""
