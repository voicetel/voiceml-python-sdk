"""``/SIP/*`` REST surface — SIP Trunking (Twilio-compatible).

Three top-level sub-resources live under ``client.sip``:

- ``client.sip.domains`` — :class:`SipDomainsResource`
- ``client.sip.credential_lists`` — :class:`SipCredentialListsResource`
- ``client.sip.ip_access_control_lists`` — :class:`SipIpAccessControlListsResource`

Per-resource sub-collections (credentials within a CredentialList, IP
addresses within an IpAccessControlList, mappings under a domain) are
exposed as factory methods that take the parent sid and return a
purpose-built sub-resource instance::

    client.sip.credential_lists.credentials(credential_list_sid).list()
    client.sip.ip_access_control_lists.ip_addresses(ipacl_sid).create(…)
    client.sip.domains.credential_list_mappings(domain_sid).list()
    client.sip.domains.auth.calls.credential_list_mappings(domain_sid).list()
    client.sip.domains.auth.registrations.credential_list_mappings(domain_sid).list()

The factory pattern keeps method discovery flat (one call into the parent
plus one call into the sub-resource) without exploding the sub-resource
classes into a Cartesian product of all possible parent sids.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..models import (
    CreateSipCredentialListMappingRequest,
    CreateSipCredentialListRequest,
    CreateSipCredentialRequest,
    CreateSipDomainRequest,
    CreateSipIpAccessControlListMappingRequest,
    CreateSipIpAccessControlListRequest,
    CreateSipIpAddressRequest,
    SipCredential,
    SipCredentialList,
    SipCredentialListList,
    SipCredentialListMappingList,
    SipCredentialListPage,
    SipDomain,
    SipDomainList,
    SipDomainMapping,
    SipIpAccessControlList,
    SipIpAccessControlListList,
    SipIpAccessControlListMappingList,
    SipIpAddress,
    SipIpAddressList,
    UpdateSipCredentialListRequest,
    UpdateSipCredentialRequest,
    UpdateSipDomainRequest,
    UpdateSipIpAccessControlListRequest,
    UpdateSipIpAddressRequest,
)
from ._base import AsyncResource, Resource


# ---------------------------------------------------------------------------
# Shared param/body builders
# ---------------------------------------------------------------------------


def _page_params(
    *, page: int | None, page_size: int | None, page_token: str | None
) -> dict[str, object]:
    return {"Page": page, "PageSize": page_size, "PageToken": page_token}


def _create_domain_form(**kwargs: object) -> dict[str, object]:
    return CreateSipDomainRequest(
        DomainName=kwargs["domain_name"],
        FriendlyName=kwargs.get("friendly_name"),
        VoiceUrl=kwargs.get("voice_url"),
        VoiceMethod=kwargs.get("voice_method"),
        VoiceFallbackUrl=kwargs.get("voice_fallback_url"),
        VoiceFallbackMethod=kwargs.get("voice_fallback_method"),
        VoiceStatusCallbackUrl=kwargs.get("voice_status_callback_url"),
        VoiceStatusCallbackMethod=kwargs.get("voice_status_callback_method"),
        SipRegistration=kwargs.get("sip_registration"),
        Secure=kwargs.get("secure"),
        EmergencyCallingEnabled=kwargs.get("emergency_calling_enabled"),
        ByocTrunkSid=kwargs.get("byoc_trunk_sid"),
        EmergencyCallerSid=kwargs.get("emergency_caller_sid"),
    ).to_form()


def _update_domain_form(**kwargs: object) -> dict[str, object]:
    return UpdateSipDomainRequest(
        FriendlyName=kwargs.get("friendly_name"),
        VoiceUrl=kwargs.get("voice_url"),
        VoiceMethod=kwargs.get("voice_method"),
        VoiceFallbackUrl=kwargs.get("voice_fallback_url"),
        VoiceFallbackMethod=kwargs.get("voice_fallback_method"),
        VoiceStatusCallbackUrl=kwargs.get("voice_status_callback_url"),
        VoiceStatusCallbackMethod=kwargs.get("voice_status_callback_method"),
        SipRegistration=kwargs.get("sip_registration"),
        Secure=kwargs.get("secure"),
        EmergencyCallingEnabled=kwargs.get("emergency_calling_enabled"),
        ByocTrunkSid=kwargs.get("byoc_trunk_sid"),
        EmergencyCallerSid=kwargs.get("emergency_caller_sid"),
    ).to_form()


# ===========================================================================
# Sync resources
# ===========================================================================


class _SipDomainCredentialListMappingsResource(Resource):
    """Per-domain CredentialList mappings under ``/SIP/Domains/{Sid}/CredentialListMappings``."""

    def __init__(self, transport: object, domain_sid: str, *, auth_segment: str | None = None) -> None:
        super().__init__(transport)  # type: ignore[arg-type]
        self._domain_sid = domain_sid
        self._auth_segment = auth_segment

    def _root(self, *tail: str) -> str:
        if self._auth_segment:
            return self._path(
                "SIP", "Domains", self._domain_sid, "Auth", self._auth_segment,
                "CredentialListMappings", *tail,
            )
        return self._path(
            "SIP", "Domains", self._domain_sid, "CredentialListMappings", *tail
        )

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipCredentialListMappingList:
        return SipCredentialListMappingList.model_validate(
            self._t.request(
                "GET",
                self._root(),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    def create(self, *, credential_list_sid: str) -> SipDomainMapping:
        body = CreateSipCredentialListMappingRequest(
            CredentialListSid=credential_list_sid
        ).to_form()
        return SipDomainMapping.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def fetch(self, mapping_sid: str) -> SipDomainMapping:
        return SipDomainMapping.model_validate(
            self._t.request("GET", self._root(mapping_sid))
        )

    def delete(self, mapping_sid: str) -> None:
        self._t.request("DELETE", self._root(mapping_sid))


class _SipDomainIpAccessControlListMappingsResource(Resource):
    """Per-domain IpAccessControlList mappings."""

    def __init__(self, transport: object, domain_sid: str, *, auth_segment: str | None = None) -> None:
        super().__init__(transport)  # type: ignore[arg-type]
        self._domain_sid = domain_sid
        self._auth_segment = auth_segment

    def _root(self, *tail: str) -> str:
        if self._auth_segment:
            return self._path(
                "SIP", "Domains", self._domain_sid, "Auth", self._auth_segment,
                "IpAccessControlListMappings", *tail,
            )
        return self._path(
            "SIP", "Domains", self._domain_sid, "IpAccessControlListMappings", *tail
        )

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipIpAccessControlListMappingList:
        return SipIpAccessControlListMappingList.model_validate(
            self._t.request(
                "GET",
                self._root(),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    def create(self, *, ip_access_control_list_sid: str) -> SipDomainMapping:
        body = CreateSipIpAccessControlListMappingRequest(
            IpAccessControlListSid=ip_access_control_list_sid
        ).to_form()
        return SipDomainMapping.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def fetch(self, mapping_sid: str) -> SipDomainMapping:
        return SipDomainMapping.model_validate(
            self._t.request("GET", self._root(mapping_sid))
        )

    def delete(self, mapping_sid: str) -> None:
        self._t.request("DELETE", self._root(mapping_sid))


class _SipDomainAuthCallsResource:
    """Holder for ``client.sip.domains.auth.calls.*`` sub-resources."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def credential_list_mappings(
        self, domain_sid: str
    ) -> _SipDomainCredentialListMappingsResource:
        return _SipDomainCredentialListMappingsResource(
            self._t, domain_sid, auth_segment="Calls"
        )

    def ip_access_control_list_mappings(
        self, domain_sid: str
    ) -> _SipDomainIpAccessControlListMappingsResource:
        return _SipDomainIpAccessControlListMappingsResource(
            self._t, domain_sid, auth_segment="Calls"
        )


