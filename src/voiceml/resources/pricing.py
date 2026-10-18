"""``/v1`` + ``/v2`` Pricing surface — Twilio-compatible pricing lookups.

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

from typing import Generic, TypeVar

from pydantic import BaseModel

from .._http import AsyncTransport, Transport
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
from ._base import path, seg

ModelT = TypeVar("ModelT", bound=BaseModel)
CountriesT = TypeVar("CountriesT")
NumbersT = TypeVar("NumbersT")


def _page_params(*, page_size: int | None) -> dict[str, object]:
    return {"PageSize": page_size}


# ===========================================================================
# Sync
# ===========================================================================


class _PricingCountriesResource(Generic[ModelT]):
    """``.../Countries`` list + per-country fetch (sync). ``model`` is the fetch body."""

    def __init__(self, transport: Transport, base_path: str, model: type[ModelT]) -> None:
        self._t = transport
        self._base = base_path
        self._model = model

    def list(self, *, page_size: int | None = None) -> PricingCountriesList:
        return PricingCountriesList.model_validate(
            self._t.request("GET", self._base, params=_page_params(page_size=page_size))
        )

    def fetch(self, iso_country: str) -> ModelT:
        return self._model.model_validate(
            self._t.request("GET", f"{self._base}/{seg(iso_country)}")
        )


class _PricingV1VoiceNumbersResource:
    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def fetch(self, number: str) -> PricingVoiceNumber:
        return PricingVoiceNumber.model_validate(
            self._t.request("GET", path("v1", "Voice", "Numbers", number))
        )


class _PricingV2VoiceNumbersResource:
    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def fetch(
        self, destination_number: str, *, origination_number: str | None = None
    ) -> PricingVoiceNumberV2:
        return PricingVoiceNumberV2.model_validate(
            self._t.request(
                "GET",
                path("v2", "Voice", "Numbers", destination_number),
                params={"OriginationNumber": origination_number},
            )
        )


class _PricingV2TrunkingNumbersResource:
    def __init__(self, transport: Transport) -> None:
        self._t = transport

    def fetch(
        self, destination_number: str, *, origination_number: str | None = None
    ) -> PricingTrunkingNumber:
        return PricingTrunkingNumber.model_validate(
            self._t.request(
                "GET",
                path("v2", "Trunking", "Numbers", destination_number),
                params={"OriginationNumber": origination_number},
            )
        )


class _PricingV1Resource:
    def __init__(self, transport: Transport) -> None:
        self.voice = _PricingProduct(
            _PricingCountriesResource(
                transport, path("v1", "Voice", "Countries"), PricingVoiceCountry
            ),
            _PricingV1VoiceNumbersResource(transport),
        )
        self.messaging = _PricingCountriesOnlyProduct(
            _PricingCountriesResource(
                transport, path("v1", "Messaging", "Countries"), PricingMessagingCountry
            ),
        )
        self.phone_numbers = _PricingCountriesOnlyProduct(
            _PricingCountriesResource(
                transport, path("v1", "PhoneNumbers", "Countries"), PricingPhoneNumberCountry
            ),
        )


class _PricingV2Resource:
    def __init__(self, transport: Transport) -> None:
        self.voice = _PricingProduct(
            _PricingCountriesResource(
                transport, path("v2", "Voice", "Countries"), PricingVoiceCountryV2
            ),
            _PricingV2VoiceNumbersResource(transport),
        )
        self.trunking = _PricingProduct(
            _PricingCountriesResource(
                transport, path("v2", "Trunking", "Countries"), PricingTrunkingCountry
            ),
            _PricingV2TrunkingNumbersResource(transport),
        )


class _PricingProduct(Generic[CountriesT, NumbersT]):
    """A pricing product group exposing ``.countries`` and ``.numbers``."""

    def __init__(self, countries: CountriesT, numbers: NumbersT) -> None:
        self.countries = countries
        self.numbers = numbers


class _PricingCountriesOnlyProduct(Generic[CountriesT]):
    """A pricing product group exposing only ``.countries``."""

    def __init__(self, countries: CountriesT) -> None:
        self.countries = countries


class PricingResource:
    """Holder for ``client.pricing.*`` (sync)."""

    def __init__(self, transport: Transport) -> None:
        self.v1 = _PricingV1Resource(transport)
        self.v2 = _PricingV2Resource(transport)


# ===========================================================================
# Async counterparts — same surface; methods are awaitable.
# ===========================================================================


class _PricingCountriesAsyncResource(Generic[ModelT]):
    def __init__(self, transport: AsyncTransport, base_path: str, model: type[ModelT]) -> None:
        self._t = transport
        self._base = base_path
        self._model = model

    async def list(self, *, page_size: int | None = None) -> PricingCountriesList:
        return PricingCountriesList.model_validate(
            await self._t.request("GET", self._base, params=_page_params(page_size=page_size))
        )

    async def fetch(self, iso_country: str) -> ModelT:
        return self._model.model_validate(
            await self._t.request("GET", f"{self._base}/{seg(iso_country)}")
        )


class _PricingV1VoiceNumbersAsyncResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def fetch(self, number: str) -> PricingVoiceNumber:
        return PricingVoiceNumber.model_validate(
            await self._t.request("GET", path("v1", "Voice", "Numbers", number))
        )


class _PricingV2VoiceNumbersAsyncResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def fetch(
        self, destination_number: str, *, origination_number: str | None = None
    ) -> PricingVoiceNumberV2:
        return PricingVoiceNumberV2.model_validate(
            await self._t.request(
                "GET",
                path("v2", "Voice", "Numbers", destination_number),
                params={"OriginationNumber": origination_number},
            )
        )


class _PricingV2TrunkingNumbersAsyncResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    async def fetch(
        self, destination_number: str, *, origination_number: str | None = None
    ) -> PricingTrunkingNumber:
        return PricingTrunkingNumber.model_validate(
            await self._t.request(
                "GET",
                path("v2", "Trunking", "Numbers", destination_number),
                params={"OriginationNumber": origination_number},
            )
        )


class _PricingV1AsyncResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self.voice = _PricingProduct(
            _PricingCountriesAsyncResource(
                transport, path("v1", "Voice", "Countries"), PricingVoiceCountry
            ),
            _PricingV1VoiceNumbersAsyncResource(transport),
        )
        self.messaging = _PricingCountriesOnlyProduct(
            _PricingCountriesAsyncResource(
                transport, path("v1", "Messaging", "Countries"), PricingMessagingCountry
            ),
        )
        self.phone_numbers = _PricingCountriesOnlyProduct(
            _PricingCountriesAsyncResource(
                transport, path("v1", "PhoneNumbers", "Countries"), PricingPhoneNumberCountry
            ),
        )


class _PricingV2AsyncResource:
    def __init__(self, transport: AsyncTransport) -> None:
        self.voice = _PricingProduct(
            _PricingCountriesAsyncResource(
                transport, path("v2", "Voice", "Countries"), PricingVoiceCountryV2
            ),
            _PricingV2VoiceNumbersAsyncResource(transport),
        )
        self.trunking = _PricingProduct(
            _PricingCountriesAsyncResource(
                transport, path("v2", "Trunking", "Countries"), PricingTrunkingCountry
            ),
            _PricingV2TrunkingNumbersAsyncResource(transport),
        )


class PricingAsyncResource:
    """Holder for ``client.pricing.*`` (async)."""

    def __init__(self, transport: AsyncTransport) -> None:
        self.v1 = _PricingV1AsyncResource(transport)
        self.v2 = _PricingV2AsyncResource(transport)
