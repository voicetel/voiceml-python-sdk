"""``/v1/*`` REST surface — Twilio Voice v1 (voice.twilio.com/v1).

Six sub-resources live under ``client.voice_v1``:

- ``client.voice_v1.byoc_trunks.*`` — :class:`VoiceV1ByocTrunksResource`
- ``client.voice_v1.connection_policies.*`` — :class:`VoiceV1ConnectionPoliciesResource`,
  with per-policy ``client.voice_v1.connection_policies.targets(sid).*``
- ``client.voice_v1.settings.*`` — :class:`VoiceV1SettingsResource`
- ``client.voice_v1.source_ip_mappings.*` — :class:`VoiceV1SourceIpMappingsResource`
- ``client.voice_v1.ip_records.*`` — :class:`VoiceV1IpRecordsResource`

These paths sit at ``/v1/`` (no ``/2010-04-01/Accounts/{Sid}/`` prefix);
the account is resolved from HTTP Basic auth, so the resource classes
use bare path strings rather than the :meth:`Resource._path` helper that
prepends the AccountSid namespace.
"""

from __future__ import annotations

from ..models import (
    CreateVoiceV1ByocTrunkRequest,
    CreateVoiceV1ConnectionPolicyRequest,
    CreateVoiceV1ConnectionPolicyTargetRequest,
    CreateVoiceV1IpRecordRequest,
    CreateVoiceV1SourceIpMappingRequest,
    UpdateVoiceV1ByocTrunkRequest,
    UpdateVoiceV1ConnectionPolicyRequest,
    UpdateVoiceV1ConnectionPolicyTargetRequest,
    UpdateVoiceV1DialingPermissionsSettingsRequest,
    UpdateVoiceV1IpRecordRequest,
    UpdateVoiceV1SourceIpMappingRequest,
    VoiceV1ByocTrunk,
    VoiceV1ByocTrunkList,
    VoiceV1ConnectionPolicy,
    VoiceV1ConnectionPolicyList,
    VoiceV1ConnectionPolicyTarget,
    VoiceV1ConnectionPolicyTargetList,
    VoiceV1DialingPermissionsSettings,
    VoiceV1IpRecord,
    VoiceV1IpRecordList,
    VoiceV1SourceIpMapping,
    VoiceV1SourceIpMappingList,
)


def _page_params(*, page_size: int | None) -> dict[str, object]:
    return {"PageSize": page_size}


# ===========================================================================
# Sync resources
# ===========================================================================


