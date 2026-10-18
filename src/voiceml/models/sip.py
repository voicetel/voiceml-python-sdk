"""SIP Trunking resources — the Twilio-compatible ``/SIP`` REST surface.

VoiceML's SIP Trunking surface covers three sub-trees:

- **Domains** (`SD…`): SIP ingress endpoints with voice URL handlers.
- **CredentialLists** (`CL…`) holding **Credentials** (`CR…`): username +
  password for SIP-digest authentication of dialing or registering devices.
- **IpAccessControlLists** (`AL…`) holding **IpAddresses** (`IP…`):
  CIDR-bound allowlists for source IP authentication.

CredentialLists and IpAccessControlLists are attached to a SipDomain via
"mappings" — separate sub-resources that record which authentication
sources guard a domain's call traffic and registration traffic. Twilio
exposes four mapping endpoints per domain:

- ``/SIP/Domains/{Sid}/CredentialListMappings`` — historical alias for
  the calls-auth credential list bound to the domain.
- ``/SIP/Domains/{Sid}/IpAccessControlListMappings`` — historical alias
  for the calls-auth ACL bound to the domain.
- ``/SIP/Domains/{Sid}/Auth/Calls/CredentialListMappings`` and
  ``/SIP/Domains/{Sid}/Auth/Calls/IpAccessControlListMappings`` — the
  current ``Auth/Calls`` namespace; same wire shape as the historical
  aliases.
- ``/SIP/Domains/{Sid}/Auth/Registrations/CredentialListMappings`` —
  controls who may SIP-REGISTER against the domain (no ACL counterpart
  on the registrations side; only credential lists are supported there).

All four mapping endpoints round-trip the same :class:`SipDomainMapping`
shape; the namespace difference is purely a routing concern.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request
from .common import Page

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class SipDomain(_Base):
    """A SIP ingress domain — Twilio-compatible ``SD…`` resource.

    Bind a CredentialList and/or IpAccessControlList via the mapping
    sub-resources to authenticate inbound SIP traffic.
    """

    sid: str | None = None
    account_sid: str | None = None
    domain_name: str | None = None
    api_version: str | None = None
    friendly_name: str | None = None
    auth_type: str | None = None
    voice_url: str | None = None
    voice_method: str | None = None
    voice_fallback_url: str | None = None
    voice_fallback_method: str | None = None
    voice_status_callback_url: str | None = None
    voice_status_callback_method: str | None = None
    sip_registration: bool | None = None
    emergency_calling_enabled: bool | None = None
    secure: bool | None = None
    byoc_trunk_sid: str | None = None
    emergency_caller_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None
    subresource_uris: dict[str, str] | None = None


class SipDomainList(Page[SipDomain]):
    domains: list[SipDomain] = Field(default_factory=list)


class SipCredentialList(_Base):
    """A named bag of SIP-digest credentials — Twilio-compatible ``CL…``."""

    sid: str | None = None
    account_sid: str | None = None
    friendly_name: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None
    subresource_uris: dict[str, str] | None = None


class SipCredentialListList(Page[SipCredentialList]):
    credential_lists: list[SipCredentialList] = Field(default_factory=list)


class SipCredential(_Base):
    """A single SIP-digest username + (write-only) password — ``CR…``.

    ``password`` is never round-tripped on the response — only the
    ``username`` survives across fetch/list. To rotate, ``update`` with
    a new password.
    """

    sid: str | None = None
    account_sid: str | None = None
    credential_list_sid: str | None = None
    username: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None


class SipCredentialListPage(Page[SipCredential]):
    """List page for credentials within a CredentialList.

    Spec-named ``SipCredentialListPage`` (note: it's a *page of credentials*,
    not a page of credential-lists — the schema name follows the Twilio-compatible API).
    """

    credentials: list[SipCredential] = Field(default_factory=list)


class SipIpAccessControlList(_Base):
    """A named bag of CIDR-bound IP addresses — Twilio-compatible ``AL…``."""

    sid: str | None = None
    account_sid: str | None = None
    friendly_name: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None
    subresource_uris: dict[str, str] | None = None


class SipIpAccessControlListList(Page[SipIpAccessControlList]):
    ip_access_control_lists: list[SipIpAccessControlList] = Field(default_factory=list)


class SipIpAddress(_Base):
    """A single CIDR-bound entry in an IpAccessControlList — ``IP…``."""

    sid: str | None = None
    account_sid: str | None = None
    ip_access_control_list_sid: str | None = None
    friendly_name: str | None = None
    ip_address: str | None = None
    cidr_prefix_length: int
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None


class SipIpAddressList(Page[SipIpAddress]):
    ip_addresses: list[SipIpAddress] = Field(default_factory=list)


class SipDomainMapping(_Base):
    """One CredentialList ↔ Domain or IpAccessControlList ↔ Domain link.

    All four mapping endpoints (Calls / Registrations × CredentialList /
    IpAccessControlList) round-trip this shape. The ``sid`` echoes the
    sid of the bound resource (CL… for credential mappings, AL… for
    IP-ACL mappings); ``domain_sid`` records which domain the binding
    is attached to.

    ``uri`` and ``domain_sid`` are populated on the historical (no-Auth)
    namespace responses but omitted on the modern ``Auth/Calls`` and
    ``Auth/Registrations`` namespace responses, which return the bare
    mapping object without an envelope-style URI.
    """

    sid: str | None = None
    account_sid: str | None = None
    friendly_name: str | None = None
    domain_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None


class SipCredentialListMappingList(Page[SipDomainMapping]):
    credential_list_mappings: list[SipDomainMapping] = Field(default_factory=list)


class SipIpAccessControlListMappingList(Page[SipDomainMapping]):
    ip_access_control_list_mappings: list[SipDomainMapping] = Field(default_factory=list)


class SipAuthMappingList(Page[SipDomainMapping]):
    """List envelope for ``Auth/Calls`` and ``Auth/Registrations`` mappings.

    The modern Auth-namespace list endpoints all wrap their items in a
    generic ``contents`` array instead of a resource-typed field name
    (``credential_list_mappings`` / ``ip_access_control_list_mappings``)
    the way the historical no-Auth endpoints do.
    """

    contents: list[SipDomainMapping] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Request models (form-encoded bodies)
# ---------------------------------------------------------------------------


class CreateSipDomainRequest(_Request):
    """Body for ``POST /SIP/Domains.json``. ``DomainName`` is required."""

    domain_name: str = Field(alias="DomainName")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: Literal["GET", "POST"] | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: Literal["GET", "POST"] | None = Field(
        default=None, alias="VoiceFallbackMethod"
    )
    voice_status_callback_url: str | None = Field(default=None, alias="VoiceStatusCallbackUrl")
    voice_status_callback_method: Literal["GET", "POST"] | None = Field(
        default=None, alias="VoiceStatusCallbackMethod"
    )
    sip_registration: bool | None = Field(default=None, alias="SipRegistration")
    secure: bool | None = Field(default=None, alias="Secure")
    emergency_calling_enabled: bool | None = Field(default=None, alias="EmergencyCallingEnabled")
    byoc_trunk_sid: str | None = Field(default=None, alias="ByocTrunkSid")
    emergency_caller_sid: str | None = Field(default=None, alias="EmergencyCallerSid")


class UpdateSipDomainRequest(_Request):
    """Body for ``POST /SIP/Domains/{Sid}.json``. All fields optional."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: Literal["GET", "POST"] | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: Literal["GET", "POST"] | None = Field(
        default=None, alias="VoiceFallbackMethod"
    )
    voice_status_callback_url: str | None = Field(default=None, alias="VoiceStatusCallbackUrl")
    voice_status_callback_method: Literal["GET", "POST"] | None = Field(
        default=None, alias="VoiceStatusCallbackMethod"
    )
    sip_registration: bool | None = Field(default=None, alias="SipRegistration")
    secure: bool | None = Field(default=None, alias="Secure")
    emergency_calling_enabled: bool | None = Field(default=None, alias="EmergencyCallingEnabled")
    byoc_trunk_sid: str | None = Field(default=None, alias="ByocTrunkSid")
    emergency_caller_sid: str | None = Field(default=None, alias="EmergencyCallerSid")


