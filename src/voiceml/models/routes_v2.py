"""Routes V2 — Twilio's Inbound Processing Region API.

Sits outside the ``/2010-04-01/`` namespace at ``/v2/`` and is keyed by SIP
**domain name** (not the SipDomain SID). The account is resolved from HTTP
Basic auth, so callers pass only the registrable domain string.

Two operations today:

- ``GET  /v2/SipDomains/{SipDomain}``  — fetch the region binding
- ``POST /v2/SipDomains/{SipDomain}``  — update the region and/or friendly name

The SipDomain resource MUST already exist via the
``/2010-04-01/Accounts/{Sid}/SIP/Domains`` API before this can find it.
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
