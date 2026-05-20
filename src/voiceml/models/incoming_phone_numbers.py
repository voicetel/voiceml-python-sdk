"""``IncomingPhoneNumbers`` resource — tenant-self-serve DID assignment + voice routing.

The schema follows Twilio's full ``IncomingPhoneNumber`` shape so strict-binding SDKs
deserialize without throwing. Fields VoiceML doesn't track (regulatory, SMS, emergency,
trunking) come back empty / default; the spec at ``IncomingPhoneNumber:`` documents the
per-field Twilio-compat policy.

Note: ``sid`` is the canonical ``PN``-prefixed identifier; ``phone_number`` carries the
E.164 form. These are distinct fields — code that needs the dialable number reads
``.phone_number``, code that needs a stable handle reads ``.sid``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import Page

HttpMethod = Literal["GET", "POST"]


class IncomingPhoneNumberCapabilities(_Base):
    """Twilio-compat channel-capability bag. VoiceML is voice-only, so ``voice`` is the
    only field that ever flips ``True``; the rest stay ``False`` to match the wire.
    """

    voice: bool = False
    sms: bool = False
    mms: bool = False
    fax: bool = False


class IncomingPhoneNumber(_Base):
    """One DID assigned to the authenticated tenant.

    Fields are typed loosely (``str | None``) on the Twilio-compat slots that VoiceML
    emits empty — Pydantic's ``extra="allow"`` covers future-server additions.
    """

    sid: str
    account_sid: str
    phone_number: str
    friendly_name: str | None = None
    api_version: str | None = None
    uri: str | None = None

    # Voice routing — the live, tenant-editable fields.
    voice_url: str | None = None
    voice_method: HttpMethod | None = None
    voice_fallback_url: str | None = None
    voice_fallback_method: HttpMethod | None = None

    # Capabilities + lifecycle metadata.
    capabilities: IncomingPhoneNumberCapabilities | None = None
    date_created: str | None = None
    date_updated: str | None = None

    # Twilio-compat fields VoiceML emits empty / default. Listed so static type
    # checkers and IDE completion see the full Twilio surface.
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


class IncomingPhoneNumberList(Page[IncomingPhoneNumber]):
    """Paginated list response from ``GET /IncomingPhoneNumbers``."""

    incoming_phone_numbers: list[IncomingPhoneNumber] = Field(default_factory=list)


class CreateIncomingPhoneNumberRequest(_Base):
    """Body for ``POST /IncomingPhoneNumbers``.

    ``PhoneNumber`` is required (E.164). Voice routing fields are optional — re-POSTing
    the same number rebinds routing on the existing row (idempotent per spec).
    """

    phone_number: str = Field(alias="PhoneNumber")
    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: HttpMethod | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: HttpMethod | None = Field(default=None, alias="VoiceFallbackMethod")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")


class UpdateIncomingPhoneNumberRequest(_Base):
    """Body for ``POST /IncomingPhoneNumbers/{PhoneNumberSid}`` — partial update.

    Only set fields are touched server-side.
    """

    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: HttpMethod | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: HttpMethod | None = Field(default=None, alias="VoiceFallbackMethod")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")
