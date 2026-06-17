"""Unit tests for the SIP Trunking resources — voiceml.sip.*.

Wire-shape assertions only (no network). Uses pytest-httpx like the rest
of the suite.
"""

from __future__ import annotations

from urllib.parse import parse_qs

from pytest_httpx import HTTPXMock

from voiceml import AsyncClient, Client

ACCOUNT_SID = "AC" + "f" * 32
API_KEY = "secret-key-1234"
BASE = "https://voiceml.voicetel.com"

DOMAIN_SID = "SD" + "1" * 32
CL_SID = "CL" + "2" * 32
CR_SID = "CR" + "3" * 32
ACL_SID = "AL" + "4" * 32
IP_SID = "IP" + "5" * 32
MAPPING_SID = "CL" + "9" * 32  # mappings echo the bound resource sid


def _form(content: bytes) -> dict[str, list[str]]:
    return parse_qs(content.decode(), keep_blank_values=True)


def _domain_payload(sid: str = DOMAIN_SID, domain_name: str = "ingress.example.com") -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "api_version": "2010-04-01",
        "domain_name": domain_name,
        "friendly_name": "ingress",
        "voice_url": None,
        "voice_method": None,
        "voice_fallback_url": None,
        "voice_fallback_method": None,
        "voice_status_callback_url": None,
        "voice_status_callback_method": None,
        "sip_registration": False,
        "emergency_calling_enabled": False,
        "secure": True,
        "byoc_trunk_sid": None,
        "emergency_caller_sid": None,
        "auth_type": None,
        "date_created": "Mon, 17 Jun 2026 12:00:00 +0000",
        "date_updated": "Mon, 17 Jun 2026 12:00:00 +0000",
        "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{sid}.json",
    }


def _credential_list_payload(sid: str = CL_SID) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "friendly_name": "office-handsets",
        "date_created": "Mon, 17 Jun 2026 12:00:00 +0000",
        "date_updated": "Mon, 17 Jun 2026 12:00:00 +0000",
        "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists/{sid}.json",
    }


def _credential_payload(sid: str = CR_SID) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "credential_list_sid": CL_SID,
        "username": "alice",
        "date_created": "Mon, 17 Jun 2026 12:00:00 +0000",
        "date_updated": "Mon, 17 Jun 2026 12:00:00 +0000",
        "uri": (
            f"/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists/{CL_SID}"
            f"/Credentials/{sid}.json"
        ),
    }


def _ipacl_payload(sid: str = ACL_SID) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "friendly_name": "carrier-allowlist",
        "date_created": "Mon, 17 Jun 2026 12:00:00 +0000",
        "date_updated": "Mon, 17 Jun 2026 12:00:00 +0000",
        "uri": f"/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists/{sid}.json",
    }


def _ip_address_payload(sid: str = IP_SID) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "ip_access_control_list_sid": ACL_SID,
        "friendly_name": "carrier-edge-1",
        "ip_address": "203.0.113.10",
        "cidr_prefix_length": 32,
        "date_created": "Mon, 17 Jun 2026 12:00:00 +0000",
        "date_updated": "Mon, 17 Jun 2026 12:00:00 +0000",
        "uri": (
            f"/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists/"
            f"{ACL_SID}/IpAddresses/{sid}.json"
        ),
    }


def _mapping_payload(sid: str = MAPPING_SID) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "friendly_name": None,
        "domain_sid": DOMAIN_SID,
        "date_created": "Mon, 17 Jun 2026 12:00:00 +0000",
        "date_updated": "Mon, 17 Jun 2026 12:00:00 +0000",
        "uri": "/2010-04-01/Accounts/" + ACCOUNT_SID + "/SIP/Domains/" + DOMAIN_SID
            + "/CredentialListMappings/" + sid + ".json",
    }


# --- Wiring ----------------------------------------------------------------


def test_sip_resource_is_wired_on_client():
    c = Client(account_sid=ACCOUNT_SID, api_key=API_KEY)
    try:
        assert c.sip is not None
        assert c.sip.domains is not None
        assert c.sip.credential_lists is not None
        assert c.sip.ip_access_control_lists is not None
        assert c.sip.domains.auth.calls is not None
        assert c.sip.domains.auth.registrations is not None
    finally:
        c.close()


