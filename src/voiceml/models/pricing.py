"""Pricing v1/v2 resources — Twilio ``pricing.twilio.com`` REST surface (#18).

VoiceML has no dedicated pricing subdomain, so these live on the default host
(``voiceml.voicetel.com``) under ``/v1`` and ``/v2``. All operations are
read-only ``GET`` s. VoiceML is NANP-only: every ``Countries`` list carries
exactly one entry (the tenant's own country), and a ``Numbers`` fetch 404s for
a non-NANP destination.
"""

from __future__ import annotations

from pydantic import Field

from ._base import _Base
from .voice_v1 import VoiceV1Meta

# ---------------------------------------------------------------------------
# Price leaves
# ---------------------------------------------------------------------------


class PricingInboundCallPrice(_Base):
    base_price: str | None = None
    current_price: str | None = None
    number_type: str | None = None


class PricingOutboundCallPrice(_Base):
    base_price: str | None = None
    current_price: str | None = None


class PricingOutboundCallPriceWithOrigin(_Base):
    origination_prefixes: list[str] = Field(default_factory=list)
    base_price: str | None = None
    current_price: str | None = None


class PricingOutboundPrefixPrice(_Base):
    prefixes: list[str] = Field(default_factory=list)
    base_price: str | None = None
    current_price: str | None = None
    friendly_name: str | None = None


class PricingOutboundPrefixPriceWithOrigin(_Base):
    origination_prefixes: list[str] = Field(default_factory=list)
    destination_prefixes: list[str] = Field(default_factory=list)
    base_price: str | None = None
    current_price: str | None = None
    friendly_name: str | None = None


class PricingOutboundSMSPrice(_Base):
    carrier: str | None = None
    mcc: str | None = None
    mnc: str | None = None
    prices: list[PricingInboundCallPrice] = Field(default_factory=list)


class PricingPhoneNumberPrice(_Base):
    number_type: str | None = None
    base_price: str | None = None
    current_price: str | None = None


# ---------------------------------------------------------------------------
# Countries list envelope
# ---------------------------------------------------------------------------


class PricingCountryRef(_Base):
    country: str | None = None
    iso_country: str | None = None
    url: str | None = None


class PricingCountriesList(_Base):
    countries: list[PricingCountryRef] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


# ---------------------------------------------------------------------------
# Pricing v1 country / number bodies
# ---------------------------------------------------------------------------


class PricingVoiceCountry(_Base):
    country: str | None = None
    iso_country: str | None = None
    outbound_prefix_prices: list[PricingOutboundPrefixPrice] = Field(
        default_factory=list
    )
    inbound_call_prices: list[PricingInboundCallPrice] = Field(default_factory=list)
    price_unit: str | None = None
    url: str | None = None


class PricingVoiceNumber(_Base):
    number: str | None = None
    country: str | None = None
    iso_country: str | None = None
    outbound_call_price: PricingOutboundCallPrice | None = None
    inbound_call_price: PricingInboundCallPrice | None = None
    price_unit: str | None = None
    url: str | None = None


class PricingMessagingCountry(_Base):
    country: str | None = None
    iso_country: str | None = None
    outbound_sms_prices: list[PricingOutboundSMSPrice] = Field(default_factory=list)
    inbound_sms_prices: list[PricingInboundCallPrice] = Field(default_factory=list)
    price_unit: str | None = None
    url: str | None = None


class PricingPhoneNumberCountry(_Base):
    country: str | None = None
    iso_country: str | None = None
    phone_number_prices: list[PricingPhoneNumberPrice] = Field(default_factory=list)
    price_unit: str | None = None
    url: str | None = None


# ---------------------------------------------------------------------------
# Pricing v2 country / number bodies
# ---------------------------------------------------------------------------


class PricingVoiceCountryV2(_Base):
    country: str | None = None
    iso_country: str | None = None
    outbound_prefix_prices: list[PricingOutboundPrefixPriceWithOrigin] = Field(
        default_factory=list
    )
    inbound_call_prices: list[PricingInboundCallPrice] = Field(default_factory=list)
    price_unit: str | None = None
    url: str | None = None


class PricingVoiceNumberV2(_Base):
    destination_number: str | None = None
    origination_number: str | None = None
    country: str | None = None
    iso_country: str | None = None
    outbound_call_prices: list[PricingOutboundCallPriceWithOrigin] = Field(
        default_factory=list
    )
    inbound_call_price: PricingInboundCallPrice | None = None
    price_unit: str | None = None
    url: str | None = None


class PricingTrunkingCountry(_Base):
    country: str | None = None
    iso_country: str | None = None
    terminating_prefix_prices: list[PricingOutboundPrefixPriceWithOrigin] = Field(
        default_factory=list
    )
    originating_call_prices: list[PricingInboundCallPrice] = Field(default_factory=list)
    price_unit: str | None = None
    url: str | None = None


class PricingTrunkingNumber(_Base):
    destination_number: str | None = None
    origination_number: str | None = None
    country: str | None = None
    iso_country: str | None = None
    terminating_prefix_prices: list[PricingOutboundPrefixPriceWithOrigin] = Field(
        default_factory=list
    )
    originating_call_price: PricingInboundCallPrice | None = None
    price_unit: str | None = None
    url: str | None = None