class CreateSipCredentialListRequest(_Request):
    """Body for ``POST /SIP/CredentialLists.json``."""

    friendly_name: str = Field(alias="FriendlyName")


class UpdateSipCredentialListRequest(_Request):
    """Body for ``POST /SIP/CredentialLists/{Sid}.json``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")


class CreateSipCredentialRequest(_Request):
    """Body for ``POST /SIP/CredentialLists/{CredentialListSid}/Credentials.json``."""

    username: str = Field(alias="Username")
    password: str = Field(alias="Password")


class UpdateSipCredentialRequest(_Request):
    """Body for ``POST /SIP/CredentialLists/{CredentialListSid}/Credentials/{Sid}.json``.

    Only the password is mutable; username and credential-list assignment
    are pinned at creation time.
    """

    password: str = Field(alias="Password")


class CreateSipIpAccessControlListRequest(_Request):
    """Body for ``POST /SIP/IpAccessControlLists.json``."""

    friendly_name: str = Field(alias="FriendlyName")


class UpdateSipIpAccessControlListRequest(_Request):
    """Body for ``POST /SIP/IpAccessControlLists/{Sid}.json``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")


class CreateSipIpAddressRequest(_Request):
    """Body for ``POST /SIP/IpAccessControlLists/{Sid}/IpAddresses.json``.

    ``CidrPrefixLength`` defaults to ``32`` (single host) when omitted.
    """

    friendly_name: str = Field(alias="FriendlyName")
    ip_address: str = Field(alias="IpAddress")
    cidr_prefix_length: int | None = Field(default=None, alias="CidrPrefixLength")