class _SipDomainAuthRegistrationsResource:
    """Holder for ``client.sip.domains.auth.registrations.*`` sub-resources.

    Twilio exposes only credential-list mappings on the registrations
    side (no IP-ACL counterpart).
    """

    def __init__(self, transport: object) -> None:
        self._t = transport

    def credential_list_mappings(
        self, domain_sid: str
    ) -> _SipDomainCredentialListMappingsResource:
        return _SipDomainCredentialListMappingsResource(
            self._t, domain_sid, auth_segment="Registrations"
        )


class _SipDomainAuthResource:
    """Holder for ``client.sip.domains.auth.{calls,registrations}``."""

    def __init__(self, transport: object) -> None:
        self.calls = _SipDomainAuthCallsResource(transport)
        self.registrations = _SipDomainAuthRegistrationsResource(transport)


class SipDomainsResource(Resource):
    """Operations on ``/SIP/Domains``."""

    def __init__(self, transport: object) -> None:
        super().__init__(transport)  # type: ignore[arg-type]
        self.auth = _SipDomainAuthResource(transport)

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipDomainList:
        return SipDomainList.model_validate(
            self._t.request(
                "GET",
                self._path("SIP", "Domains"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    def create(
        self,
        *,
        domain_name: str,
        friendly_name: str | None = None,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        voice_status_callback_url: str | None = None,
        voice_status_callback_method: str | None = None,
        sip_registration: bool | None = None,
        secure: bool | None = None,
        emergency_calling_enabled: bool | None = None,
        byoc_trunk_sid: str | None = None,
        emergency_caller_sid: str | None = None,
    ) -> SipDomain:
        return SipDomain.model_validate(
            self._t.request(
                "POST",
                self._path("SIP", "Domains"),
                data=_create_domain_form(
                    domain_name=domain_name,
                    friendly_name=friendly_name,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    voice_status_callback_url=voice_status_callback_url,
                    voice_status_callback_method=voice_status_callback_method,
                    sip_registration=sip_registration,
                    secure=secure,
                    emergency_calling_enabled=emergency_calling_enabled,
                    byoc_trunk_sid=byoc_trunk_sid,
                    emergency_caller_sid=emergency_caller_sid,
                ),
            )
        )

    def fetch(self, domain_sid: str) -> SipDomain:
        return SipDomain.model_validate(
            self._t.request("GET", self._path("SIP", "Domains", domain_sid))
        )

    def update(
        self,
        domain_sid: str,
        *,
        friendly_name: str | None = None,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        voice_status_callback_url: str | None = None,
        voice_status_callback_method: str | None = None,
        sip_registration: bool | None = None,
        secure: bool | None = None,
        emergency_calling_enabled: bool | None = None,
        byoc_trunk_sid: str | None = None,
        emergency_caller_sid: str | None = None,
    ) -> SipDomain:
        return SipDomain.model_validate(
            self._t.request(
                "POST",
                self._path("SIP", "Domains", domain_sid),
                data=_update_domain_form(
                    friendly_name=friendly_name,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    voice_status_callback_url=voice_status_callback_url,
                    voice_status_callback_method=voice_status_callback_method,
                    sip_registration=sip_registration,
                    secure=secure,
                    emergency_calling_enabled=emergency_calling_enabled,
                    byoc_trunk_sid=byoc_trunk_sid,
                    emergency_caller_sid=emergency_caller_sid,
                ),
            )
        )

    def delete(self, domain_sid: str) -> None:
        self._t.request("DELETE", self._path("SIP", "Domains", domain_sid))

    def iter(
        self, *, page_size: int | None = None
    ) -> Sequence[SipDomain]:
        out: list[SipDomain] = []
        page = 0
        while True:
            chunk = self.list(page=page, page_size=page_size)
            out.extend(chunk.domains)
            if not chunk.next_page_uri or not chunk.domains:
                return out
            page += 1

    def credential_list_mappings(
        self, domain_sid: str
    ) -> _SipDomainCredentialListMappingsResource:
        return _SipDomainCredentialListMappingsResource(self._t, domain_sid)

    def ip_access_control_list_mappings(
        self, domain_sid: str
    ) -> _SipDomainIpAccessControlListMappingsResource:
        return _SipDomainIpAccessControlListMappingsResource(self._t, domain_sid)


class _SipCredentialsResource(Resource):
    """Per-CredentialList credentials under ``/SIP/CredentialLists/{Sid}/Credentials``."""

    def __init__(self, transport: object, credential_list_sid: str) -> None:
        super().__init__(transport)  # type: ignore[arg-type]
        self._cl_sid = credential_list_sid

    def _root(self, *tail: str) -> str:
        return self._path(
            "SIP", "CredentialLists", self._cl_sid, "Credentials", *tail
        )

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipCredentialListPage:
        return SipCredentialListPage.model_validate(
            self._t.request(
                "GET",
                self._root(),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    def create(self, *, username: str, password: str) -> SipCredential:
        body = CreateSipCredentialRequest(
            Username=username, Password=password
        ).to_form()
        return SipCredential.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def fetch(self, credential_sid: str) -> SipCredential:
        return SipCredential.model_validate(
            self._t.request("GET", self._root(credential_sid))
        )

    def update(self, credential_sid: str, *, password: str) -> SipCredential:
        body = UpdateSipCredentialRequest(Password=password).to_form()
        return SipCredential.model_validate(
            self._t.request("POST", self._root(credential_sid), data=body)
        )

    def delete(self, credential_sid: str) -> None:
        self._t.request("DELETE", self._root(credential_sid))


class SipCredentialListsResource(Resource):
    """Operations on ``/SIP/CredentialLists``."""

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipCredentialListList:
        return SipCredentialListList.model_validate(
            self._t.request(
                "GET",
                self._path("SIP", "CredentialLists"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    def create(self, *, friendly_name: str) -> SipCredentialList:
        body = CreateSipCredentialListRequest(FriendlyName=friendly_name).to_form()
        return SipCredentialList.model_validate(
            self._t.request("POST", self._path("SIP", "CredentialLists"), data=body)
        )

    def fetch(self, credential_list_sid: str) -> SipCredentialList:
        return SipCredentialList.model_validate(
            self._t.request(
                "GET", self._path("SIP", "CredentialLists", credential_list_sid)
            )
        )

    def update(
        self, credential_list_sid: str, *, friendly_name: str | None = None
    ) -> SipCredentialList:
        body = UpdateSipCredentialListRequest(FriendlyName=friendly_name).to_form()
        return SipCredentialList.model_validate(
            self._t.request(
                "POST",
                self._path("SIP", "CredentialLists", credential_list_sid),
                data=body,
            )
        )

    def delete(self, credential_list_sid: str) -> None:
        self._t.request(
            "DELETE", self._path("SIP", "CredentialLists", credential_list_sid)
        )

    def credentials(self, credential_list_sid: str) -> _SipCredentialsResource:
        return _SipCredentialsResource(self._t, credential_list_sid)


class _SipIpAddressesResource(Resource):
    """Per-IpAccessControlList addresses under ``/SIP/IpAccessControlLists/{Sid}/IpAddresses``."""

    def __init__(self, transport: object, ipacl_sid: str) -> None:
        super().__init__(transport)  # type: ignore[arg-type]
        self._ipacl_sid = ipacl_sid

    def _root(self, *tail: str) -> str:
        return self._path(
            "SIP", "IpAccessControlLists", self._ipacl_sid, "IpAddresses", *tail
        )

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipIpAddressList:
        return SipIpAddressList.model_validate(
            self._t.request(
                "GET",
                self._root(),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    def create(
        self,
        *,
        friendly_name: str,
        ip_address: str,
        cidr_prefix_length: int | None = None,
    ) -> SipIpAddress:
        body = CreateSipIpAddressRequest(
            FriendlyName=friendly_name,
            IpAddress=ip_address,
            CidrPrefixLength=cidr_prefix_length,
        ).to_form()
        return SipIpAddress.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def fetch(self, ip_address_sid: str) -> SipIpAddress:
        return SipIpAddress.model_validate(
            self._t.request("GET", self._root(ip_address_sid))
        )

    def update(
        self,
        ip_address_sid: str,
        *,
        friendly_name: str | None = None,
        ip_address: str | None = None,
        cidr_prefix_length: int | None = None,
    ) -> SipIpAddress:
        body = UpdateSipIpAddressRequest(
            FriendlyName=friendly_name,
            IpAddress=ip_address,
            CidrPrefixLength=cidr_prefix_length,
        ).to_form()
        return SipIpAddress.model_validate(
            self._t.request("POST", self._root(ip_address_sid), data=body)
        )

    def delete(self, ip_address_sid: str) -> None:
        self._t.request("DELETE", self._root(ip_address_sid))


class SipIpAccessControlListsResource(Resource):
    """Operations on ``/SIP/IpAccessControlLists``."""

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipIpAccessControlListList:
        return SipIpAccessControlListList.model_validate(
            self._t.request(
                "GET",
                self._path("SIP", "IpAccessControlLists"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    def create(self, *, friendly_name: str) -> SipIpAccessControlList:
        body = CreateSipIpAccessControlListRequest(
            FriendlyName=friendly_name
        ).to_form()
        return SipIpAccessControlList.model_validate(
            self._t.request(
                "POST", self._path("SIP", "IpAccessControlLists"), data=body
            )
        )

    def fetch(self, ipacl_sid: str) -> SipIpAccessControlList:
        return SipIpAccessControlList.model_validate(
            self._t.request(
                "GET", self._path("SIP", "IpAccessControlLists", ipacl_sid)
            )
        )

    def update(
        self, ipacl_sid: str, *, friendly_name: str | None = None
    ) -> SipIpAccessControlList:
        body = UpdateSipIpAccessControlListRequest(
            FriendlyName=friendly_name
        ).to_form()
        return SipIpAccessControlList.model_validate(
            self._t.request(
                "POST",
                self._path("SIP", "IpAccessControlLists", ipacl_sid),
                data=body,
            )
        )

    def delete(self, ipacl_sid: str) -> None:
        self._t.request(
            "DELETE", self._path("SIP", "IpAccessControlLists", ipacl_sid)
        )

    def ip_addresses(self, ipacl_sid: str) -> _SipIpAddressesResource:
        return _SipIpAddressesResource(self._t, ipacl_sid)


class SipResource:
    """Top-level holder for ``client.sip.{domains,credential_lists,ip_access_control_lists}``."""

    def __init__(self, transport: object) -> None:
        self.domains = SipDomainsResource(transport)
        self.credential_lists = SipCredentialListsResource(transport)
        self.ip_access_control_lists = SipIpAccessControlListsResource(transport)


# ===========================================================================
# Async resources — same surface; methods are awaitable.
# ===========================================================================


class _AsyncSipDomainCredentialListMappingsResource(AsyncResource):
    def __init__(self, transport: object, domain_sid: str, *, auth_segment: str | None = None) -> None:
        super().__init__(transport)  # type: ignore[arg-type]
        self._domain_sid = domain_sid
        self._auth_segment = auth_segment

    def _root(self, *tail: str) -> str:
        if self._auth_segment:
            return self._path(
                "SIP", "Domains", self._domain_sid, "Auth", self._auth_segment,
                "CredentialListMappings", *tail,
            )
        return self._path(
            "SIP", "Domains", self._domain_sid, "CredentialListMappings", *tail
        )

    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipCredentialListMappingList:
        return SipCredentialListMappingList.model_validate(
            await self._t.request(
                "GET",
                self._root(),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def create(self, *, credential_list_sid: str) -> SipDomainMapping:
        body = CreateSipCredentialListMappingRequest(
            CredentialListSid=credential_list_sid
        ).to_form()
        return SipDomainMapping.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def fetch(self, mapping_sid: str) -> SipDomainMapping:
        return SipDomainMapping.model_validate(
            await self._t.request("GET", self._root(mapping_sid))
        )

    async def delete(self, mapping_sid: str) -> None:
        await self._t.request("DELETE", self._root(mapping_sid))


class _AsyncSipDomainIpAccessControlListMappingsResource(AsyncResource):
    def __init__(self, transport: object, domain_sid: str, *, auth_segment: str | None = None) -> None:
        super().__init__(transport)  # type: ignore[arg-type]
        self._domain_sid = domain_sid
        self._auth_segment = auth_segment

    def _root(self, *tail: str) -> str:
        if self._auth_segment:
            return self._path(
                "SIP", "Domains", self._domain_sid, "Auth", self._auth_segment,
                "IpAccessControlListMappings", *tail,
            )
        return self._path(
            "SIP", "Domains", self._domain_sid, "IpAccessControlListMappings", *tail
        )

    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipIpAccessControlListMappingList:
        return SipIpAccessControlListMappingList.model_validate(
            await self._t.request(
                "GET",
                self._root(),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def create(self, *, ip_access_control_list_sid: str) -> SipDomainMapping:
        body = CreateSipIpAccessControlListMappingRequest(
            IpAccessControlListSid=ip_access_control_list_sid
        ).to_form()
        return SipDomainMapping.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def fetch(self, mapping_sid: str) -> SipDomainMapping:
        return SipDomainMapping.model_validate(
            await self._t.request("GET", self._root(mapping_sid))
        )

    async def delete(self, mapping_sid: str) -> None:
        await self._t.request("DELETE", self._root(mapping_sid))


class _AsyncSipDomainAuthCallsResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def credential_list_mappings(
        self, domain_sid: str
    ) -> _AsyncSipDomainCredentialListMappingsResource:
        return _AsyncSipDomainCredentialListMappingsResource(
            self._t, domain_sid, auth_segment="Calls"
        )

    def ip_access_control_list_mappings(
        self, domain_sid: str
    ) -> _AsyncSipDomainIpAccessControlListMappingsResource:
        return _AsyncSipDomainIpAccessControlListMappingsResource(
            self._t, domain_sid, auth_segment="Calls"
        )


class _AsyncSipDomainAuthRegistrationsResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def credential_list_mappings(
        self, domain_sid: str
    ) -> _AsyncSipDomainCredentialListMappingsResource:
        return _AsyncSipDomainCredentialListMappingsResource(
            self._t, domain_sid, auth_segment="Registrations"
        )


class _AsyncSipDomainAuthResource:
    def __init__(self, transport: object) -> None:
        self.calls = _AsyncSipDomainAuthCallsResource(transport)
        self.registrations = _AsyncSipDomainAuthRegistrationsResource(transport)


class SipDomainsAsyncResource(AsyncResource):
    def __init__(self, transport: object) -> None:
        super().__init__(transport)  # type: ignore[arg-type]
        self.auth = _AsyncSipDomainAuthResource(transport)

    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipDomainList:
        return SipDomainList.model_validate(
            await self._t.request(
                "GET",
                self._path("SIP", "Domains"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def create(
        self,
        *,
        domain_name: str,
        friendly_name: str | None = None,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        voice_status_callback_url: str | None = None,
        voice_status_callback_method: str | None = None,
        sip_registration: bool | None = None,
        secure: bool | None = None,
        emergency_calling_enabled: bool | None = None,
        byoc_trunk_sid: str | None = None,
        emergency_caller_sid: str | None = None,
    ) -> SipDomain:
        return SipDomain.model_validate(
            await self._t.request(
                "POST",
                self._path("SIP", "Domains"),
                data=_create_domain_form(
                    domain_name=domain_name,
                    friendly_name=friendly_name,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    voice_status_callback_url=voice_status_callback_url,
                    voice_status_callback_method=voice_status_callback_method,
                    sip_registration=sip_registration,
                    secure=secure,
                    emergency_calling_enabled=emergency_calling_enabled,
                    byoc_trunk_sid=byoc_trunk_sid,
                    emergency_caller_sid=emergency_caller_sid,
                ),
            )
        )

    async def fetch(self, domain_sid: str) -> SipDomain:
        return SipDomain.model_validate(
            await self._t.request("GET", self._path("SIP", "Domains", domain_sid))
        )

    async def update(
        self,
        domain_sid: str,
        *,
        friendly_name: str | None = None,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        voice_status_callback_url: str | None = None,
        voice_status_callback_method: str | None = None,
        sip_registration: bool | None = None,
        secure: bool | None = None,
        emergency_calling_enabled: bool | None = None,
        byoc_trunk_sid: str | None = None,
        emergency_caller_sid: str | None = None,
    ) -> SipDomain:
        return SipDomain.model_validate(
            await self._t.request(
                "POST",
                self._path("SIP", "Domains", domain_sid),
                data=_update_domain_form(
                    friendly_name=friendly_name,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    voice_status_callback_url=voice_status_callback_url,
                    voice_status_callback_method=voice_status_callback_method,
                    sip_registration=sip_registration,
                    secure=secure,
                    emergency_calling_enabled=emergency_calling_enabled,
                    byoc_trunk_sid=byoc_trunk_sid,
                    emergency_caller_sid=emergency_caller_sid,
                ),
            )
        )

    async def delete(self, domain_sid: str) -> None:
        await self._t.request("DELETE", self._path("SIP", "Domains", domain_sid))

    def credential_list_mappings(
        self, domain_sid: str
    ) -> _AsyncSipDomainCredentialListMappingsResource:
        return _AsyncSipDomainCredentialListMappingsResource(self._t, domain_sid)

    def ip_access_control_list_mappings(
        self, domain_sid: str
    ) -> _AsyncSipDomainIpAccessControlListMappingsResource:
        return _AsyncSipDomainIpAccessControlListMappingsResource(self._t, domain_sid)


class _AsyncSipCredentialsResource(AsyncResource):
    def __init__(self, transport: object, credential_list_sid: str) -> None:
        super().__init__(transport)  # type: ignore[arg-type]
        self._cl_sid = credential_list_sid

    def _root(self, *tail: str) -> str:
        return self._path(
            "SIP", "CredentialLists", self._cl_sid, "Credentials", *tail
        )

    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipCredentialListPage:
        return SipCredentialListPage.model_validate(
            await self._t.request(
                "GET",
                self._root(),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def create(self, *, username: str, password: str) -> SipCredential:
        body = CreateSipCredentialRequest(
            Username=username, Password=password
        ).to_form()
        return SipCredential.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def fetch(self, credential_sid: str) -> SipCredential:
        return SipCredential.model_validate(
            await self._t.request("GET", self._root(credential_sid))
        )

    async def update(self, credential_sid: str, *, password: str) -> SipCredential:
        body = UpdateSipCredentialRequest(Password=password).to_form()
        return SipCredential.model_validate(
            await self._t.request("POST", self._root(credential_sid), data=body)
        )

    async def delete(self, credential_sid: str) -> None:
        await self._t.request("DELETE", self._root(credential_sid))


class SipCredentialListsAsyncResource(AsyncResource):
    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipCredentialListList:
        return SipCredentialListList.model_validate(
            await self._t.request(
                "GET",
                self._path("SIP", "CredentialLists"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def create(self, *, friendly_name: str) -> SipCredentialList:
        body = CreateSipCredentialListRequest(FriendlyName=friendly_name).to_form()
        return SipCredentialList.model_validate(
            await self._t.request(
                "POST", self._path("SIP", "CredentialLists"), data=body
            )
        )

    async def fetch(self, credential_list_sid: str) -> SipCredentialList:
        return SipCredentialList.model_validate(
            await self._t.request(
                "GET", self._path("SIP", "CredentialLists", credential_list_sid)
            )
        )

    async def update(
        self, credential_list_sid: str, *, friendly_name: str | None = None
    ) -> SipCredentialList:
        body = UpdateSipCredentialListRequest(FriendlyName=friendly_name).to_form()
        return SipCredentialList.model_validate(
            await self._t.request(
                "POST",
                self._path("SIP", "CredentialLists", credential_list_sid),
                data=body,
            )
        )

    async def delete(self, credential_list_sid: str) -> None:
        await self._t.request(
            "DELETE", self._path("SIP", "CredentialLists", credential_list_sid)
        )

    def credentials(
        self, credential_list_sid: str
    ) -> _AsyncSipCredentialsResource:
        return _AsyncSipCredentialsResource(self._t, credential_list_sid)


class _AsyncSipIpAddressesResource(AsyncResource):
    def __init__(self, transport: object, ipacl_sid: str) -> None:
        super().__init__(transport)  # type: ignore[arg-type]
        self._ipacl_sid = ipacl_sid

    def _root(self, *tail: str) -> str:
        return self._path(
            "SIP", "IpAccessControlLists", self._ipacl_sid, "IpAddresses", *tail
        )

    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipIpAddressList:
        return SipIpAddressList.model_validate(
            await self._t.request(
                "GET",
                self._root(),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def create(
        self,
        *,
        friendly_name: str,
        ip_address: str,
        cidr_prefix_length: int | None = None,
    ) -> SipIpAddress:
        body = CreateSipIpAddressRequest(
            FriendlyName=friendly_name,
            IpAddress=ip_address,
            CidrPrefixLength=cidr_prefix_length,
        ).to_form()
        return SipIpAddress.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def fetch(self, ip_address_sid: str) -> SipIpAddress:
        return SipIpAddress.model_validate(
            await self._t.request("GET", self._root(ip_address_sid))
        )

    async def update(
        self,
        ip_address_sid: str,
        *,
        friendly_name: str | None = None,
        ip_address: str | None = None,
        cidr_prefix_length: int | None = None,
    ) -> SipIpAddress:
        body = UpdateSipIpAddressRequest(
            FriendlyName=friendly_name,
            IpAddress=ip_address,
            CidrPrefixLength=cidr_prefix_length,
        ).to_form()
        return SipIpAddress.model_validate(
            await self._t.request("POST", self._root(ip_address_sid), data=body)
        )

    async def delete(self, ip_address_sid: str) -> None:
        await self._t.request("DELETE", self._root(ip_address_sid))


class SipIpAccessControlListsAsyncResource(AsyncResource):
    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> SipIpAccessControlListList:
        return SipIpAccessControlListList.model_validate(
            await self._t.request(
                "GET",
                self._path("SIP", "IpAccessControlLists"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def create(self, *, friendly_name: str) -> SipIpAccessControlList:
        body = CreateSipIpAccessControlListRequest(
            FriendlyName=friendly_name
        ).to_form()
        return SipIpAccessControlList.model_validate(
            await self._t.request(
                "POST", self._path("SIP", "IpAccessControlLists"), data=body
            )
        )

    async def fetch(self, ipacl_sid: str) -> SipIpAccessControlList:
        return SipIpAccessControlList.model_validate(
            await self._t.request(
                "GET", self._path("SIP", "IpAccessControlLists", ipacl_sid)
            )
        )

    async def update(
        self, ipacl_sid: str, *, friendly_name: str | None = None
    ) -> SipIpAccessControlList:
        body = UpdateSipIpAccessControlListRequest(
            FriendlyName=friendly_name
        ).to_form()
        return SipIpAccessControlList.model_validate(
            await self._t.request(
                "POST",
                self._path("SIP", "IpAccessControlLists", ipacl_sid),
                data=body,
            )
        )

    async def delete(self, ipacl_sid: str) -> None:
        await self._t.request(
            "DELETE", self._path("SIP", "IpAccessControlLists", ipacl_sid)
        )

    def ip_addresses(self, ipacl_sid: str) -> _AsyncSipIpAddressesResource:
        return _AsyncSipIpAddressesResource(self._t, ipacl_sid)


class SipAsyncResource:
    def __init__(self, transport: object) -> None:
        self.domains = SipDomainsAsyncResource(transport)
        self.credential_lists = SipCredentialListsAsyncResource(transport)
        self.ip_access_control_lists = SipIpAccessControlListsAsyncResource(transport)
