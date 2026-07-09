"""``/v1`` + ``/v2`` Pricing surface — Twilio ``pricing.twilio.com`` (#18).

Read-only. Served on the default host (VoiceML has no pricing subdomain). Layout::

    client.pricing.v1.voice.countries.list / fetch
    client.pricing.v1.voice.numbers.fetch
    client.pricing.v1.messaging.countries.list / fetch
    client.pricing.v1.phone_numbers.countries.list / fetch
    client.pricing.v2.voice.countries.list / fetch
    client.pricing.v2.voice.numbers.fetch
    client.pricing.v2.trunking.countries.list / fetch
    client.pricing.v2.trunking.numbers.fetch

Every ``countries.list`` returns the shared :class:`PricingCountriesList`
envelope; ``fetch`` returns the product-specific country/number body.
"""

from __future__ import annotations

from urllib.parse import quote

from ..models import (
    PricingCountriesList,
    PricingMessagingCountry,
    PricingPhoneNumberCountry,
    PricingTrunkingCountry,
    PricingTrunkingNumber,
    PricingVoiceCountry,
    PricingVoiceCountryV2,
    PricingVoiceNumber,
    PricingVoiceNumberV2,
)


def _page_params(*, page_size: int | None) -> dict[str, object]:
    return {"PageSize": page_size}


# ===========================================================================
# Sync
# ===========================================================================


class _PricingCountriesResource:
    """``.../Countries`` list + per-country fetch (sync). ``model`` is the fetch body."""

    def __init__(self, transport: object, base_path: str, model: type) -> None:
        self._t = transport
        self._base = base_path
        self._model = model

    def list(self, *, page_size: int | None = None) -> PricingCountriesList:
        return PricingCountriesList.model_validate(
            self._t.request("GET", self._base, params=_page_params(page_size=page_size))
        )

    def fetch(self, iso_country: str) -> object:
        return self._model.model_validate(
            self._t.request("GET", f"{self._base}/{iso_country}")
        )


class _PricingV1VoiceNumbersResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def fetch(self, number: str) -> PricingVoiceNumber:
        return PricingVoiceNumber.model_validate(
            self._t.request("GET", f"/v1/Voice/Numbers/{quote(number, safe='')}")
        )


class _PricingV2VoiceNumbersResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def fetch(
        self, destination_number: str, *, origination_number: str | None = None
    ) -> PricingVoiceNumberV2:
        return PricingVoiceNumberV2.model_validate(
            self._t.request(
                "GET",
                f"/v2/Voice/Numbers/{quote(destination_number, safe='')}",
                params={"OriginationNumber": origination_number},
            )
        )


class _PricingV2TrunkingNumbersResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def fetch(
        self, destination_number: str, *, origination_number: str | None = None
    ) -> PricingTrunkingNumber:
        return PricingTrunkingNumber.model_validate(
            self._t.request(
                "GET",
                f"/v2/Trunking/Numbers/{quote(destination_number, safe='')}",
                params={"OriginationNumber": origination_number},
            )
        )


class _PricingV1Resource:
    def __init__(self, transport: object) -> None:
        self.voice = _PricingProduct(
            _PricingCountriesResource(transport, "/v1/Voice/Countries", PricingVoiceCountry),
            _PricingV1VoiceNumbersResource(transport),
        )
        self.messaging = _PricingProduct(
            _PricingCountriesResource(
                transport, "/v1/Messaging/Countries", PricingMessagingCountry
            ),
            None,
        )
        self.phone_numbers = _PricingProduct(
            _PricingCountriesResource(
                transport, "/v1/PhoneNumbers/Countries", PricingPhoneNumberCountry
            ),
            None,
        )


class _PricingV2Resource:
    def __init__(self, transport: object) -> None:
        self.voice = _PricingProduct(
            _PricingCountriesResource(
                transport, "/v2/Voice/Countries", PricingVoiceCountryV2
            ),
            _PricingV2VoiceNumbersResource(transport),
        )
        self.trunking = _PricingProduct(
            _PricingCountriesResource(
                transport, "/v2/Trunking/Countries", PricingTrunkingCountry
            ),
            _PricingV2TrunkingNumbersResource(transport),
        )