class UpdateSipIpAddressRequest(_Request):
    """Body for ``POST /SIP/IpAccessControlLists/{Sid}/IpAddresses/{Sid}.json``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    ip_address: str | None = Field(default=None, alias="IpAddress")
    cidr_prefix_length: int | None = Field(default=None, alias="CidrPrefixLength")


class CreateSipCredentialListMappingRequest(_Request):
    """Body for any ``…/CredentialListMappings.json`` POST.

    Used for both the historical (no-Auth) namespace and the modern
    Auth/Calls + Auth/Registrations namespaces.
    """

    credential_list_sid: str = Field(alias="CredentialListSid")


class CreateSipIpAccessControlListMappingRequest(_Request):
    """Body for any ``…/IpAccessControlListMappings.json`` POST.

    Used for both the historical (no-Auth) namespace and the modern
    Auth/Calls namespace. No registrations counterpart — Twilio omits
    IP-ACL mappings on the registrations side.
    """

    ip_access_control_list_sid: str = Field(alias="IpAccessControlListSid")


class SipRegistrationContact(_Base):
    """One registered contact binding of a SIP user."""

    contact: str | None = None
    received: str | None = None
    socket: str | None = None
    user_agent: str | None = None
    expires_at: str | None = None
    registered: bool | None = None


class SipRegistrationActiveCall(_Base):
    """The call a registered SIP user is currently on, if any."""

    call_sid: str | None = None
    direction: str | None = None
    remote: str | None = None
    since: str | None = None


class SipRegistration(_Base):
    """A SIP user registration (``GET /SIP/Registrations``)."""

    aor: str | None = None
    username: str | None = None
    domain: str | None = None
    domain_sid: str | None = None
    status: Literal["registered", "expired"] | str | None = None
    caller_id: str | None = None
    user_agent: str | None = None
    last_registered: str | None = None
    contacts: list[SipRegistrationContact] = Field(default_factory=list)
    active_call: SipRegistrationActiveCall | None = None


class SipRegistrationList(Page[SipRegistration]):
    registrations: list[SipRegistration] = Field(default_factory=list)
