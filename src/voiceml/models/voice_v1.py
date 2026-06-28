"""Voice v1 resources — Twilio ``voice.twilio.com/v1`` REST surface.

Sits outside the ``/2010-04-01/`` Twilio-API-classic namespace at ``/v1/`` paths.
The account is resolved from HTTP Basic auth — no ``AccountSid`` segment in
URLs. List responses carry the shared ``meta`` envelope (also reused by
Conversations v1), and dates are ISO-8601 ``date-time`` strings.

Six resources live under ``client.voice_v1.*``:

- ``ByocTrunks`` (``BY``) — bring-your-own-carrier trunks.
- ``ConnectionPolicies`` (``NY``) with nested ``Targets`` (``NE``).
- ``Settings`` — DialingPermissions inheritance toggle (single per-account row).
- ``SourceIpMappings`` (``IB``) — bind an :class:`VoiceV1IpRecord` to a
  SipDomain so inbound calls from that IP route into the domain.
- ``IpRecords`` (``IL``) — standalone allowed source IPs.
"""

from __future__ import annotations

from pydantic import Field

from ._base import _Base


# ---------------------------------------------------------------------------
# Shared list envelope
# ---------------------------------------------------------------------------


class VoiceV1Meta(_Base):
    """Voice/Conversations v1 list envelope.

    Used by every paginated ``/v1/`` list response (Voice and Conversations).
    Fields mirror the wire shape exactly; ``next_page_url`` drives
    auto-pagination if any caller chooses to follow it.
    """

    first_page_url: str | None = None
    next_page_url: str | None = None
    previous_page_url: str | None = None
    url: str | None = None
    page: int | None = None
    page_size: int | None = None
    key: str | None = None


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class VoiceV1IpRecord(_Base):
    """A standalone allowed source IPv4 — Twilio ``IL…`` resource.

    Attach to a SipDomain via :class:`VoiceV1SourceIpMapping` to make
    inbound calls from this CIDR route into the domain.
    """

    account_sid: str | None = None
    sid: str | None = None
    friendly_name: str | None = None
    ip_address: str | None = None
    cidr_prefix_length: int | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None


class VoiceV1IpRecordList(_Base):
    ip_records: list[VoiceV1IpRecord] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class VoiceV1SourceIpMapping(_Base):
    """A binding of an :class:`VoiceV1IpRecord` to a SipDomain — ``IB…``.

    Inbound SIP traffic from the IpRecord's address is routed to the
    SipDomain referenced by ``sip_domain_sid``.
    """

    sid: str | None = None
    ip_record_sid: str | None = None
    sip_domain_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None


class VoiceV1SourceIpMappingList(_Base):
    source_ip_mappings: list[VoiceV1SourceIpMapping] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class VoiceV1ByocTrunk(_Base):
    """A bring-your-own-carrier trunk — Twilio ``BY…`` resource."""

    account_sid: str | None = None
    sid: str | None = None
    friendly_name: str | None = None
    voice_url: str | None = None
    voice_method: str | None = None
    voice_fallback_url: str | None = None
    voice_fallback_method: str | None = None
    status_callback_url: str | None = None
    status_callback_method: str | None = None
    cnam_lookup_enabled: bool | None = None
    connection_policy_sid: str | None = None
    from_domain_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None


class VoiceV1ByocTrunkList(_Base):
    byoc_trunks: list[VoiceV1ByocTrunk] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class VoiceV1ConnectionPolicy(_Base):
    """An origination ConnectionPolicy — Twilio ``NY…`` resource.

    Groups one or more :class:`VoiceV1ConnectionPolicyTarget` rows under a
    single named policy for outbound SIP egress routing.
    """

    account_sid: str | None = None
    sid: str | None = None
    friendly_name: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None
    links: dict[str, str] | None = None


class VoiceV1ConnectionPolicyList(_Base):
    connection_policies: list[VoiceV1ConnectionPolicy] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class VoiceV1ConnectionPolicyTarget(_Base):
    """A single SIP-URI target inside a ConnectionPolicy — ``NE…``.

    Lower ``priority`` is preferred; ``weight`` load-balances among targets
    that share a priority.
    """

    account_sid: str | None = None
    connection_policy_sid: str | None = None
    sid: str | None = None
    friendly_name: str | None = None
    target: str | None = None
    priority: int | None = None
    weight: int | None = None
    enabled: bool | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None


