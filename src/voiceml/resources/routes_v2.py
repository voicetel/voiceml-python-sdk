"""``/v2/SipDomains/{SipDomain}`` — Twilio Routes V2 Inbound Processing Region.

Exposed under ``client.routes_v2.sip_domains.*``. Keyed by SIP domain name
(not the SipDomain SID) — the account is resolved from HTTP Basic auth.

Sync and async variants.
"""

from __future__ import annotations

from ..models import (
    RoutesV2SipDomain,
    UpdateRoutesV2SipDomainRequest,
)


def _update_form(*, voice_region: str | None, friendly_name: str | None) -> dict[str, object]:
    return UpdateRoutesV2SipDomainRequest(
        VoiceRegion=voice_region,
        FriendlyName=friendly_name,
    ).to_form()


class RoutesV2SipDomainsResource:
    """Operations on ``/v2/SipDomains/{SipDomain}`` (sync)."""

    def __init__(self, transport: object) -> None:
        self._t = transport  # type: ignore[assignment]

    def fetch(self, domain_name: str) -> RoutesV2SipDomain:
        """Fetch the Inbound Processing Region binding for ``domain_name``."""
        return RoutesV2SipDomain.model_validate(
            self._t.request("GET", f"/v2/SipDomains/{domain_name}")
        )

    def update(
        self,
        domain_name: str,
        *,
        voice_region: str | None = None,
        friendly_name: str | None = None,
    ) -> RoutesV2SipDomain:
        """Set ``voice_region`` and/or ``friendly_name`` for ``domain_name``.

        Both fields optional; pass only the ones you want to change.
        """
        return RoutesV2SipDomain.model_validate(
            self._t.request(
                "POST",
                f"/v2/SipDomains/{domain_name}",
                data=_update_form(voice_region=voice_region, friendly_name=friendly_name),
            )
        )


class RoutesV2Resource:
    """Holder for ``client.routes_v2.*`` sub-resources."""

    def __init__(self, transport: object) -> None:
        self.sip_domains = RoutesV2SipDomainsResource(transport)


# ===========================================================================
# Async counterparts
# ===========================================================================


class RoutesV2SipDomainsAsyncResource:
    def __init__(self, transport: object) -> None:
        self._t = transport  # type: ignore[assignment]

    async def fetch(self, domain_name: str) -> RoutesV2SipDomain:
        return RoutesV2SipDomain.model_validate(
            await self._t.request("GET", f"/v2/SipDomains/{domain_name}")
        )

    async def update(
        self,
        domain_name: str,
        *,
        voice_region: str | None = None,
        friendly_name: str | None = None,
    ) -> RoutesV2SipDomain:
        return RoutesV2SipDomain.model_validate(
            await self._t.request(
                "POST",
                f"/v2/SipDomains/{domain_name}",
                data=_update_form(voice_region=voice_region, friendly_name=friendly_name),
            )
        )


class RoutesV2AsyncResource:
    def __init__(self, transport: object) -> None:
        self.sip_domains = RoutesV2SipDomainsAsyncResource(transport)
