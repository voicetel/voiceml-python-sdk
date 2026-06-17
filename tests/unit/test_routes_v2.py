"""Tests for the Routes V2 (Inbound Processing Region) API — voiceml.routes_v2."""

from __future__ import annotations

from urllib.parse import parse_qs

from pytest_httpx import HTTPXMock

from voiceml import AsyncClient, Client

ACCOUNT_SID = "AC" + "f" * 32
API_KEY = "secret-key-1234"
BASE = "https://voiceml.voicetel.com"

DOMAIN_NAME = "ingress.example.com"
QQ_SID = "QQ" + "0" * 32


def _payload() -> dict:
    return {
        "sid": QQ_SID,
        "sip_domain": DOMAIN_NAME,
        "account_sid": ACCOUNT_SID,
        "friendly_name": "ingress",
        "voice_region": "us1",
        "url": f"https://voiceml.voicetel.com/v2/SipDomains/{DOMAIN_NAME}",
        "date_created": "2026-06-17T20:00:00Z",
        "date_updated": "2026-06-17T20:00:00Z",
    }


def test_routes_v2_resource_is_wired_on_client():
    c = Client(account_sid=ACCOUNT_SID, api_key=API_KEY)
    try:
        assert c.routes_v2 is not None
        assert c.routes_v2.sip_domains is not None
    finally:
        c.close()


def test_routes_v2_resource_is_wired_on_async_client():
    c = AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY)
    assert c.routes_v2 is not None
    assert c.routes_v2.sip_domains is not None


def test_routes_v2_sip_domains_fetch(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v2/SipDomains/{DOMAIN_NAME}",
        json=_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        rv = c.routes_v2.sip_domains.fetch(DOMAIN_NAME)
    assert rv.sid == QQ_SID
    assert rv.sip_domain == DOMAIN_NAME
    assert rv.voice_region == "us1"


def test_routes_v2_sip_domains_update_voice_region_only(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v2/SipDomains/{DOMAIN_NAME}",
        json=_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.routes_v2.sip_domains.update(DOMAIN_NAME, voice_region="us1")
    body = parse_qs(httpx_mock.get_request().content.decode(), keep_blank_values=True)
    assert body == {"VoiceRegion": ["us1"]}


def test_routes_v2_sip_domains_update_both_fields(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v2/SipDomains/{DOMAIN_NAME}",
        json=_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.routes_v2.sip_domains.update(
            DOMAIN_NAME, voice_region="ie1", friendly_name="renamed"
        )
    body = parse_qs(httpx_mock.get_request().content.decode(), keep_blank_values=True)
    assert body == {"VoiceRegion": ["ie1"], "FriendlyName": ["renamed"]}


def test_routes_v2_path_has_no_account_prefix(httpx_mock: HTTPXMock):
    """The /v2/ namespace is account-implicit (auth-derived) — no /2010-04-01/Accounts/.../ prefix."""
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v2/SipDomains/{DOMAIN_NAME}",
        json=_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.routes_v2.sip_domains.fetch(DOMAIN_NAME)
    req = httpx_mock.get_request()
    assert ACCOUNT_SID not in str(req.url)
    assert str(req.url).endswith(f"/v2/SipDomains/{DOMAIN_NAME}")
