"""Wire-shape smoke tests for the v0.9.0 surface (Conversations v1, Voice v1, Routes V2).

One create/list/fetch/update/delete pass per resource family — verifies the
HTTP method, path, and form/query encoding against a stub transport.
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs

import pytest
from pytest_httpx import HTTPXMock

from voiceml import AsyncClient, Client

ACCOUNT_SID = "AC" + "f" * 32
API_KEY = "secret-key-1234"
BASE = "https://voiceml.voicetel.com"

# ---------------------------------------------------------------------------
# Resource wiring
# ---------------------------------------------------------------------------


def test_v0_9_0_resources_wired_on_sync_client():
    c = Client(account_sid=ACCOUNT_SID, api_key=API_KEY)
    try:
        assert c.routes_v2.phone_numbers is not None
        assert c.voice_v1.byoc_trunks is not None
        assert c.voice_v1.connection_policies is not None
        assert c.voice_v1.settings is not None
        assert c.voice_v1.source_ip_mappings is not None
        assert c.voice_v1.ip_records is not None
        assert c.conversations_v1.conversations is not None
        assert c.conversations_v1.roles is not None
        assert c.conversations_v1.users is not None
        assert c.conversations_v1.credentials is not None
        assert c.conversations_v1.configuration is not None
        assert c.conversations_v1.configuration.webhooks is not None
        assert c.conversations_v1.configuration.addresses is not None
        assert c.conversations_v1.participant_conversations is not None
        assert c.conversations_v1.conversation_with_participants is not None
        assert c.conversations_v1.services is not None
    finally:
        c.close()


def test_v0_9_0_resources_wired_on_async_client():
    c = AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY)
    assert c.routes_v2.phone_numbers is not None
    assert c.voice_v1.byoc_trunks is not None
    assert c.conversations_v1.conversations is not None


# ---------------------------------------------------------------------------
# Routes V2 PhoneNumbers
# ---------------------------------------------------------------------------


def _phone_number_payload(phone: str = "+18005551234") -> dict:
    return {
        "sid": "QQ" + "0" * 32,
        "phone_number": phone,
        "account_sid": ACCOUNT_SID,
        "friendly_name": "main",
        "voice_region": "us1",
        "url": f"https://voiceml.voicetel.com/v2/PhoneNumbers/{phone}",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
    }


def test_routes_v2_phone_numbers_fetch_url_encodes_plus(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v2/PhoneNumbers/%2B18005551234",
        json=_phone_number_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        rv = c.routes_v2.phone_numbers.fetch("+18005551234")
    assert rv.sid.startswith("QQ")
    assert rv.phone_number == "+18005551234"


def test_routes_v2_phone_numbers_update(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v2/PhoneNumbers/%2B18005551234",
        json=_phone_number_payload(),
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.routes_v2.phone_numbers.update(
            "+18005551234", voice_region="ie1", friendly_name="renamed"
        )
    body = parse_qs(
        httpx_mock.get_request().content.decode(), keep_blank_values=True
    )
    assert body == {"VoiceRegion": ["ie1"], "FriendlyName": ["renamed"]}


# ---------------------------------------------------------------------------
# Voice V1 IpRecords
# ---------------------------------------------------------------------------


def _ip_record_payload(sid: str = "IL" + "0" * 32) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "sid": sid,
        "friendly_name": "carrier-a",
        "ip_address": "203.0.113.10",
        "cidr_prefix_length": 32,
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/IpRecords/{sid}",
    }


def _meta() -> dict:
    return {
        "first_page_url": f"{BASE}/v1/x?Page=0",
        "next_page_url": None,
        "previous_page_url": None,
        "url": f"{BASE}/v1/x",
        "page": 0,
        "page_size": 50,
        "key": "x",
    }


def test_voice_v1_ip_records_crud(httpx_mock: HTTPXMock):
    sid = "IL" + "1" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/IpRecords",
        json=_ip_record_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/IpRecords(\?.*)?$"),
        json={"ip_records": [_ip_record_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/IpRecords/{sid}",
        json=_ip_record_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/IpRecords/{sid}",
        json=_ip_record_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/IpRecords/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        created = c.voice_v1.ip_records.create(
            ip_address="203.0.113.10",
            friendly_name="carrier-a",
            cidr_prefix_length=32,
        )
        listed = c.voice_v1.ip_records.list(page_size=25)
        fetched = c.voice_v1.ip_records.fetch(sid)
        updated = c.voice_v1.ip_records.update(sid, friendly_name="renamed")
        c.voice_v1.ip_records.delete(sid)
    assert created.sid == sid
    assert len(listed.ip_records) == 1
    assert fetched.sid == sid
    assert updated.sid == sid

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body == {
        "IpAddress": ["203.0.113.10"],
        "FriendlyName": ["carrier-a"],
        "CidrPrefixLength": ["32"],
    }
    assert "PageSize=25" in requests[1].url.query.decode()
    update_body = parse_qs(requests[3].content.decode(), keep_blank_values=True)
    assert update_body == {"FriendlyName": ["renamed"]}


# ---------------------------------------------------------------------------
# Voice V1 SourceIpMappings
# ---------------------------------------------------------------------------


def _source_ip_mapping_payload(sid: str = "IB" + "0" * 32) -> dict:
    return {
        "sid": sid,
        "ip_record_sid": "IL" + "0" * 32,
        "sip_domain_sid": "SD" + "0" * 32,
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/SourceIpMappings/{sid}",
    }


def test_voice_v1_source_ip_mappings_crud(httpx_mock: HTTPXMock):
    sid = "IB" + "2" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/SourceIpMappings",
        json=_source_ip_mapping_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/SourceIpMappings(\?.*)?$"),
        json={
            "source_ip_mappings": [_source_ip_mapping_payload(sid)],
            "meta": _meta(),
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/SourceIpMappings/{sid}",
        json=_source_ip_mapping_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/SourceIpMappings/{sid}",
        json=_source_ip_mapping_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/SourceIpMappings/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.voice_v1.source_ip_mappings.create(
            ip_record_sid="IL" + "0" * 32, sip_domain_sid="SD" + "0" * 32
        )
        c.voice_v1.source_ip_mappings.list()
        c.voice_v1.source_ip_mappings.fetch(sid)
        c.voice_v1.source_ip_mappings.update(sid, sip_domain_sid="SD" + "1" * 32)
        c.voice_v1.source_ip_mappings.delete(sid)

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body == {
        "IpRecordSid": ["IL" + "0" * 32],
        "SipDomainSid": ["SD" + "0" * 32],
    }
    update_body = parse_qs(requests[3].content.decode(), keep_blank_values=True)
    assert update_body == {"SipDomainSid": ["SD" + "1" * 32]}


# ---------------------------------------------------------------------------
# Voice V1 ByocTrunks
# ---------------------------------------------------------------------------


def _byoc_trunk_payload(sid: str = "BY" + "0" * 32) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "sid": sid,
        "friendly_name": "carrier-x",
        "voice_url": "https://example.com/twiml",
        "voice_method": "POST",
        "cnam_lookup_enabled": True,
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/ByocTrunks/{sid}",
    }


def test_voice_v1_byoc_trunks_crud(httpx_mock: HTTPXMock):
    sid = "BY" + "3" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/ByocTrunks",
        json=_byoc_trunk_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/ByocTrunks(\?.*)?$"),
        json={"byoc_trunks": [_byoc_trunk_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/ByocTrunks/{sid}",
        json=_byoc_trunk_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/ByocTrunks/{sid}",
        json=_byoc_trunk_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/ByocTrunks/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.voice_v1.byoc_trunks.create(
            friendly_name="x",
            voice_url="https://example.com",
            voice_method="POST",
            cnam_lookup_enabled=True,
        )
        c.voice_v1.byoc_trunks.list()
        c.voice_v1.byoc_trunks.fetch(sid)
        c.voice_v1.byoc_trunks.update(sid, friendly_name="renamed")
        c.voice_v1.byoc_trunks.delete(sid)

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body["FriendlyName"] == ["x"]
    assert create_body["VoiceUrl"] == ["https://example.com"]
    assert create_body["VoiceMethod"] == ["POST"]
    assert create_body["CnamLookupEnabled"] == ["true"]


# ---------------------------------------------------------------------------
# Voice V1 ConnectionPolicies + Targets
# ---------------------------------------------------------------------------


def _connection_policy_payload(sid: str = "NY" + "0" * 32) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "sid": sid,
        "friendly_name": "origination",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/ConnectionPolicies/{sid}",
        "links": {"targets": f"{BASE}/v1/ConnectionPolicies/{sid}/Targets"},
    }


def _target_payload(sid: str = "NE" + "0" * 32, policy_sid: str = "NY" + "0" * 32) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "connection_policy_sid": policy_sid,
        "sid": sid,
        "friendly_name": "edge",
        "target": "sip:edge@example.com",
        "priority": 10,
        "weight": 10,
        "enabled": True,
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/ConnectionPolicies/{policy_sid}/Targets/{sid}",
    }


def test_voice_v1_connection_policies_crud(httpx_mock: HTTPXMock):
    sid = "NY" + "4" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/ConnectionPolicies",
        json=_connection_policy_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/ConnectionPolicies(\?.*)?$"),
        json={
            "connection_policies": [_connection_policy_payload(sid)],
            "meta": _meta(),
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/ConnectionPolicies/{sid}",
        json=_connection_policy_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/ConnectionPolicies/{sid}",
        json=_connection_policy_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/ConnectionPolicies/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.voice_v1.connection_policies.create(friendly_name="origination")
        c.voice_v1.connection_policies.list()
        c.voice_v1.connection_policies.fetch(sid)
        c.voice_v1.connection_policies.update(sid, friendly_name="renamed")
        c.voice_v1.connection_policies.delete(sid)


def test_voice_v1_connection_policy_targets_crud(httpx_mock: HTTPXMock):
    policy_sid = "NY" + "5" * 32
    target_sid = "NE" + "5" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/ConnectionPolicies/{policy_sid}/Targets",
        json=_target_payload(target_sid, policy_sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/ConnectionPolicies/{policy_sid}/Targets(\?.*)?$"
        ),
        json={"targets": [_target_payload(target_sid, policy_sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/ConnectionPolicies/{policy_sid}/Targets/{target_sid}",
        json=_target_payload(target_sid, policy_sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/ConnectionPolicies/{policy_sid}/Targets/{target_sid}",
        json=_target_payload(target_sid, policy_sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/ConnectionPolicies/{policy_sid}/Targets/{target_sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        targets = c.voice_v1.connection_policies.targets(policy_sid)
        targets.create(target="sip:edge@example.com", priority=10, weight=10, enabled=True)
        targets.list()
        targets.fetch(target_sid)
        targets.update(target_sid, friendly_name="renamed")
        targets.delete(target_sid)

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body == {
        "Target": ["sip:edge@example.com"],
        "Priority": ["10"],
        "Weight": ["10"],
        "Enabled": ["true"],
    }


# ---------------------------------------------------------------------------
# Voice V1 Settings (DialingPermissions)
# ---------------------------------------------------------------------------


def test_voice_v1_settings_fetch_and_update(httpx_mock: HTTPXMock):
    payload = {
        "dialing_permissions_inheritance": False,
        "url": f"{BASE}/v1/Settings",
    }
    httpx_mock.add_response(method="GET", url=f"{BASE}/v1/Settings", json=payload)
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Settings",
        json={**payload, "dialing_permissions_inheritance": True},
        status_code=202,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        fetched = c.voice_v1.settings.fetch()
        updated = c.voice_v1.settings.update(dialing_permissions_inheritance=True)
    assert fetched.dialing_permissions_inheritance is False
    assert updated.dialing_permissions_inheritance is True

    sent = httpx_mock.get_requests()[1]
    body = parse_qs(sent.content.decode(), keep_blank_values=True)
    assert body == {"DialingPermissionsInheritance": ["true"]}


# ---------------------------------------------------------------------------
# Conversations V1 — Conversation CRUD
# ---------------------------------------------------------------------------


CH_SID = "CH" + "0" * 32


def _conversation_payload(sid: str = CH_SID) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "sid": sid,
        "friendly_name": "Support",
        "unique_name": "support-1",
        "attributes": "{}",
        "state": "active",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Conversations/{sid}",
    }


def test_conversations_v1_conversation_crud(httpx_mock: HTTPXMock):
    sid = CH_SID
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Conversations",
        json=_conversation_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Conversations(\?.*)?$"),
        json={"conversations": [_conversation_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Conversations/{sid}",
        json=_conversation_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Conversations/{sid}",
        json=_conversation_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Conversations/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        created = c.conversations_v1.conversations.create(
            friendly_name="Support",
            unique_name="support-1",
            timers_inactive="PT5M",
            timers_closed="PT1H",
            bindings_email_address="alerts@example.com",
        )
        listed = c.conversations_v1.conversations.list(page_size=10)
        fetched = c.conversations_v1.conversations.fetch(sid)
        updated = c.conversations_v1.conversations.update(sid, state="closed")
        c.conversations_v1.conversations.delete(sid)
    assert created.sid == sid
    assert len(listed.conversations) == 1
    assert fetched.sid == sid
    assert updated.sid == sid

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body["FriendlyName"] == ["Support"]
    assert create_body["UniqueName"] == ["support-1"]
    assert create_body["Timers.Inactive"] == ["PT5M"]
    assert create_body["Timers.Closed"] == ["PT1H"]
    assert create_body["Bindings.Email.Address"] == ["alerts@example.com"]


# ---------------------------------------------------------------------------
# Conversations V1 — Messages + Receipts
# ---------------------------------------------------------------------------


def _message_payload(
    sid: str = "IM" + "0" * 32, conv_sid: str = CH_SID
) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "conversation_sid": conv_sid,
        "sid": sid,
        "index": 0,
        "author": "+15551234567",
        "body": "Hello",
        "attributes": "{}",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Conversations/{conv_sid}/Messages/{sid}",
    }


def test_conversations_v1_messages_crud(httpx_mock: HTTPXMock):
    msg_sid = "IM" + "1" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Messages",
        json=_message_payload(msg_sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Conversations/{CH_SID}/Messages(\?.*)?$"
        ),
        json={"messages": [_message_payload(msg_sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Messages/{msg_sid}",
        json=_message_payload(msg_sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Messages/{msg_sid}",
        json=_message_payload(msg_sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Messages/{msg_sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        messages = c.conversations_v1.conversations(CH_SID).messages
        messages.create(author="+15551234567", body="Hello")
        messages.list()
        messages.fetch(msg_sid)
        messages.update(msg_sid, body="Hi there")
        messages.delete(msg_sid)

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body == {"Author": ["+15551234567"], "Body": ["Hello"]}


def test_conversations_v1_message_receipts_list_and_fetch(httpx_mock: HTTPXMock):
    msg_sid = "IM" + "2" * 32
    receipt_sid = "DY" + "0" * 32
    receipt_payload = {
        "account_sid": ACCOUNT_SID,
        "conversation_sid": CH_SID,
        "sid": receipt_sid,
        "message_sid": msg_sid,
        "status": "delivered",
        "error_code": 0,
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Conversations/{CH_SID}/Messages/{msg_sid}/Receipts/{receipt_sid}",
    }
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Conversations/{CH_SID}/Messages/{msg_sid}/Receipts(\?.*)?$"
        ),
        json={"delivery_receipts": [receipt_payload], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Messages/{msg_sid}/Receipts/{receipt_sid}",
        json=receipt_payload,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        receipts = c.conversations_v1.conversations(CH_SID).messages.receipts(msg_sid)
        listed = receipts.list()
        fetched = receipts.fetch(receipt_sid)
    assert len(listed.delivery_receipts) == 1
    assert fetched.sid == receipt_sid


# ---------------------------------------------------------------------------
# Conversations V1 — Participants
# ---------------------------------------------------------------------------


def _participant_payload(sid: str = "MB" + "0" * 32) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "conversation_sid": CH_SID,
        "sid": sid,
        "identity": "alice",
        "attributes": "{}",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Conversations/{CH_SID}/Participants/{sid}",
    }


def test_conversations_v1_participants_crud(httpx_mock: HTTPXMock):
    sid = "MB" + "6" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Participants",
        json=_participant_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Conversations/{CH_SID}/Participants(\?.*)?$"
        ),
        json={"participants": [_participant_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Participants/{sid}",
        json=_participant_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Participants/{sid}",
        json=_participant_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Participants/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ps = c.conversations_v1.conversations(CH_SID).participants
        ps.create(
            identity="alice",
            messaging_binding_address="+15551234567",
            messaging_binding_proxy_address="+15559876543",
        )
        ps.list()
        ps.fetch(sid)
        ps.update(sid, last_read_message_index=5)
        ps.delete(sid)

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body["Identity"] == ["alice"]
    assert create_body["MessagingBinding.Address"] == ["+15551234567"]
    assert create_body["MessagingBinding.ProxyAddress"] == ["+15559876543"]
    update_body = parse_qs(requests[3].content.decode(), keep_blank_values=True)
    assert update_body == {"LastReadMessageIndex": ["5"]}


# ---------------------------------------------------------------------------
# Conversations V1 — Scoped Webhooks
# ---------------------------------------------------------------------------


def _scoped_webhook_payload(sid: str = "WH" + "0" * 32) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "conversation_sid": CH_SID,
        "sid": sid,
        "target": "webhook",
        "configuration": {"url": "https://example.com/hook", "method": "POST"},
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Conversations/{CH_SID}/Webhooks/{sid}",
    }


def test_conversations_v1_scoped_webhooks_crud(httpx_mock: HTTPXMock):
    sid = "WH" + "7" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Webhooks",
        json=_scoped_webhook_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Conversations/{CH_SID}/Webhooks(\?.*)?$"
        ),
        json={"webhooks": [_scoped_webhook_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Webhooks/{sid}",
        json=_scoped_webhook_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Webhooks/{sid}",
        json=_scoped_webhook_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Conversations/{CH_SID}/Webhooks/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        whs = c.conversations_v1.conversations(CH_SID).webhooks
        whs.create(
            target="webhook",
            configuration_url="https://example.com/hook",
            configuration_method="POST",
        )
        whs.list()
        whs.fetch(sid)
        whs.update(sid, configuration_url="https://example.com/new")
        whs.delete(sid)

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body["Target"] == ["webhook"]
    assert create_body["Configuration.Url"] == ["https://example.com/hook"]
    assert create_body["Configuration.Method"] == ["POST"]


# ---------------------------------------------------------------------------
# Conversations V1 — Roles
# ---------------------------------------------------------------------------


def _role_payload(sid: str = "RL" + "0" * 32) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "friendly_name": "default-conversation-user",
        "type": "conversation",
        "permissions": ["sendMessage", "leaveConversation"],
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Roles/{sid}",
    }


def test_conversations_v1_roles_crud(httpx_mock: HTTPXMock):
    sid = "RL" + "8" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Roles",
        json=_role_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Roles(\?.*)?$"),
        json={"roles": [_role_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Roles/{sid}",
        json=_role_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Roles/{sid}",
        json=_role_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Roles/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.conversations_v1.roles.create(
            friendly_name="default",
            type="conversation",
            permission=["sendMessage", "leaveConversation"],
        )
        c.conversations_v1.roles.list()
        c.conversations_v1.roles.fetch(sid)
        c.conversations_v1.roles.update(sid, permission=["sendMessage"])
        c.conversations_v1.roles.delete(sid)

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body["FriendlyName"] == ["default"]
    assert create_body["Type"] == ["conversation"]
    # Repeated form param: list values become repeated keys.
    assert create_body["Permission"] == ["sendMessage", "leaveConversation"]


# ---------------------------------------------------------------------------
# Conversations V1 — Users + per-user Conversations
# ---------------------------------------------------------------------------


US_SID = "US" + "0" * 32


def _user_payload(sid: str = US_SID) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "identity": "alice",
        "friendly_name": "Alice",
        "attributes": "{}",
        "is_online": False,
        "is_notifiable": True,
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Users/{sid}",
    }


def test_conversations_v1_users_crud(httpx_mock: HTTPXMock):
    sid = "US" + "9" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Users",
        json=_user_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Users(\?.*)?$"),
        json={"users": [_user_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Users/{sid}",
        json=_user_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Users/{sid}",
        json=_user_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Users/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.conversations_v1.users.create(identity="alice", friendly_name="Alice")
        c.conversations_v1.users.list()
        c.conversations_v1.users.fetch(sid)
        c.conversations_v1.users.update(sid, friendly_name="Alice X")
        c.conversations_v1.users.delete(sid)

    create_body = parse_qs(
        httpx_mock.get_requests()[0].content.decode(), keep_blank_values=True
    )
    assert create_body == {"Identity": ["alice"], "FriendlyName": ["Alice"]}


def test_conversations_v1_user_conversations_crud(httpx_mock: HTTPXMock):
    uc_payload = {
        "account_sid": ACCOUNT_SID,
        "conversation_sid": CH_SID,
        "user_sid": US_SID,
        "conversation_state": "active",
        "notification_level": "default",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Users/{US_SID}/Conversations/{CH_SID}",
    }
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Users/{US_SID}/Conversations(\?.*)?$"
        ),
        json={"conversations": [uc_payload], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Users/{US_SID}/Conversations/{CH_SID}",
        json=uc_payload,
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Users/{US_SID}/Conversations/{CH_SID}",
        json=uc_payload,
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Users/{US_SID}/Conversations/{CH_SID}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ucs = c.conversations_v1.users(US_SID).conversations
        listed = ucs.list()
        fetched = ucs.fetch(CH_SID)
        ucs.update(CH_SID, notification_level="muted", last_read_message_index=10)
        ucs.delete(CH_SID)
    assert len(listed.conversations) == 1
    assert fetched.conversation_sid == CH_SID

    update_body = parse_qs(
        httpx_mock.get_requests()[2].content.decode(), keep_blank_values=True
    )
    assert update_body == {
        "NotificationLevel": ["muted"],
        "LastReadMessageIndex": ["10"],
    }


# ---------------------------------------------------------------------------
# Conversations V1 — Credentials
# ---------------------------------------------------------------------------


def _credential_payload(sid: str = "CR" + "0" * 32) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "friendly_name": "apns-prod",
        "type": "apn",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Credentials/{sid}",
    }


def test_conversations_v1_credentials_crud(httpx_mock: HTTPXMock):
    sid = "CR" + "a" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Credentials",
        json=_credential_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Credentials(\?.*)?$"),
        json={"credentials": [_credential_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Credentials/{sid}",
        json=_credential_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Credentials/{sid}",
        json=_credential_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Credentials/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.conversations_v1.credentials.create(
            type="apn",
            friendly_name="apns-prod",
            sandbox=False,
            certificate="-----BEGIN CERT-----...",
        )
        c.conversations_v1.credentials.list()
        c.conversations_v1.credentials.fetch(sid)
        c.conversations_v1.credentials.update(sid, friendly_name="apns-prod-v2")
        c.conversations_v1.credentials.delete(sid)

    create_body = parse_qs(
        httpx_mock.get_requests()[0].content.decode(), keep_blank_values=True
    )
    assert create_body["Type"] == ["apn"]
    assert create_body["Sandbox"] == ["false"]
    assert create_body["Certificate"] == ["-----BEGIN CERT-----..."]


# ---------------------------------------------------------------------------
# Conversations V1 — Configuration + Webhooks + Addresses
# ---------------------------------------------------------------------------


def test_conversations_v1_configuration_fetch_update(httpx_mock: HTTPXMock):
    payload = {
        "account_sid": ACCOUNT_SID,
        "default_chat_service_sid": "IS" + "0" * 32,
        "default_messaging_service_sid": "MG" + "0" * 32,
        "default_inactive_timer": "PT5M",
        "default_closed_timer": "PT1H",
        "url": f"{BASE}/v1/Configuration",
    }
    httpx_mock.add_response(method="GET", url=f"{BASE}/v1/Configuration", json=payload)
    httpx_mock.add_response(method="POST", url=f"{BASE}/v1/Configuration", json=payload)
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        fetched = c.conversations_v1.configuration.fetch()
        c.conversations_v1.configuration.update(
            default_chat_service_sid="IS" + "0" * 32,
            default_inactive_timer="PT5M",
        )
    assert fetched.default_chat_service_sid == "IS" + "0" * 32

    body = parse_qs(
        httpx_mock.get_requests()[1].content.decode(), keep_blank_values=True
    )
    assert body == {
        "DefaultChatServiceSid": ["IS" + "0" * 32],
        "DefaultInactiveTimer": ["PT5M"],
    }


def test_conversations_v1_configuration_webhooks_fetch_update(httpx_mock: HTTPXMock):
    payload = {
        "account_sid": ACCOUNT_SID,
        "method": "POST",
        "filters": ["onMessageAdded"],
        "pre_webhook_url": "https://example.com/pre",
        "post_webhook_url": "https://example.com/post",
        "target": "webhook",
        "url": f"{BASE}/v1/Configuration/Webhooks",
    }
    httpx_mock.add_response(
        method="GET", url=f"{BASE}/v1/Configuration/Webhooks", json=payload
    )
    httpx_mock.add_response(
        method="POST", url=f"{BASE}/v1/Configuration/Webhooks", json=payload
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.conversations_v1.configuration.webhooks.fetch()
        c.conversations_v1.configuration.webhooks.update(
            method="POST",
            filters=["onMessageAdded", "onMessageUpdated"],
            pre_webhook_url="https://example.com/pre",
        )
    body = parse_qs(
        httpx_mock.get_requests()[1].content.decode(), keep_blank_values=True
    )
    assert body["Method"] == ["POST"]
    assert body["Filters"] == ["onMessageAdded", "onMessageUpdated"]
    assert body["PreWebhookUrl"] == ["https://example.com/pre"]


def _config_address_payload(sid: str = "IG" + "0" * 32) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "type": "sms",
        "address": "+15551234567",
        "friendly_name": "main-sms",
        "auto_creation": {"enabled": True, "type": "webhook"},
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Configuration/Addresses/{sid}",
        "address_country": "US",
    }


def test_conversations_v1_config_addresses_crud(httpx_mock: HTTPXMock):
    sid = "IG" + "b" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Configuration/Addresses",
        json=_config_address_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Configuration/Addresses(\?.*)?$"
        ),
        json={"addresses": [_config_address_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Configuration/Addresses/{sid}",
        json=_config_address_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Configuration/Addresses/{sid}",
        json=_config_address_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Configuration/Addresses/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.conversations_v1.configuration.addresses.create(
            type="sms",
            address="+15551234567",
            friendly_name="main-sms",
            auto_creation_enabled=True,
            auto_creation_type="webhook",
            auto_creation_webhook_url="https://example.com/auto",
            address_country="US",
        )
        c.conversations_v1.configuration.addresses.list()
        c.conversations_v1.configuration.addresses.fetch(sid)
        c.conversations_v1.configuration.addresses.update(
            sid, auto_creation_enabled=False
        )
        c.conversations_v1.configuration.addresses.delete(sid)

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body["Type"] == ["sms"]
    assert create_body["Address"] == ["+15551234567"]
    assert create_body["AutoCreation.Enabled"] == ["true"]
    assert create_body["AutoCreation.Type"] == ["webhook"]
    assert create_body["AutoCreation.WebhookUrl"] == ["https://example.com/auto"]
    assert create_body["AddressCountry"] == ["US"]
    update_body = parse_qs(requests[3].content.decode(), keep_blank_values=True)
    assert update_body == {"AutoCreation.Enabled": ["false"]}


# ---------------------------------------------------------------------------
# Conversations V1 — ParticipantConversations + ConversationWithParticipants
# ---------------------------------------------------------------------------


def test_conversations_v1_participant_conversations_list(httpx_mock: HTTPXMock):
    payload = {
        "account_sid": ACCOUNT_SID,
        "participant_identity": "alice",
        "conversation_sid": CH_SID,
        "conversation_state": "active",
        "conversation_date_created": "2026-06-27T00:00:00Z",
        "conversation_date_updated": "2026-06-27T00:00:00Z",
    }
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/ParticipantConversations(\?.*)?$"),
        json={"conversations": [payload], "meta": _meta()},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        listed = c.conversations_v1.participant_conversations.list(
            identity="alice", address="+15551234567"
        )
    assert len(listed.conversations) == 1
    q = httpx_mock.get_requests()[0].url.query.decode()
    assert "Identity=alice" in q
    assert "Address=%2B15551234567" in q


def test_conversations_v1_conversation_with_participants_create(
    httpx_mock: HTTPXMock,
):
    payload = {
        **_conversation_payload(),
    }
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/ConversationWithParticipants",
        json=payload,
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.conversations_v1.conversation_with_participants.create(
            friendly_name="Support",
            participant=[
                '{"identity":"alice"}',
                '{"messaging_binding":{"address":"+15551234567"}}',
            ],
        )
    body = parse_qs(
        httpx_mock.get_requests()[0].content.decode(), keep_blank_values=True
    )
    assert body["FriendlyName"] == ["Support"]
    assert body["Participant"] == [
        '{"identity":"alice"}',
        '{"messaging_binding":{"address":"+15551234567"}}',
    ]


# ---------------------------------------------------------------------------
# Conversations V1 — Services
# ---------------------------------------------------------------------------


def test_conversations_v1_services_crud(httpx_mock: HTTPXMock):
    sid = "IS" + "c" * 32
    payload = {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "friendly_name": "support-service",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Services/{sid}",
    }
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Services",
        json=payload,
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Services(\?.*)?$"),
        json={"services": [payload], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Services/{sid}",
        json=payload,
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Services/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.conversations_v1.services.create(friendly_name="support-service")
        c.conversations_v1.services.list()
        c.conversations_v1.services.fetch(sid)
        c.conversations_v1.services.delete(sid)

    create_body = parse_qs(
        httpx_mock.get_requests()[0].content.decode(), keep_blank_values=True
    )
    assert create_body == {"FriendlyName": ["support-service"]}


# ---------------------------------------------------------------------------
# Async smoke — verify one new resource works on AsyncClient.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_conversations_v1_conversation_create(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Conversations",
        json=_conversation_payload(),
        status_code=201,
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        created = await c.conversations_v1.conversations.create(
            friendly_name="Support"
        )
    assert created.sid == CH_SID


@pytest.mark.asyncio
async def test_async_voice_v1_settings_fetch(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Settings",
        json={"dialing_permissions_inheritance": False, "url": f"{BASE}/v1/Settings"},
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        fetched = await c.voice_v1.settings.fetch()
    assert fetched.dialing_permissions_inheritance is False


@pytest.mark.asyncio
async def test_async_routes_v2_phone_numbers_fetch(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v2/PhoneNumbers/%2B18005551234",
        json=_phone_number_payload(),
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        fetched = await c.routes_v2.phone_numbers.fetch("+18005551234")
    assert fetched.phone_number == "+18005551234"
