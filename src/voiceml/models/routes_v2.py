"""Routes V2 — Twilio's Inbound Processing Region API.

Sits outside the ``/2010-04-01/`` namespace at ``/v2/`` and exposes two
resources, both keyed by their natural identifier (no Account SID in the
path — account is resolved from HTTP Basic auth):

- ``GET / POST /v2/SipDomains/{SipDomain}`` — region binding for an
  existing SipDomain (keyed by the registrable domain string).
- ``GET / POST /v2/PhoneNumbers/{PhoneNumber}`` — region binding for an
  IncomingPhoneNumber (keyed by E.164 or PN sid).

Both resources share the ``QQ…``-prefixed binding sid and the same
``friendly_name`` / ``voice_region`` mutable surface. The underlying
SipDomain or IncomingPhoneNumber MUST already exist via the classic
``/2010-04-01/Accounts/{Sid}/…`` APIs before these can find it.
"""

from __future__ import annotations

from pydantic import Field

from ._base import _Base


class RoutesV2SipDomain(_Base):
    """SIP-domain Inbound Processing Region binding (``QQ…``)."""

    sid: str
    sip_domain: str
    account_sid: str
    friendly_name: str | None = None
    voice_region: str | None = None
    url: str | None = None
    date_created: str
    date_updated: str


class UpdateRoutesV2SipDomainRequest(_Base):
    """Body for ``POST /v2/SipDomains/{SipDomain}``. All fields optional."""

    voice_region: str | None = Field(default=None, alias="VoiceRegion")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")


class RoutesV2PhoneNumber(_Base):
    """Phone-number Inbound Processing Region binding (``QQ…``).

    Mirrors :class:`RoutesV2SipDomain` field-for-field except the
    natural-key field is ``phone_number`` (E.164) instead of ``sip_domain``.
    """

    sid: str
    phone_number: str
    account_sid: str
    friendly_name: str | None = None
    voice_region: str | None = None
    url: str | None = None
    date_created: str
    date_updated: str


class UpdateRoutesV2PhoneNumberRequest(_Base):
    """Body for ``POST /v2/PhoneNumbers/{PhoneNumber}``. All fields optional."""

    voice_region: str | None = Field(default=None, alias="VoiceRegion")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")
