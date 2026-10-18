"""``IncomingPhoneNumbers`` resource — tenant-self-serve DID assignment + voice routing.

The response model carries every field of the Twilio-compatible ``IncomingPhoneNumber``
representation so strict-binding clients deserialize without throwing. Fields VoiceML
doesn't track (regulatory, emergency, trunking) come back empty / default; the spec at
``IncomingPhoneNumber:`` documents the per-field policy.

Note: ``sid`` is the canonical ``PN``-prefixed identifier; ``phone_number`` carries the
E.164 form. These are distinct fields — code that needs the dialable number reads
``.phone_number``, code that needs a stable handle reads ``.sid``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request
from .common import Page

HttpMethod = Literal["GET", "POST"]
IncomingPhoneNumberOrigin = Literal["twilio", "hosted"]
SMS_APPLICATION_SID_PATTERN = r"^AP[0-9a-fA-F]{32}$"


class IncomingPhoneNumberCapabilities(_Base):
    """Twilio-compatible channel-capability bag (``voice`` / ``sms`` / ``mms`` / ``fax``)."""

    voice: bool | None = False
    sms: bool | None = False
    mms: bool | None = False
    fax: bool | None = False


class IncomingPhoneNumber(_Base):
    """One DID assigned to the authenticated tenant.

    Fields are typed loosely (``str | None``) on the Twilio-compat slots that VoiceML
    emits empty — Pydantic's ``extra="allow"`` covers future-server additions.
    """

    sid: str | None = None
    account_sid: str | None = None
    phone_number: str | None = None
    friendly_name: str | None = None
    api_version: str | None = None
    uri: str | None = None

    # Voice routing — the live, tenant-editable fields.
    voice_url: str | None = None
    voice_method: HttpMethod | str | None = None
    voice_fallback_url: str | None = None
    voice_fallback_method: HttpMethod | str | None = None

    # Capabilities + lifecycle metadata.
    capabilities: IncomingPhoneNumberCapabilities | None = None
    date_created: str | None = None
    date_updated: str | None = None

    # Twilio-compatible fields VoiceML may emit empty / default. Listed so static type
    # checkers and IDE completion see the full field set.
    origin: str | None = None
    beta: bool | None = None
    voice_application_sid: str | None = None
    voice_caller_id_lookup: bool | None = None
    voice_receive_mode: str | None = None
    sms_url: str | None = None
    sms_method: str | None = None
    sms_fallback_url: str | None = None
    sms_fallback_method: str | None = None
    sms_application_sid: str | None = None
    status_callback: str | None = None
    status_callback_method: str | None = None
    trunk_sid: str | None = None
    address_sid: str | None = None
    address_requirements: str | None = None
    identity_sid: str | None = None
    bundle_sid: str | None = None
    emergency_status: str | None = None
    emergency_address_sid: str | None = None
    emergency_address_status: str | None = None
    status: str | None = None
    subresource_uris: dict[str, str] | None = None
    # Twilio number-class enum (local / mobile / toll-free). VoiceML doesn't categorize
    # numbers so the server emits it empty; kept for Twilio-compat deserialization.
    type: str | None = None


class IncomingPhoneNumberList(Page[IncomingPhoneNumber]):
    """Paginated list response from ``GET /IncomingPhoneNumbers``."""

    incoming_phone_numbers: list[IncomingPhoneNumber] = Field(default_factory=list)


class CreateIncomingPhoneNumberRequest(_Request):
    """Body for ``POST /IncomingPhoneNumbers``.

    ``PhoneNumber`` is required (E.164). Routing fields are optional — re-POSTing
    the same number rebinds routing on the existing row (idempotent per spec).
    ``friendly_name`` is not settable via the API.
    """

    phone_number: str = Field(alias="PhoneNumber")
    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: HttpMethod | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: HttpMethod | None = Field(default=None, alias="VoiceFallbackMethod")
    sms_url: str | None = Field(default=None, alias="SmsUrl")
    sms_method: HttpMethod | None = Field(default=None, alias="SmsMethod")
    sms_fallback_url: str | None = Field(default=None, alias="SmsFallbackUrl")
    sms_fallback_method: HttpMethod | None = Field(default=None, alias="SmsFallbackMethod")
    sms_application_sid: str | None = Field(
        default=None, alias="SmsApplicationSid", pattern=SMS_APPLICATION_SID_PATTERN
    )


class CreateTypedIncomingPhoneNumberRequest(_Request):
    """Body for ``POST /IncomingPhoneNumbers/{Local,Mobile,TollFree}``.

    The number-class create aliases accept only ``PhoneNumber``, ``VoiceUrl`` and
    ``VoiceMethod``; set the remaining routing fields with ``update`` afterwards.
    """

    phone_number: str = Field(alias="PhoneNumber")
    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: HttpMethod | None = Field(default=None, alias="VoiceMethod")


class UpdateIncomingPhoneNumberRequest(_Request):
    """Body for ``POST /IncomingPhoneNumbers/{PhoneNumberSid}`` — partial update.

    Only set fields are touched server-side. ``friendly_name`` is not settable.
    """

    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: HttpMethod | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: HttpMethod | None = Field(default=None, alias="VoiceFallbackMethod")
    sms_url: str | None = Field(default=None, alias="SmsUrl")
    sms_method: HttpMethod | None = Field(default=None, alias="SmsMethod")
    sms_fallback_url: str | None = Field(default=None, alias="SmsFallbackUrl")
    sms_fallback_method: HttpMethod | None = Field(default=None, alias="SmsFallbackMethod")
    sms_application_sid: str | None = Field(
        default=None, alias="SmsApplicationSid", pattern=SMS_APPLICATION_SID_PATTERN
    )
