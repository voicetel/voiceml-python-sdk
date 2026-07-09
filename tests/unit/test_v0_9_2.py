"""Wire-shape tests for the v0.9.2 surface: per-product host routing, Messaging
Service (#16), and Pricing v1/v2 (#18).

Messaging Service must ride ``messaging.voicetel.com`` (that host is what
disambiguates it from Conversation Service on the shared ``/v1/Services`` path).
Pricing rides the default host. Host derivation is unit-tested directly.
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs

import pytest
from pytest_httpx import HTTPXMock

from voiceml import AsyncClient, Client
from voiceml._hosts import resolve_product_base_urls

ACCOUNT_SID = "AC" + "f" * 32
API_KEY = "secret-key-1234"
BASE = "https://voiceml.voicetel.com"
MSG = "https://messaging.voicetel.com"
CONV = "https://conversations.voicetel.com"


def _meta() -> dict:
    return {
        "first_page_url": f"{MSG}/v1/Services?Page=0",
        "next_page_url": None,
        "previous_page_url": None,
        "url": f"{MSG}/v1/Services",
        "page": 0,
        "page_size": 50,
        "key": "services",
    }


# ---------------------------------------------------------------------------
# Host resolution
# ---------------------------------------------------------------------------


def test_host_derivation_from_default():
    default, messaging, conversations = resolve_product_base_urls(BASE)
    assert default == BASE
    assert messaging == MSG
    assert conversations == CONV


def test_host_derivation_regional():
    default, messaging, conversations = resolve_product_base_urls(
        "https://east-1.us.voiceml.voicetel.com"
    )
    assert default == "https://east-1.us.voiceml.voicetel.com"
    assert messaging == "https://east-1.us.messaging.voicetel.com"
    assert conversations == "https://east-1.us.conversations.voicetel.com"


def test_host_derivation_self_hosted_falls_back_to_single_host():
    # A custom host has no `voiceml` label to swap — every product stays on it,
    # so a single-host deployment keeps working.
    default, messaging, conversations = resolve_product_base_urls("https://pbx.acme.com")
    assert default == messaging == conversations == "https://pbx.acme.com"


def test_host_derivation_explicit_overrides_win():
    default, messaging, conversations = resolve_product_base_urls(
        "https://pbx.acme.com",
        messaging_base_url="https://msg.acme.com",
        conversations_base_url="https://conv.acme.com/",
    )
    assert default == "https://pbx.acme.com"
    assert messaging == "https://msg.acme.com"
    assert conversations == "https://conv.acme.com"


def test_v0_9_2_resources_wired():
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        assert c.messaging_v1.services is not None
        assert c.pricing.v1.voice.countries is not None
        assert c.pricing.v1.voice.numbers is not None
        assert c.pricing.v1.messaging.countries is not None
        assert c.pricing.v1.phone_numbers.countries is not None
        assert c.pricing.v2.voice.countries is not None
        assert c.pricing.v2.voice.numbers is not None
        assert c.pricing.v2.trunking.countries is not None
        assert c.pricing.v2.trunking.numbers is not None


# ---------------------------------------------------------------------------
# Messaging Service — CRUD on the messaging host
# ---------------------------------------------------------------------------


def _messaging_service_payload(sid: str = "MG" + "0" * 32) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "friendly_name": "alerts",
        "inbound_request_url": "https://example.com/in",
        "sticky_sender": True,
        "date_created": "2026-07-08T00:00:00Z",
        "date_updated": "2026-07-08T00:00:00Z",
        "url": f"{MSG}/v1/Services/{sid}",
    }


def test_messaging_service_crud_on_messaging_host(httpx_mock: HTTPXMock):
    sid = "MG" + "1" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{MSG}/v1/Services",
        json=_messaging_service_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(MSG)}/v1/Services(\?.*)?$"),
        json={"services": [_messaging_service_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{MSG}/v1/Services/{sid}",
        json=_messaging_service_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{MSG}/v1/Services/{sid}",
        json=_messaging_service_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{MSG}/v1/Services/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        created = c.messaging_v1.services.create(
            friendly_name="alerts",
            inbound_request_url="https://example.com/in",
            sticky_sender=True,
        )
        listed = c.messaging_v1.services.list(page_size=25)
        fetched = c.messaging_v1.services.fetch(sid)
        updated = c.messaging_v1.services.update(sid, friendly_name="renamed")
        c.messaging_v1.services.delete(sid)

    assert created.sid == sid
    assert created.sid.startswith("MG")
    assert len(listed.services) == 1
    assert fetched.sid == sid
    assert updated.sid == sid

    requests = httpx_mock.get_requests()
    # Every request must have hit the messaging host, not the default one.
    assert all(r.url.host == "messaging.voicetel.com" for r in requests)
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body["FriendlyName"] == ["alerts"]
    assert create_body["InboundRequestUrl"] == ["https://example.com/in"]
    assert create_body["StickySender"] == ["true"]
    assert "PageSize=25" in requests[1].url.query.decode()
    update_body = parse_qs(requests[3].content.decode(), keep_blank_values=True)
    assert update_body == {"FriendlyName": ["renamed"]}


def test_messaging_service_host_override(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(r"https://msg\.acme\.com/v1/Services(\?.*)?$"),
        json={"services": [], "meta": _meta()},
    )
    with Client(
        account_sid=ACCOUNT_SID,
        api_key=API_KEY,
        base_url="https://pbx.acme.com",
        messaging_base_url="https://msg.acme.com",
    ) as c:
        c.messaging_v1.services.list()
    assert httpx_mock.get_requests()[0].url.host == "msg.acme.com"


# ---------------------------------------------------------------------------
# Pricing v1/v2 — read-only on the default host
# ---------------------------------------------------------------------------


def test_pricing_v1_voice_countries_and_number(httpx_mock: HTTPXMock):
    countries = {
        "countries": [
            {
                "country": "United States",
                "iso_country": "US",
                "url": f"{BASE}/v1/Voice/Countries/US",
            }
        ],
        "meta": {"page": 0, "page_size": 50},
    }
    country = {
        "country": "United States",
        "iso_country": "US",
        "outbound_prefix_prices": [
            {
                "prefixes": ["1"],
                "base_price": "0.013",
                "current_price": "0.013",
                "friendly_name": "United States & Canada",
            }
        ],
        "inbound_call_prices": [
            {"base_price": "0.0085", "current_price": "0.0085", "number_type": "local"}
        ],
        "price_unit": "USD",
        "url": f"{BASE}/v1/Voice/Countries/US",
    }
    number = {
        "number": "+18005551234",
        "country": "United States",
        "iso_country": "US",
        "outbound_call_price": {"base_price": "0.013", "current_price": "0.013"},
        "inbound_call_price": {
            "base_price": "0.0085",
            "current_price": "0.0085",
            "number_type": "toll free",
        },
        "price_unit": "USD",
        "url": f"{BASE}/v1/Voice/Numbers/+18005551234",
    }
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Voice/Countries(\?.*)?$"),
        json=countries,
    )
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/v1/Voice/Countries/US", json=country
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Voice/Numbers/%2B18005551234",
        json=number,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        listed = c.pricing.v1.voice.countries.list()
        fetched = c.pricing.v1.voice.countries.fetch("US")
        num = c.pricing.v1.voice.numbers.fetch("+18005551234")
    assert listed.countries[0].iso_country == "US"
    assert fetched.outbound_prefix_prices[0].prefixes == ["1"]
    assert num.inbound_call_price.number_type == "toll free"
    assert all(
        r.url.host == "voiceml.voicetel.com" for r in httpx_mock.get_requests()
    )


def test_pricing_v2_voice_number_with_origination(httpx_mock: HTTPXMock):
    payload = {
        "destination_number": "+18005551234",
        "origination_number": "+15551112222",
        "country": "United States",
        "iso_country": "US",
        "outbound_call_prices": [
            {
                "origination_prefixes": ["1"],
                "base_price": "0.013",
                "current_price": "0.013",
            }
        ],
        "inbound_call_price": {
            "base_price": "0.0085",
            "current_price": "0.0085",
            "number_type": "local",
        },
        "price_unit": "USD",
        "url": f"{BASE}/v2/Voice/Numbers/+18005551234",
    }
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v2/Voice/Numbers/%2B18005551234(\?.*)?$"),
        json=payload,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        got = c.pricing.v2.voice.numbers.fetch(
            "+18005551234", origination_number="+15551112222"
        )
    assert got.origination_number == "+15551112222"
    q = httpx_mock.get_requests()[0].url.query.decode()
    assert "OriginationNumber=%2B15551112222" in q


def test_pricing_v2_trunking_country(httpx_mock: HTTPXMock):
    payload = {
        "country": "United States",
        "iso_country": "US",
        "terminating_prefix_prices": [
            {
                "origination_prefixes": ["1"],
                "destination_prefixes": ["1"],
                "base_price": "0.013",
                "current_price": "0.013",
                "friendly_name": "US",
            }
        ],
        "originating_call_prices": [
            {"base_price": "0.0085", "current_price": "0.0085", "number_type": "local"}
        ],
        "price_unit": "USD",
        "url": f"{BASE}/v2/Trunking/Countries/US",
    }
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/v2/Trunking/Countries/US", json=payload
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        got = c.pricing.v2.trunking.countries.fetch("US")
    assert got.terminating_prefix_prices[0].friendly_name == "US"


# ---------------------------------------------------------------------------
# Async smoke
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_messaging_service_create(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{MSG}/v1/Services",
        json=_messaging_service_payload(),
        status_code=201,
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        created = await c.messaging_v1.services.create(friendly_name="alerts")
    assert created.sid.startswith("MG")
    assert httpx_mock.get_requests()[0].url.host == "messaging.voicetel.com"


@pytest.mark.asyncio
async def test_async_pricing_v1_messaging_countries_list(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Messaging/Countries(\?.*)?$"),
        json={"countries": [], "meta": {"page": 0}},
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        listed = await c.pricing.v1.messaging.countries.list()
    assert listed.countries == []
    assert httpx_mock.get_requests()[0].url.host == "voiceml.voicetel.com"