class VoiceV1IpRecordsResource:
    """Operations on ``/v1/IpRecords`` (sync)."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def create(
        self,
        *,
        ip_address: str,
        friendly_name: str | None = None,
        cidr_prefix_length: int | None = None,
    ) -> VoiceV1IpRecord:
        body = CreateVoiceV1IpRecordRequest(
            IpAddress=ip_address,
            FriendlyName=friendly_name,
            CidrPrefixLength=cidr_prefix_length,
        ).to_form()
        return VoiceV1IpRecord.model_validate(
            self._t.request("POST", "/v1/IpRecords", data=body)
        )

    def list(self, *, page_size: int | None = None) -> VoiceV1IpRecordList:
        return VoiceV1IpRecordList.model_validate(
            self._t.request(
                "GET", "/v1/IpRecords", params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> VoiceV1IpRecord:
        return VoiceV1IpRecord.model_validate(
            self._t.request("GET", f"/v1/IpRecords/{sid}")
        )

    def update(
        self, sid: str, *, friendly_name: str | None = None
    ) -> VoiceV1IpRecord:
        body = UpdateVoiceV1IpRecordRequest(FriendlyName=friendly_name).to_form()
        return VoiceV1IpRecord.model_validate(
            self._t.request("POST", f"/v1/IpRecords/{sid}", data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", f"/v1/IpRecords/{sid}")


class VoiceV1SourceIpMappingsResource:
    """Operations on ``/v1/SourceIpMappings`` (sync)."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def create(
        self, *, ip_record_sid: str, sip_domain_sid: str
    ) -> VoiceV1SourceIpMapping:
        body = CreateVoiceV1SourceIpMappingRequest(
            IpRecordSid=ip_record_sid, SipDomainSid=sip_domain_sid
        ).to_form()
        return VoiceV1SourceIpMapping.model_validate(
            self._t.request("POST", "/v1/SourceIpMappings", data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> VoiceV1SourceIpMappingList:
        return VoiceV1SourceIpMappingList.model_validate(
            self._t.request(
                "GET",
                "/v1/SourceIpMappings",
                params=_page_params(page_size=page_size),
            )
        )

    def fetch(self, sid: str) -> VoiceV1SourceIpMapping:
        return VoiceV1SourceIpMapping.model_validate(
            self._t.request("GET", f"/v1/SourceIpMappings/{sid}")
        )

    def update(self, sid: str, *, sip_domain_sid: str) -> VoiceV1SourceIpMapping:
        body = UpdateVoiceV1SourceIpMappingRequest(
            SipDomainSid=sip_domain_sid
        ).to_form()
        return VoiceV1SourceIpMapping.model_validate(
            self._t.request("POST", f"/v1/SourceIpMappings/{sid}", data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", f"/v1/SourceIpMappings/{sid}")


def _byoc_trunk_create_form(
    **kwargs: object,
) -> dict[str, object]:
    return CreateVoiceV1ByocTrunkRequest(
        FriendlyName=kwargs.get("friendly_name"),
        VoiceUrl=kwargs.get("voice_url"),
        VoiceMethod=kwargs.get("voice_method"),
        VoiceFallbackUrl=kwargs.get("voice_fallback_url"),
        VoiceFallbackMethod=kwargs.get("voice_fallback_method"),
        StatusCallbackUrl=kwargs.get("status_callback_url"),
        StatusCallbackMethod=kwargs.get("status_callback_method"),
        CnamLookupEnabled=kwargs.get("cnam_lookup_enabled"),
        ConnectionPolicySid=kwargs.get("connection_policy_sid"),
        FromDomainSid=kwargs.get("from_domain_sid"),
    ).to_form()


def _byoc_trunk_update_form(
    **kwargs: object,
) -> dict[str, object]:
    return UpdateVoiceV1ByocTrunkRequest(
        FriendlyName=kwargs.get("friendly_name"),
        VoiceUrl=kwargs.get("voice_url"),
        VoiceMethod=kwargs.get("voice_method"),
        VoiceFallbackUrl=kwargs.get("voice_fallback_url"),
        VoiceFallbackMethod=kwargs.get("voice_fallback_method"),
        StatusCallbackUrl=kwargs.get("status_callback_url"),
        StatusCallbackMethod=kwargs.get("status_callback_method"),
        CnamLookupEnabled=kwargs.get("cnam_lookup_enabled"),
        ConnectionPolicySid=kwargs.get("connection_policy_sid"),
        FromDomainSid=kwargs.get("from_domain_sid"),
    ).to_form()


class VoiceV1ByocTrunksResource:
    """Operations on ``/v1/ByocTrunks`` (sync)."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def create(
        self,
        *,
        friendly_name: str | None = None,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        status_callback_url: str | None = None,
        status_callback_method: str | None = None,
        cnam_lookup_enabled: bool | None = None,
        connection_policy_sid: str | None = None,
        from_domain_sid: str | None = None,
    ) -> VoiceV1ByocTrunk:
        return VoiceV1ByocTrunk.model_validate(
            self._t.request(
                "POST",
                "/v1/ByocTrunks",
                data=_byoc_trunk_create_form(
                    friendly_name=friendly_name,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    status_callback_url=status_callback_url,
                    status_callback_method=status_callback_method,
                    cnam_lookup_enabled=cnam_lookup_enabled,
                    connection_policy_sid=connection_policy_sid,
                    from_domain_sid=from_domain_sid,
                ),
            )
        )

    def list(self, *, page_size: int | None = None) -> VoiceV1ByocTrunkList:
        return VoiceV1ByocTrunkList.model_validate(
            self._t.request(
                "GET", "/v1/ByocTrunks", params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> VoiceV1ByocTrunk:
        return VoiceV1ByocTrunk.model_validate(
            self._t.request("GET", f"/v1/ByocTrunks/{sid}")
        )

    def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        status_callback_url: str | None = None,
        status_callback_method: str | None = None,
        cnam_lookup_enabled: bool | None = None,
        connection_policy_sid: str | None = None,
        from_domain_sid: str | None = None,
    ) -> VoiceV1ByocTrunk:
        return VoiceV1ByocTrunk.model_validate(
            self._t.request(
                "POST",
                f"/v1/ByocTrunks/{sid}",
                data=_byoc_trunk_update_form(
                    friendly_name=friendly_name,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    status_callback_url=status_callback_url,
                    status_callback_method=status_callback_method,
                    cnam_lookup_enabled=cnam_lookup_enabled,
                    connection_policy_sid=connection_policy_sid,
                    from_domain_sid=from_domain_sid,
                ),
            )
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", f"/v1/ByocTrunks/{sid}")


class _VoiceV1ConnectionPolicyTargetsResource:
    """Per-policy ``/v1/ConnectionPolicies/{Sid}/Targets`` operations (sync)."""

    def __init__(self, transport: object, connection_policy_sid: str) -> None:
        self._t = transport
        self._policy_sid = connection_policy_sid

    def _root(self, *tail: str) -> str:
        parts = ["v1", "ConnectionPolicies", self._policy_sid, "Targets", *tail]
        return "/" + "/".join(parts)

    def create(
        self,
        *,
        target: str,
        friendly_name: str | None = None,
        priority: int | None = None,
        weight: int | None = None,
        enabled: bool | None = None,
    ) -> VoiceV1ConnectionPolicyTarget:
        body = CreateVoiceV1ConnectionPolicyTargetRequest(
            Target=target,
            FriendlyName=friendly_name,
            Priority=priority,
            Weight=weight,
            Enabled=enabled,
        ).to_form()
        return VoiceV1ConnectionPolicyTarget.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> VoiceV1ConnectionPolicyTargetList:
        return VoiceV1ConnectionPolicyTargetList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> VoiceV1ConnectionPolicyTarget:
        return VoiceV1ConnectionPolicyTarget.model_validate(
            self._t.request("GET", self._root(sid))
        )

    def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        target: str | None = None,
        priority: int | None = None,
        weight: int | None = None,
        enabled: bool | None = None,
    ) -> VoiceV1ConnectionPolicyTarget:
        body = UpdateVoiceV1ConnectionPolicyTargetRequest(
            FriendlyName=friendly_name,
            Target=target,
            Priority=priority,
            Weight=weight,
            Enabled=enabled,
        ).to_form()
        return VoiceV1ConnectionPolicyTarget.model_validate(
            self._t.request("POST", self._root(sid), data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", self._root(sid))


class VoiceV1ConnectionPoliciesResource:
    """Operations on ``/v1/ConnectionPolicies`` (sync)."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def create(
        self, *, friendly_name: str | None = None
    ) -> VoiceV1ConnectionPolicy:
        body = CreateVoiceV1ConnectionPolicyRequest(
            FriendlyName=friendly_name
        ).to_form()
        return VoiceV1ConnectionPolicy.model_validate(
            self._t.request("POST", "/v1/ConnectionPolicies", data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> VoiceV1ConnectionPolicyList:
        return VoiceV1ConnectionPolicyList.model_validate(
            self._t.request(
                "GET",
                "/v1/ConnectionPolicies",
                params=_page_params(page_size=page_size),
            )
        )

    def fetch(self, sid: str) -> VoiceV1ConnectionPolicy:
        return VoiceV1ConnectionPolicy.model_validate(
            self._t.request("GET", f"/v1/ConnectionPolicies/{sid}")
        )

    def update(
        self, sid: str, *, friendly_name: str | None = None
    ) -> VoiceV1ConnectionPolicy:
        body = UpdateVoiceV1ConnectionPolicyRequest(
            FriendlyName=friendly_name
        ).to_form()
        return VoiceV1ConnectionPolicy.model_validate(
            self._t.request("POST", f"/v1/ConnectionPolicies/{sid}", data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", f"/v1/ConnectionPolicies/{sid}")

    def targets(
        self, connection_policy_sid: str
    ) -> _VoiceV1ConnectionPolicyTargetsResource:
        """Sub-resource for the policy's :class:`VoiceV1ConnectionPolicyTarget` rows."""
        return _VoiceV1ConnectionPolicyTargetsResource(
            self._t, connection_policy_sid
        )


class VoiceV1SettingsResource:
    """Operations on ``/v1/Settings`` (DialingPermissions; sync)."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def fetch(self) -> VoiceV1DialingPermissionsSettings:
        return VoiceV1DialingPermissionsSettings.model_validate(
            self._t.request("GET", "/v1/Settings")
        )

    def update(
        self, *, dialing_permissions_inheritance: bool | None = None
    ) -> VoiceV1DialingPermissionsSettings:
        body = UpdateVoiceV1DialingPermissionsSettingsRequest(
            DialingPermissionsInheritance=dialing_permissions_inheritance
        ).to_form()
        return VoiceV1DialingPermissionsSettings.model_validate(
            self._t.request("POST", "/v1/Settings", data=body)
        )


class VoiceV1Resource:
    """Holder for ``client.voice_v1.*`` sub-resources (sync)."""

    def __init__(self, transport: object) -> None:
        self.byoc_trunks = VoiceV1ByocTrunksResource(transport)
        self.connection_policies = VoiceV1ConnectionPoliciesResource(transport)
        self.settings = VoiceV1SettingsResource(transport)
        self.source_ip_mappings = VoiceV1SourceIpMappingsResource(transport)
        self.ip_records = VoiceV1IpRecordsResource(transport)


# ===========================================================================
# Async counterparts
# ===========================================================================


class VoiceV1IpRecordsAsyncResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def create(
        self,
        *,
        ip_address: str,
        friendly_name: str | None = None,
        cidr_prefix_length: int | None = None,
    ) -> VoiceV1IpRecord:
        body = CreateVoiceV1IpRecordRequest(
            IpAddress=ip_address,
            FriendlyName=friendly_name,
            CidrPrefixLength=cidr_prefix_length,
        ).to_form()
        return VoiceV1IpRecord.model_validate(
            await self._t.request("POST", "/v1/IpRecords", data=body)
        )

    async def list(self, *, page_size: int | None = None) -> VoiceV1IpRecordList:
        return VoiceV1IpRecordList.model_validate(
            await self._t.request(
                "GET", "/v1/IpRecords", params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> VoiceV1IpRecord:
        return VoiceV1IpRecord.model_validate(
            await self._t.request("GET", f"/v1/IpRecords/{sid}")
        )

    async def update(
        self, sid: str, *, friendly_name: str | None = None
    ) -> VoiceV1IpRecord:
        body = UpdateVoiceV1IpRecordRequest(FriendlyName=friendly_name).to_form()
        return VoiceV1IpRecord.model_validate(
            await self._t.request("POST", f"/v1/IpRecords/{sid}", data=body)
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", f"/v1/IpRecords/{sid}")


class VoiceV1SourceIpMappingsAsyncResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def create(
        self, *, ip_record_sid: str, sip_domain_sid: str
    ) -> VoiceV1SourceIpMapping:
        body = CreateVoiceV1SourceIpMappingRequest(
            IpRecordSid=ip_record_sid, SipDomainSid=sip_domain_sid
        ).to_form()
        return VoiceV1SourceIpMapping.model_validate(
            await self._t.request("POST", "/v1/SourceIpMappings", data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> VoiceV1SourceIpMappingList:
        return VoiceV1SourceIpMappingList.model_validate(
            await self._t.request(
                "GET",
                "/v1/SourceIpMappings",
                params=_page_params(page_size=page_size),
            )
        )

    async def fetch(self, sid: str) -> VoiceV1SourceIpMapping:
        return VoiceV1SourceIpMapping.model_validate(
            await self._t.request("GET", f"/v1/SourceIpMappings/{sid}")
        )

    async def update(
        self, sid: str, *, sip_domain_sid: str
    ) -> VoiceV1SourceIpMapping:
        body = UpdateVoiceV1SourceIpMappingRequest(
            SipDomainSid=sip_domain_sid
        ).to_form()
        return VoiceV1SourceIpMapping.model_validate(
            await self._t.request(
                "POST", f"/v1/SourceIpMappings/{sid}", data=body
            )
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", f"/v1/SourceIpMappings/{sid}")


class VoiceV1ByocTrunksAsyncResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def create(
        self,
        *,
        friendly_name: str | None = None,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        status_callback_url: str | None = None,
        status_callback_method: str | None = None,
        cnam_lookup_enabled: bool | None = None,
        connection_policy_sid: str | None = None,
        from_domain_sid: str | None = None,
    ) -> VoiceV1ByocTrunk:
        return VoiceV1ByocTrunk.model_validate(
            await self._t.request(
                "POST",
                "/v1/ByocTrunks",
                data=_byoc_trunk_create_form(
                    friendly_name=friendly_name,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    status_callback_url=status_callback_url,
                    status_callback_method=status_callback_method,
                    cnam_lookup_enabled=cnam_lookup_enabled,
                    connection_policy_sid=connection_policy_sid,
                    from_domain_sid=from_domain_sid,
                ),
            )
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> VoiceV1ByocTrunkList:
        return VoiceV1ByocTrunkList.model_validate(
            await self._t.request(
                "GET", "/v1/ByocTrunks", params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> VoiceV1ByocTrunk:
        return VoiceV1ByocTrunk.model_validate(
            await self._t.request("GET", f"/v1/ByocTrunks/{sid}")
        )

    async def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        status_callback_url: str | None = None,
        status_callback_method: str | None = None,
        cnam_lookup_enabled: bool | None = None,
        connection_policy_sid: str | None = None,
        from_domain_sid: str | None = None,
    ) -> VoiceV1ByocTrunk:
        return VoiceV1ByocTrunk.model_validate(
            await self._t.request(
                "POST",
                f"/v1/ByocTrunks/{sid}",
                data=_byoc_trunk_update_form(
                    friendly_name=friendly_name,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    status_callback_url=status_callback_url,
                    status_callback_method=status_callback_method,
                    cnam_lookup_enabled=cnam_lookup_enabled,
                    connection_policy_sid=connection_policy_sid,
                    from_domain_sid=from_domain_sid,
                ),
            )
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", f"/v1/ByocTrunks/{sid}")


class _VoiceV1ConnectionPolicyTargetsAsyncResource:
    def __init__(self, transport: object, connection_policy_sid: str) -> None:
        self._t = transport
        self._policy_sid = connection_policy_sid

    def _root(self, *tail: str) -> str:
        parts = ["v1", "ConnectionPolicies", self._policy_sid, "Targets", *tail]
        return "/" + "/".join(parts)

    async def create(
        self,
        *,
        target: str,
        friendly_name: str | None = None,
        priority: int | None = None,
        weight: int | None = None,
        enabled: bool | None = None,
    ) -> VoiceV1ConnectionPolicyTarget:
        body = CreateVoiceV1ConnectionPolicyTargetRequest(
            Target=target,
            FriendlyName=friendly_name,
            Priority=priority,
            Weight=weight,
            Enabled=enabled,
        ).to_form()
        return VoiceV1ConnectionPolicyTarget.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> VoiceV1ConnectionPolicyTargetList:
        return VoiceV1ConnectionPolicyTargetList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> VoiceV1ConnectionPolicyTarget:
        return VoiceV1ConnectionPolicyTarget.model_validate(
            await self._t.request("GET", self._root(sid))
        )

    async def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        target: str | None = None,
        priority: int | None = None,
        weight: int | None = None,
        enabled: bool | None = None,
    ) -> VoiceV1ConnectionPolicyTarget:
        body = UpdateVoiceV1ConnectionPolicyTargetRequest(
            FriendlyName=friendly_name,
            Target=target,
            Priority=priority,
            Weight=weight,
            Enabled=enabled,
        ).to_form()
        return VoiceV1ConnectionPolicyTarget.model_validate(
            await self._t.request("POST", self._root(sid), data=body)
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", self._root(sid))


class VoiceV1ConnectionPoliciesAsyncResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def create(
        self, *, friendly_name: str | None = None
    ) -> VoiceV1ConnectionPolicy:
        body = CreateVoiceV1ConnectionPolicyRequest(
            FriendlyName=friendly_name
        ).to_form()
        return VoiceV1ConnectionPolicy.model_validate(
            await self._t.request("POST", "/v1/ConnectionPolicies", data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> VoiceV1ConnectionPolicyList:
        return VoiceV1ConnectionPolicyList.model_validate(
            await self._t.request(
                "GET",
                "/v1/ConnectionPolicies",
                params=_page_params(page_size=page_size),
            )
        )

    async def fetch(self, sid: str) -> VoiceV1ConnectionPolicy:
        return VoiceV1ConnectionPolicy.model_validate(
            await self._t.request("GET", f"/v1/ConnectionPolicies/{sid}")
        )

    async def update(
        self, sid: str, *, friendly_name: str | None = None
    ) -> VoiceV1ConnectionPolicy:
        body = UpdateVoiceV1ConnectionPolicyRequest(
            FriendlyName=friendly_name
        ).to_form()
        return VoiceV1ConnectionPolicy.model_validate(
            await self._t.request(
                "POST", f"/v1/ConnectionPolicies/{sid}", data=body
            )
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", f"/v1/ConnectionPolicies/{sid}")

    def targets(
        self, connection_policy_sid: str
    ) -> _VoiceV1ConnectionPolicyTargetsAsyncResource:
        return _VoiceV1ConnectionPolicyTargetsAsyncResource(
            self._t, connection_policy_sid
        )


class VoiceV1SettingsAsyncResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def fetch(self) -> VoiceV1DialingPermissionsSettings:
        return VoiceV1DialingPermissionsSettings.model_validate(
            await self._t.request("GET", "/v1/Settings")
        )

    async def update(
        self, *, dialing_permissions_inheritance: bool | None = None
    ) -> VoiceV1DialingPermissionsSettings:
        body = UpdateVoiceV1DialingPermissionsSettingsRequest(
            DialingPermissionsInheritance=dialing_permissions_inheritance
        ).to_form()
        return VoiceV1DialingPermissionsSettings.model_validate(
            await self._t.request("POST", "/v1/Settings", data=body)
        )


class VoiceV1AsyncResource:
    """Holder for ``client.voice_v1.*`` sub-resources (async)."""

    def __init__(self, transport: object) -> None:
        self.byoc_trunks = VoiceV1ByocTrunksAsyncResource(transport)
        self.connection_policies = VoiceV1ConnectionPoliciesAsyncResource(transport)
        self.settings = VoiceV1SettingsAsyncResource(transport)
        self.source_ip_mappings = VoiceV1SourceIpMappingsAsyncResource(transport)
        self.ip_records = VoiceV1IpRecordsAsyncResource(transport)