def test_sip_resource_is_wired_on_async_client():
    c = AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY)
    assert c.sip is not None
    assert c.sip.domains is not None


# --- SipDomains: list / create / fetch / update / delete -------------------


def test_sip_domains_list(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains.json",
        json={"domains": [_domain_payload()], "page": 0, "page_size": 50, "total": 1,
              "next_page_uri": None, "uri": ""},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        out = c.sip.domains.list()
    assert len(out.domains) == 1
    assert out.domains[0].sid == DOMAIN_SID
    assert out.domains[0].domain_name == "ingress.example.com"


def test_sip_domains_create_sends_form(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains.json",
        json=_domain_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        domain = c.sip.domains.create(
            domain_name="ingress.example.com",
            friendly_name="ingress",
            voice_url="https://hooks.example.com/voice",
            voice_method="POST",
            sip_registration=False,
            secure=True,
        )
    req = httpx_mock.get_request()
    body = _form(req.content)
    assert body["DomainName"] == ["ingress.example.com"]
    assert body["FriendlyName"] == ["ingress"]
    assert body["VoiceUrl"] == ["https://hooks.example.com/voice"]
    assert body["VoiceMethod"] == ["POST"]
    assert body["SipRegistration"] == ["false"]
    assert body["Secure"] == ["true"]
    assert domain.sid == DOMAIN_SID


def test_sip_domains_fetch(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{DOMAIN_SID}.json",
        json=_domain_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        d = c.sip.domains.fetch(DOMAIN_SID)
    assert d.sid == DOMAIN_SID


def test_sip_domains_update_only_emits_set_fields(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{DOMAIN_SID}.json",
        json=_domain_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.domains.update(DOMAIN_SID, friendly_name="renamed")
    body = _form(httpx_mock.get_request().content)
    assert body == {"FriendlyName": ["renamed"]}


def test_sip_domains_delete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{DOMAIN_SID}.json",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.domains.delete(DOMAIN_SID)


# --- SipCredentialLists ----------------------------------------------------


def test_sip_credential_lists_list(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists.json",
        json={"credential_lists": [_credential_list_payload()], "page": 0,
              "page_size": 50, "total": 1, "next_page_uri": None, "uri": ""},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        out = c.sip.credential_lists.list()
    assert out.credential_lists[0].sid == CL_SID


def test_sip_credential_lists_create(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists.json",
        json=_credential_list_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        cl = c.sip.credential_lists.create(friendly_name="office-handsets")
    body = _form(httpx_mock.get_request().content)
    assert body == {"FriendlyName": ["office-handsets"]}
    assert cl.sid == CL_SID


def test_sip_credential_lists_fetch(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists/{CL_SID}.json",
        json=_credential_list_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        cl = c.sip.credential_lists.fetch(CL_SID)
    assert cl.sid == CL_SID


def test_sip_credential_lists_update(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists/{CL_SID}.json",
        json=_credential_list_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.credential_lists.update(CL_SID, friendly_name="renamed-list")
    body = _form(httpx_mock.get_request().content)
    assert body == {"FriendlyName": ["renamed-list"]}


def test_sip_credential_lists_delete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists/{CL_SID}.json",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.credential_lists.delete(CL_SID)


# --- SipCredentials (nested in CredentialList) -----------------------------


def test_sip_credentials_list(httpx_mock: HTTPXMock):
    url = f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists/{CL_SID}/Credentials.json"
    httpx_mock.add_response(
        method="GET",
        url=url,
        json={"credentials": [_credential_payload()], "page": 0, "page_size": 50,
              "total": 1, "next_page_uri": None, "uri": ""},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        out = c.sip.credential_lists.credentials(CL_SID).list()
    assert out.credentials[0].username == "alice"


def test_sip_credentials_create_sends_username_and_password(httpx_mock: HTTPXMock):
    url = f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists/{CL_SID}/Credentials.json"
    httpx_mock.add_response(method="POST", url=url, json=_credential_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        cred = c.sip.credential_lists.credentials(CL_SID).create(
            username="alice", password="hunter2"
        )
    body = _form(httpx_mock.get_request().content)
    assert body == {"Username": ["alice"], "Password": ["hunter2"]}
    assert cred.username == "alice"


def test_sip_credentials_fetch(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists/{CL_SID}"
        f"/Credentials/{CR_SID}.json"
    )
    httpx_mock.add_response(method="GET", url=url, json=_credential_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        cred = c.sip.credential_lists.credentials(CL_SID).fetch(CR_SID)
    assert cred.sid == CR_SID


def test_sip_credentials_update_password_only(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists/{CL_SID}"
        f"/Credentials/{CR_SID}.json"
    )
    httpx_mock.add_response(method="POST", url=url, json=_credential_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.credential_lists.credentials(CL_SID).update(CR_SID, password="newpwd")
    body = _form(httpx_mock.get_request().content)
    assert body == {"Password": ["newpwd"]}


def test_sip_credentials_delete(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/CredentialLists/{CL_SID}"
        f"/Credentials/{CR_SID}.json"
    )
    httpx_mock.add_response(method="DELETE", url=url, status_code=204)
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.credential_lists.credentials(CL_SID).delete(CR_SID)


# --- SipIpAccessControlLists -----------------------------------------------


def test_sip_ip_access_control_lists_list(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists.json",
        json={"ip_access_control_lists": [_ipacl_payload()], "page": 0,
              "page_size": 50, "total": 1, "next_page_uri": None, "uri": ""},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        out = c.sip.ip_access_control_lists.list()
    assert out.ip_access_control_lists[0].sid == ACL_SID


def test_sip_ip_access_control_lists_create(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists.json",
        json=_ipacl_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        acl = c.sip.ip_access_control_lists.create(friendly_name="carrier-allowlist")
    body = _form(httpx_mock.get_request().content)
    assert body == {"FriendlyName": ["carrier-allowlist"]}
    assert acl.sid == ACL_SID


def test_sip_ip_access_control_lists_fetch(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists/{ACL_SID}.json",
        json=_ipacl_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        acl = c.sip.ip_access_control_lists.fetch(ACL_SID)
    assert acl.sid == ACL_SID


def test_sip_ip_access_control_lists_update(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists/{ACL_SID}.json",
        json=_ipacl_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.ip_access_control_lists.update(ACL_SID, friendly_name="renamed-acl")
    body = _form(httpx_mock.get_request().content)
    assert body == {"FriendlyName": ["renamed-acl"]}


def test_sip_ip_access_control_lists_delete(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists/{ACL_SID}.json",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.ip_access_control_lists.delete(ACL_SID)


# --- SipIpAddresses (nested in IpAccessControlList) ------------------------


def test_sip_ip_addresses_list(httpx_mock: HTTPXMock):
    url = f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists/{ACL_SID}/IpAddresses.json"
    httpx_mock.add_response(
        method="GET", url=url,
        json={"ip_addresses": [_ip_address_payload()], "page": 0, "page_size": 50,
              "total": 1, "next_page_uri": None, "uri": ""},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        out = c.sip.ip_access_control_lists.ip_addresses(ACL_SID).list()
    assert out.ip_addresses[0].sid == IP_SID


def test_sip_ip_addresses_create(httpx_mock: HTTPXMock):
    url = f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists/{ACL_SID}/IpAddresses.json"
    httpx_mock.add_response(method="POST", url=url, json=_ip_address_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ip = c.sip.ip_access_control_lists.ip_addresses(ACL_SID).create(
            friendly_name="carrier-edge-1",
            ip_address="203.0.113.10",
            cidr_prefix_length=32,
        )
    body = _form(httpx_mock.get_request().content)
    assert body == {
        "FriendlyName": ["carrier-edge-1"],
        "IpAddress": ["203.0.113.10"],
        "CidrPrefixLength": ["32"],
    }
    assert ip.cidr_prefix_length == 32


def test_sip_ip_addresses_fetch(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists/"
        f"{ACL_SID}/IpAddresses/{IP_SID}.json"
    )
    httpx_mock.add_response(method="GET", url=url, json=_ip_address_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ip = c.sip.ip_access_control_lists.ip_addresses(ACL_SID).fetch(IP_SID)
    assert ip.sid == IP_SID


def test_sip_ip_addresses_update(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists/"
        f"{ACL_SID}/IpAddresses/{IP_SID}.json"
    )
    httpx_mock.add_response(method="POST", url=url, json=_ip_address_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.ip_access_control_lists.ip_addresses(ACL_SID).update(
            IP_SID, ip_address="203.0.113.11"
        )
    body = _form(httpx_mock.get_request().content)
    assert body == {"IpAddress": ["203.0.113.11"]}


def test_sip_ip_addresses_delete(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/IpAccessControlLists/"
        f"{ACL_SID}/IpAddresses/{IP_SID}.json"
    )
    httpx_mock.add_response(method="DELETE", url=url, status_code=204)
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.ip_access_control_lists.ip_addresses(ACL_SID).delete(IP_SID)


# --- SipDomain mappings (historical no-Auth namespace) ---------------------


def test_sip_domain_credential_list_mappings_create(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{DOMAIN_SID}"
        f"/CredentialListMappings.json"
    )
    httpx_mock.add_response(method="POST", url=url, json=_mapping_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.domains.credential_list_mappings(DOMAIN_SID).create(
            credential_list_sid=CL_SID
        )
    body = _form(httpx_mock.get_request().content)
    assert body == {"CredentialListSid": [CL_SID]}


def test_sip_domain_credential_list_mappings_list(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{DOMAIN_SID}"
        f"/CredentialListMappings.json"
    )
    httpx_mock.add_response(
        method="GET", url=url,
        json={"credential_list_mappings": [_mapping_payload()], "page": 0,
              "page_size": 50, "total": 1, "next_page_uri": None, "uri": ""},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        out = c.sip.domains.credential_list_mappings(DOMAIN_SID).list()
    assert out.credential_list_mappings[0].domain_sid == DOMAIN_SID


def test_sip_domain_credential_list_mappings_fetch_delete(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{DOMAIN_SID}"
        f"/CredentialListMappings/{MAPPING_SID}.json"
    )
    httpx_mock.add_response(method="GET", url=url, json=_mapping_payload())
    httpx_mock.add_response(method="DELETE", url=url, status_code=204)
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        m = c.sip.domains.credential_list_mappings(DOMAIN_SID).fetch(MAPPING_SID)
        assert m.sid == MAPPING_SID
        c.sip.domains.credential_list_mappings(DOMAIN_SID).delete(MAPPING_SID)


def test_sip_domain_ip_access_control_list_mappings_create(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{DOMAIN_SID}"
        f"/IpAccessControlListMappings.json"
    )
    httpx_mock.add_response(method="POST", url=url, json=_mapping_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.domains.ip_access_control_list_mappings(DOMAIN_SID).create(
            ip_access_control_list_sid=ACL_SID
        )
    body = _form(httpx_mock.get_request().content)
    assert body == {"IpAccessControlListSid": [ACL_SID]}


# --- SipDomain Auth/Calls and Auth/Registrations namespaces ----------------


def test_sip_domain_auth_calls_credential_list_mappings_create(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{DOMAIN_SID}"
        f"/Auth/Calls/CredentialListMappings.json"
    )
    httpx_mock.add_response(method="POST", url=url, json=_mapping_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.domains.auth.calls.credential_list_mappings(DOMAIN_SID).create(
            credential_list_sid=CL_SID
        )
    body = _form(httpx_mock.get_request().content)
    assert body == {"CredentialListSid": [CL_SID]}


def test_sip_domain_auth_calls_ip_access_control_list_mappings_create(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{DOMAIN_SID}"
        f"/Auth/Calls/IpAccessControlListMappings.json"
    )
    httpx_mock.add_response(method="POST", url=url, json=_mapping_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.domains.auth.calls.ip_access_control_list_mappings(DOMAIN_SID).create(
            ip_access_control_list_sid=ACL_SID
        )
    body = _form(httpx_mock.get_request().content)
    assert body == {"IpAccessControlListSid": [ACL_SID]}


def test_sip_domain_auth_registrations_credential_list_mappings_create(httpx_mock: HTTPXMock):
    url = (
        f"{BASE}/2010-04-01/Accounts/{ACCOUNT_SID}/SIP/Domains/{DOMAIN_SID}"
        f"/Auth/Registrations/CredentialListMappings.json"
    )
    httpx_mock.add_response(method="POST", url=url, json=_mapping_payload())
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.sip.domains.auth.registrations.credential_list_mappings(DOMAIN_SID).create(
            credential_list_sid=CL_SID
        )
    body = _form(httpx_mock.get_request().content)
    assert body == {"CredentialListSid": [CL_SID]}
