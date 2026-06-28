"""``/v2/SipDomains/{SipDomain}`` + ``/v2/PhoneNumbers/{PhoneNumber}`` —
Twilio Routes V2 Inbound Processing Region.

Exposed under ``client.routes_v2.sip_domains.*`` and
``client.routes_v2.phone_numbers.*``. Both endpoints are account-implicit
(auth-derived) and keyed by the natural identifier:

- ``sip_domains`` — by registrable SIP domain name.
- ``phone_numbers`` — by E.164 phone number (e.g. ``+18005551234``) or the
  ``PN…`` sid. The natural-key value is URL-encoded so the leading ``+``
  in an E.164 survives routing.

Sync and async variants.
"""

from __future__ import annotations

from urllib.parse import quote

from ..models import (
    RoutesV2PhoneNumber,
    RoutesV2SipDomain,
    UpdateRoutesV2PhoneNumberRequest,
    UpdateRoutesV2SipDomainRequest,
)


def _update_form(*, voice_region: str | None, friendly_name: str | None) -> dict[str, object]:
    return UpdateRoutesV2SipDomainRequest(
        VoiceRegion=voice_region,
        FriendlyName=friendly_name,
    ).to_form()


def _phone_number_update_form(
    *, voice_region: str | None, friendly_name: str | None
) -> dict[str, object]:
    return UpdateRoutesV2PhoneNumberRequest(
        VoiceRegion=voice_region,
        FriendlyName=friendly_name,
    ).to_form()


def _encode_phone_number(value: str) -> str:
    """URL-encode a phone-number key.

    The Routes V2 PhoneNumbers endpoint accepts either an E.164 number
    (``+18005551234``) or a ``PN…`` sid. PN sids ([A-Za-z0-9]) pass through
    unchanged; E.164 has its leading ``+`` encoded to ``%2B`` so routing
    treats it as a literal character rather than a space.
    """
    return quote(value, safe="")


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


class RoutesV2PhoneNumbersResource:
    """Operations on ``/v2/PhoneNumbers/{PhoneNumber}`` (sync)."""

    def __init__(self, transport: object) -> None:
        self._t = transport  # type: ignore[assignment]

    def fetch(self, phone_number: str) -> RoutesV2PhoneNumber:
        """Fetch the Inbound Processing Region binding for ``phone_number``.

        ``phone_number`` may be an E.164 value or the ``PN…`` sid.
        """
        return RoutesV2PhoneNumber.model_validate(
            self._t.request(
                "GET", f"/v2/PhoneNumbers/{_encode_phone_number(phone_number)}"
            )
        )

    def update(
        self,
        phone_number: str,
        *,
        voice_region: str | None = None,
        friendly_name: str | None = None,
    ) -> RoutesV2PhoneNumber:
        """Set ``voice_region`` and/or ``friendly_name`` for ``phone_number``."""
        return RoutesV2PhoneNumber.model_validate(
            self._t.request(
                "POST",
                f"/v2/PhoneNumbers/{_encode_phone_number(phone_number)}",
                data=_phone_number_update_form(
                    voice_region=voice_region, friendly_name=friendly_name
                ),
            )
        )


class RoutesV2Resource:
    """Holder for ``client.routes_v2.*`` sub-resources."""

    def __init__(self, transport: object) -> None:
        self.sip_domains = RoutesV2SipDomainsResource(transport)
        self.phone_numbers = RoutesV2PhoneNumbersResource(transport)


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


class RoutesV2PhoneNumbersAsyncResource:
    def __init__(self, transport: object) -> None:
        self._t = transport  # type: ignore[assignment]

    async def fetch(self, phone_number: str) -> RoutesV2PhoneNumber:
        return RoutesV2PhoneNumber.model_validate(
            await self._t.request(
                "GET", f"/v2/PhoneNumbers/{_encode_phone_number(phone_number)}"
            )
        )

    async def update(
        self,
        phone_number: str,
        *,
        voice_region: str | None = None,
        friendly_name: str | None = None,
    ) -> RoutesV2PhoneNumber:
        return RoutesV2PhoneNumber.model_validate(
            await self._t.request(
                "POST",
                f"/v2/PhoneNumbers/{_encode_phone_number(phone_number)}",
                data=_phone_number_update_form(
                    voice_region=voice_region, friendly_name=friendly_name
                ),
            )
        )


class RoutesV2AsyncResource:
    def __init__(self, transport: object) -> None:
        self.sip_domains = RoutesV2SipDomainsAsyncResource(transport)
        self.phone_numbers = RoutesV2PhoneNumbersAsyncResource(transport)
