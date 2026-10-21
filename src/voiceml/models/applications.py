"""Application resource — persistent TwiML+callback bundles dispatched by `<Dial><Application>`."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request
from .calls import CallStatusCallbackEvent
from .common import Page

HttpMethod = Literal["GET", "POST"]


class Application(_Base):
    """A stored TwiML application. ``status_callback_event`` is deprecated (no longer
    emitted by the server)."""

    sid: str | None = None
    account_sid: str | None = None
    friendly_name: str | None = None
    api_version: str | None = None
    voice_url: str | None = None
    voice_method: HttpMethod | str | None = None
    voice_fallback_url: str | None = None
    voice_fallback_method: HttpMethod | str | None = None
    voice_caller_id_lookup: bool | None = None
    status_callback: str | None = None
    status_callback_method: HttpMethod | str | None = None
    message_status_callback: str | None = None
    sms_status_callback: str | None = None
    sms_url: str | None = None
    sms_method: HttpMethod | str | None = None
    sms_fallback_url: str | None = None
    sms_fallback_method: HttpMethod | str | None = None
    status_callback_event: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None


class ApplicationList(Page[Application]):
    applications: list[Application] = Field(default_factory=list)


class _ApplicationBody(_Request):
    """Shared form fields for create + update."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: HttpMethod | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: HttpMethod | None = Field(default=None, alias="VoiceFallbackMethod")
    voice_caller_id_lookup: bool | None = Field(default=None, alias="VoiceCallerIdLookup")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: HttpMethod | None = Field(default=None, alias="StatusCallbackMethod")
    status_callback_event: list[CallStatusCallbackEvent] | None = Field(
        default=None, alias="StatusCallbackEvent"
    )
    message_status_callback: str | None = Field(default=None, alias="MessageStatusCallback")
    sms_status_callback: str | None = Field(default=None, alias="SmsStatusCallback")
    sms_url: str | None = Field(default=None, alias="SmsUrl")
    sms_method: HttpMethod | None = Field(default=None, alias="SmsMethod")
    sms_fallback_url: str | None = Field(default=None, alias="SmsFallbackUrl")
    sms_fallback_method: HttpMethod | None = Field(default=None, alias="SmsFallbackMethod")
    public_application_connect_enabled: bool | None = Field(
        default=None, alias="PublicApplicationConnectEnabled"
    )


class CreateApplicationRequest(_ApplicationBody):
    """Body for ``POST /Applications``. All fields optional per spec."""


class UpdateApplicationRequest(_ApplicationBody):
    """Body for ``POST /Applications/{sid}``. Partial — only set fields are touched."""