class VoiceV1ConnectionPolicyTargetList(_Base):
    targets: list[VoiceV1ConnectionPolicyTarget] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class VoiceV1DialingPermissionsSettings(_Base):
    """The account-wide DialingPermissions inheritance toggle.

    Twilio exposes only ``dialing_permissions_inheritance`` here; defaults
    to ``False`` when never set.
    """

    dialing_permissions_inheritance: bool | None = None
    url: str | None = None


# ---------------------------------------------------------------------------
# Request models (form-encoded bodies)
# ---------------------------------------------------------------------------


class CreateVoiceV1IpRecordRequest(_Base):
    """Body for ``POST /v1/IpRecords``. ``IpAddress`` is required."""

    ip_address: str = Field(alias="IpAddress")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    cidr_prefix_length: int | None = Field(default=None, alias="CidrPrefixLength")


class UpdateVoiceV1IpRecordRequest(_Base):
    """Body for ``POST /v1/IpRecords/{Sid}``. Only ``FriendlyName`` is mutable."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")


class CreateVoiceV1SourceIpMappingRequest(_Base):
    """Body for ``POST /v1/SourceIpMappings``. Both fields required."""

    ip_record_sid: str = Field(alias="IpRecordSid")
    sip_domain_sid: str = Field(alias="SipDomainSid")


class UpdateVoiceV1SourceIpMappingRequest(_Base):
    """Body for ``POST /v1/SourceIpMappings/{Sid}``. Only ``SipDomainSid`` is mutable."""

    sip_domain_sid: str = Field(alias="SipDomainSid")


class CreateVoiceV1ByocTrunkRequest(_Base):
    """Body for ``POST /v1/ByocTrunks``. All fields optional."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: str | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: str | None = Field(default=None, alias="VoiceFallbackMethod")
    status_callback_url: str | None = Field(default=None, alias="StatusCallbackUrl")
    status_callback_method: str | None = Field(default=None, alias="StatusCallbackMethod")
    cnam_lookup_enabled: bool | None = Field(default=None, alias="CnamLookupEnabled")
    connection_policy_sid: str | None = Field(default=None, alias="ConnectionPolicySid")
    from_domain_sid: str | None = Field(default=None, alias="FromDomainSid")


class UpdateVoiceV1ByocTrunkRequest(_Base):
    """Body for ``POST /v1/ByocTrunks/{Sid}``. All fields optional."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: str | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: str | None = Field(default=None, alias="VoiceFallbackMethod")
    status_callback_url: str | None = Field(default=None, alias="StatusCallbackUrl")
    status_callback_method: str | None = Field(default=None, alias="StatusCallbackMethod")
    cnam_lookup_enabled: bool | None = Field(default=None, alias="CnamLookupEnabled")
    connection_policy_sid: str | None = Field(default=None, alias="ConnectionPolicySid")
    from_domain_sid: str | None = Field(default=None, alias="FromDomainSid")


class CreateVoiceV1ConnectionPolicyRequest(_Base):
    """Body for ``POST /v1/ConnectionPolicies``. All fields optional."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")


class UpdateVoiceV1ConnectionPolicyRequest(_Base):
    """Body for ``POST /v1/ConnectionPolicies/{Sid}``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")


class CreateVoiceV1ConnectionPolicyTargetRequest(_Base):
    """Body for ``POST /v1/ConnectionPolicies/{Sid}/Targets``. ``Target`` is required."""

    target: str = Field(alias="Target")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    priority: int | None = Field(default=None, alias="Priority")
    weight: int | None = Field(default=None, alias="Weight")
    enabled: bool | None = Field(default=None, alias="Enabled")


class UpdateVoiceV1ConnectionPolicyTargetRequest(_Base):
    """Body for ``POST /v1/ConnectionPolicies/{Sid}/Targets/{Sid}``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    target: str | None = Field(default=None, alias="Target")
    priority: int | None = Field(default=None, alias="Priority")
    weight: int | None = Field(default=None, alias="Weight")
    enabled: bool | None = Field(default=None, alias="Enabled")


class UpdateVoiceV1DialingPermissionsSettingsRequest(_Base):
    """Body for ``POST /v1/Settings``."""

    dialing_permissions_inheritance: bool | None = Field(
        default=None, alias="DialingPermissionsInheritance"
    )