class _PricingProduct:
    """A pricing product group exposing ``.countries`` and optionally ``.numbers``."""

    def __init__(self, countries: object, numbers: object | None) -> None:
        self.countries = countries
        if numbers is not None:
            self.numbers = numbers


class PricingResource:
    """Holder for ``client.pricing.*`` (sync)."""

    def __init__(self, transport: object) -> None:
        self.v1 = _PricingV1Resource(transport)
        self.v2 = _PricingV2Resource(transport)


# ===========================================================================
# Async counterparts — same surface; methods are awaitable.
# ===========================================================================


class _PricingCountriesAsyncResource:
    def __init__(self, transport: object, base_path: str, model: type) -> None:
        self._t = transport
        self._base = base_path
        self._model = model

    async def list(self, *, page_size: int | None = None) -> PricingCountriesList:
        return PricingCountriesList.model_validate(
            await self._t.request(
                "GET", self._base, params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, iso_country: str) -> object:
        return self._model.model_validate(
            await self._t.request("GET", f"{self._base}/{iso_country}")
        )


class _PricingV1VoiceNumbersAsyncResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def fetch(self, number: str) -> PricingVoiceNumber:
        return PricingVoiceNumber.model_validate(
            await self._t.request("GET", f"/v1/Voice/Numbers/{quote(number, safe='')}")
        )


class _PricingV2VoiceNumbersAsyncResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def fetch(
        self, destination_number: str, *, origination_number: str | None = None
    ) -> PricingVoiceNumberV2:
        return PricingVoiceNumberV2.model_validate(
            await self._t.request(
                "GET",
                f"/v2/Voice/Numbers/{quote(destination_number, safe='')}",
                params={"OriginationNumber": origination_number},
            )
        )


class _PricingV2TrunkingNumbersAsyncResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def fetch(
        self, destination_number: str, *, origination_number: str | None = None
    ) -> PricingTrunkingNumber:
        return PricingTrunkingNumber.model_validate(
            await self._t.request(
                "GET",
                f"/v2/Trunking/Numbers/{quote(destination_number, safe='')}",
                params={"OriginationNumber": origination_number},
            )
        )


class _PricingV1AsyncResource:
    def __init__(self, transport: object) -> None:
        self.voice = _PricingProduct(
            _PricingCountriesAsyncResource(
                transport, "/v1/Voice/Countries", PricingVoiceCountry
            ),
            _PricingV1VoiceNumbersAsyncResource(transport),
        )
        self.messaging = _PricingProduct(
            _PricingCountriesAsyncResource(
                transport, "/v1/Messaging/Countries", PricingMessagingCountry
            ),
            None,
        )
        self.phone_numbers = _PricingProduct(
            _PricingCountriesAsyncResource(
                transport, "/v1/PhoneNumbers/Countries", PricingPhoneNumberCountry
            ),
            None,
        )


class _PricingV2AsyncResource:
    def __init__(self, transport: object) -> None:
        self.voice = _PricingProduct(
            _PricingCountriesAsyncResource(
                transport, "/v2/Voice/Countries", PricingVoiceCountryV2
            ),
            _PricingV2VoiceNumbersAsyncResource(transport),
        )
        self.trunking = _PricingProduct(
            _PricingCountriesAsyncResource(
                transport, "/v2/Trunking/Countries", PricingTrunkingCountry
            ),
            _PricingV2TrunkingNumbersAsyncResource(transport),
        )


class PricingAsyncResource:
    """Holder for ``client.pricing.*`` (async)."""

    def __init__(self, transport: object) -> None:
        self.v1 = _PricingV1AsyncResource(transport)
        self.v2 = _PricingV2AsyncResource(transport)
