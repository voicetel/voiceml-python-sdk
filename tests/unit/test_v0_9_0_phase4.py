"""Wire-shape smoke tests for the v0.9.0 Phase 4 service-scoped Conversations v1 surface.

Each test covers one resource family under ``/v1/Services/{ChatServiceSid}/…``
with at least one round-trip per supported HTTP verb, asserting method, path,
and form/query encoding against a stub transport.
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

SVC_SID = "IS" + "0" * 32
CH_SID = "CH" + "0" * 32
US_SID = "US" + "0" * 32


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


# ---------------------------------------------------------------------------
# Scope wiring
# ---------------------------------------------------------------------------


def test_phase4_service_scope_is_callable_and_exposes_full_surface():
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        # Account-level surface remains accessible.
        assert c.conversations_v1.services.create is not None
        assert c.conversations_v1.services.list is not None
        assert c.conversations_v1.services.fetch is not None
        assert c.conversations_v1.services.delete is not None

        scope = c.conversations_v1.services(SVC_SID)
        assert scope.conversations is not None
        assert scope.roles is not None
        assert scope.users is not None
        assert scope.bindings is not None
        assert scope.configuration is not None
        assert scope.configuration.notifications is not None
        assert scope.configuration.webhooks is not None
        assert scope.participant_conversations is not None
        assert scope.conversation_with_participants is not None

        # Nested factories.
        ctx = scope.conversations(CH_SID)
        assert ctx.messages is not None
        assert ctx.participants is not None
        assert ctx.webhooks is not None
        assert ctx.messages.receipts("IM" + "0" * 32) is not None

        uctx = scope.users(US_SID)
        assert uctx.conversations is not None


def test_phase4_service_scope_wired_on_async_client():
    c = AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY)
    scope = c.conversations_v1.services(SVC_SID)
    assert scope.conversations is not None
    assert scope.roles is not None
    assert scope.bindings is not None
    assert scope.configuration.notifications is not None
    assert scope.configuration.webhooks is not None


# ---------------------------------------------------------------------------
# Service Conversations CRUD
# ---------------------------------------------------------------------------


def _service_conversation_payload(sid: str = CH_SID) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "sid": sid,
        "friendly_name": "Support",
        "unique_name": "support-1",
        "attributes": "{}",
        "state": "active",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Services/{SVC_SID}/Conversations/{sid}",
    }


def test_phase4_service_conversations_crud(httpx_mock: HTTPXMock):
    sid = "CH" + "1" * 32
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Services/{SVC_SID}/Conversations",
        json=_service_conversation_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Services/{SVC_SID}/Conversations(\?.*)?$"
        ),
        json={"conversations": [_service_conversation_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Services/{SVC_SID}/Conversations/{sid}",
        json=_service_conversation_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Services/{SVC_SID}/Conversations/{sid}",
        json=_service_conversation_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Services/{SVC_SID}/Conversations/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        scope = c.conversations_v1.services(SVC_SID)
        created = scope.conversations.create(
            friendly_name="Support",
            unique_name="support-1",
            timers_inactive="PT5M",
            timers_closed="PT1H",
        )
        listed = scope.conversations.list(page_size=10)
        fetched = scope.conversations.fetch(sid)
        updated = scope.conversations.update(sid, state="closed")
        scope.conversations.delete(sid)
    assert created.sid == sid
    assert created.chat_service_sid == SVC_SID
    assert len(listed.conversations) == 1
    assert fetched.sid == sid
    assert updated.sid == sid

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body["FriendlyName"] == ["Support"]
    assert create_body["UniqueName"] == ["support-1"]
    assert create_body["Timers.Inactive"] == ["PT5M"]
    assert create_body["Timers.Closed"] == ["PT1H"]
    update_body = parse_qs(requests[3].content.decode(), keep_blank_values=True)
    assert update_body == {"State": ["closed"]}


# ---------------------------------------------------------------------------
# Service Messages + Receipts
# ---------------------------------------------------------------------------


def _service_message_payload(
    sid: str = "IM" + "0" * 32, conv_sid: str = CH_SID
) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "conversation_sid": conv_sid,
        "sid": sid,
        "index": 0,
        "author": "+15551234567",
        "body": "Hello",
        "attributes": "{}",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Services/{SVC_SID}/Conversations/{conv_sid}/Messages/{sid}",
    }


def test_phase4_service_messages_crud(httpx_mock: HTTPXMock):
    msg_sid = "IM" + "1" * 32
    base_path = f"{BASE}/v1/Services/{SVC_SID}/Conversations/{CH_SID}/Messages"
    httpx_mock.add_response(
        method="POST",
        url=base_path,
        json=_service_message_payload(msg_sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(base_path)}(\?.*)?$"),
        json={"messages": [_service_message_payload(msg_sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{base_path}/{msg_sid}",
        json=_service_message_payload(msg_sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{base_path}/{msg_sid}",
        json=_service_message_payload(msg_sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{base_path}/{msg_sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        messages = c.conversations_v1.services(SVC_SID).conversations(CH_SID).messages
        messages.create(author="+15551234567", body="Hello")
        messages.list()
        messages.fetch(msg_sid)
        messages.update(msg_sid, body="Hi there")
        messages.delete(msg_sid)

    create_body = parse_qs(
        httpx_mock.get_requests()[0].content.decode(), keep_blank_values=True
    )
    assert create_body == {"Author": ["+15551234567"], "Body": ["Hello"]}


def test_phase4_service_message_receipts_list_and_fetch(httpx_mock: HTTPXMock):
    msg_sid = "IM" + "2" * 32
    receipt_sid = "DY" + "0" * 32
    base_path = (
        f"{BASE}/v1/Services/{SVC_SID}/Conversations/{CH_SID}/Messages/{msg_sid}/Receipts"
    )
    receipt_payload = {
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "conversation_sid": CH_SID,
        "sid": receipt_sid,
        "message_sid": msg_sid,
        "status": "delivered",
        "error_code": 0,
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{base_path}/{receipt_sid}",
    }
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(base_path)}(\?.*)?$"),
        json={"delivery_receipts": [receipt_payload], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{base_path}/{receipt_sid}",
        json=receipt_payload,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        receipts = (
            c.conversations_v1.services(SVC_SID)
            .conversations(CH_SID)
            .messages.receipts(msg_sid)
        )
        listed = receipts.list()
        fetched = receipts.fetch(receipt_sid)
    assert len(listed.delivery_receipts) == 1
    assert fetched.sid == receipt_sid
    assert fetched.chat_service_sid == SVC_SID


# ---------------------------------------------------------------------------
# Service Participants
# ---------------------------------------------------------------------------


def _service_participant_payload(sid: str = "MB" + "0" * 32) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "conversation_sid": CH_SID,
        "sid": sid,
        "identity": "alice",
        "attributes": "{}",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Services/{SVC_SID}/Conversations/{CH_SID}/Participants/{sid}",
    }


def test_phase4_service_participants_crud(httpx_mock: HTTPXMock):
    sid = "MB" + "6" * 32
    base_path = f"{BASE}/v1/Services/{SVC_SID}/Conversations/{CH_SID}/Participants"
    httpx_mock.add_response(
        method="POST",
        url=base_path,
        json=_service_participant_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(base_path)}(\?.*)?$"),
        json={"participants": [_service_participant_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{base_path}/{sid}",
        json=_service_participant_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{base_path}/{sid}",
        json=_service_participant_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{base_path}/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ps = c.conversations_v1.services(SVC_SID).conversations(CH_SID).participants
        ps.create(
            identity="alice",
            messaging_binding_address="+15551234567",
            messaging_binding_proxy_address="+15559876543",
        )
        ps.list()
        ps.fetch(sid)
        ps.update(sid, role_sid="RL" + "0" * 32, attributes="{}")
        ps.delete(sid)

    requests = httpx_mock.get_requests()
    create_body = parse_qs(requests[0].content.decode(), keep_blank_values=True)
    assert create_body["Identity"] == ["alice"]
    assert create_body["MessagingBinding.Address"] == ["+15551234567"]
    assert create_body["MessagingBinding.ProxyAddress"] == ["+15559876543"]
    update_body = parse_qs(requests[3].content.decode(), keep_blank_values=True)
    # Service-scoped update accepts only Attributes/RoleSid.
    assert update_body == {"RoleSid": ["RL" + "0" * 32], "Attributes": ["{}"]}


# ---------------------------------------------------------------------------
# Service Scoped Webhooks
# ---------------------------------------------------------------------------


def _service_webhook_payload(sid: str = "WH" + "0" * 32) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "conversation_sid": CH_SID,
        "sid": sid,
        "target": "webhook",
        "configuration": {"url": "https://example.com/hook", "method": "POST"},
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Services/{SVC_SID}/Conversations/{CH_SID}/Webhooks/{sid}",
    }


def test_phase4_service_scoped_webhooks_crud(httpx_mock: HTTPXMock):
    sid = "WH" + "7" * 32
    base_path = f"{BASE}/v1/Services/{SVC_SID}/Conversations/{CH_SID}/Webhooks"
    httpx_mock.add_response(
        method="POST",
        url=base_path,
        json=_service_webhook_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(base_path)}(\?.*)?$"),
        json={"webhooks": [_service_webhook_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{base_path}/{sid}",
        json=_service_webhook_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{base_path}/{sid}",
        json=_service_webhook_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{base_path}/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        whs = c.conversations_v1.services(SVC_SID).conversations(CH_SID).webhooks
        whs.create(
            target="webhook",
            configuration_url="https://example.com/hook",
            configuration_method="POST",
        )
        whs.list()
        whs.fetch(sid)
        whs.update(sid, configuration_url="https://example.com/new")
        whs.delete(sid)

    create_body = parse_qs(
        httpx_mock.get_requests()[0].content.decode(), keep_blank_values=True
    )
    assert create_body["Target"] == ["webhook"]
    assert create_body["Configuration.Url"] == ["https://example.com/hook"]
    assert create_body["Configuration.Method"] == ["POST"]


# ---------------------------------------------------------------------------
# Service Roles
# ---------------------------------------------------------------------------


def _service_role_payload(sid: str = "RL" + "0" * 32) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "friendly_name": "service-admin",
        "type": "service",
        "permissions": ["editAnyMessage"],
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Services/{SVC_SID}/Roles/{sid}",
    }


def test_phase4_service_roles_crud(httpx_mock: HTTPXMock):
    sid = "RL" + "8" * 32
    base_path = f"{BASE}/v1/Services/{SVC_SID}/Roles"
    httpx_mock.add_response(
        method="POST",
        url=base_path,
        json=_service_role_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(base_path)}(\?.*)?$"),
        json={"roles": [_service_role_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{base_path}/{sid}",
        json=_service_role_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{base_path}/{sid}",
        json=_service_role_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{base_path}/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        roles = c.conversations_v1.services(SVC_SID).roles
        roles.create(
            friendly_name="service-admin",
            type="service",
            permission=["editAnyMessage", "deleteAnyMessage"],
        )
        roles.list()
        roles.fetch(sid)
        roles.update(sid, permission=["editAnyMessage"])
        roles.delete(sid)

    create_body = parse_qs(
        httpx_mock.get_requests()[0].content.decode(), keep_blank_values=True
    )
    assert create_body["FriendlyName"] == ["service-admin"]
    assert create_body["Type"] == ["service"]
    assert create_body["Permission"] == ["editAnyMessage", "deleteAnyMessage"]


# ---------------------------------------------------------------------------
# Service Users + per-user Conversations
# ---------------------------------------------------------------------------


def _service_user_payload(sid: str = US_SID) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "identity": "alice",
        "friendly_name": "Alice",
        "attributes": "{}",
        "is_online": False,
        "is_notifiable": True,
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Services/{SVC_SID}/Users/{sid}",
    }


def test_phase4_service_users_crud(httpx_mock: HTTPXMock):
    sid = "US" + "9" * 32
    base_path = f"{BASE}/v1/Services/{SVC_SID}/Users"
    httpx_mock.add_response(
        method="POST",
        url=base_path,
        json=_service_user_payload(sid),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(base_path)}(\?.*)?$"),
        json={"users": [_service_user_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{base_path}/{sid}",
        json=_service_user_payload(sid),
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{base_path}/{sid}",
        json=_service_user_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{base_path}/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        users = c.conversations_v1.services(SVC_SID).users
        users.create(identity="alice", friendly_name="Alice")
        users.list()
        users.fetch(sid)
        users.update(sid, friendly_name="Alice X")
        users.delete(sid)

    create_body = parse_qs(
        httpx_mock.get_requests()[0].content.decode(), keep_blank_values=True
    )
    assert create_body == {"Identity": ["alice"], "FriendlyName": ["Alice"]}


def test_phase4_service_user_conversations_list(httpx_mock: HTTPXMock):
    user_sid = US_SID
    payload = {
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "conversation_sid": CH_SID,
        "user_sid": user_sid,
        "conversation_state": "active",
        "notification_level": "default",
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Services/{SVC_SID}/Users/{user_sid}/Conversations/{CH_SID}",
    }
    base_path = f"{BASE}/v1/Services/{SVC_SID}/Users/{user_sid}/Conversations"
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(base_path)}(\?.*)?$"),
        json={"conversations": [payload], "meta": _meta()},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        listed = c.conversations_v1.services(SVC_SID).users(user_sid).conversations.list(
            page_size=5
        )
    assert len(listed.conversations) == 1
    assert listed.conversations[0].chat_service_sid == SVC_SID
    assert "PageSize=5" in httpx_mock.get_requests()[0].url.query.decode()


# ---------------------------------------------------------------------------
# Service Bindings (list+fetch+delete)
# ---------------------------------------------------------------------------


def _service_binding_payload(sid: str = "BS" + "0" * 32) -> dict:
    return {
        "sid": sid,
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "credential_sid": "CR" + "0" * 32,
        "binding_type": "apn",
        "endpoint": "iphone-1",
        "identity": "alice",
        "message_types": ["new_message"],
        "date_created": "2026-06-27T00:00:00Z",
        "date_updated": "2026-06-27T00:00:00Z",
        "url": f"{BASE}/v1/Services/{SVC_SID}/Bindings/{sid}",
    }


def test_phase4_service_bindings_list_fetch_delete(httpx_mock: HTTPXMock):
    sid = "BS" + "a" * 32
    base_path = f"{BASE}/v1/Services/{SVC_SID}/Bindings"
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(base_path)}(\?.*)?$"),
        json={"bindings": [_service_binding_payload(sid)], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{base_path}/{sid}",
        json=_service_binding_payload(sid),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{base_path}/{sid}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        bindings = c.conversations_v1.services(SVC_SID).bindings
        listed = bindings.list(binding_type="apn", identity="alice", page_size=5)
        fetched = bindings.fetch(sid)
        bindings.delete(sid)
    assert len(listed.bindings) == 1
    assert fetched.binding_type == "apn"

    q = httpx_mock.get_requests()[0].url.query.decode()
    assert "BindingType=apn" in q
    assert "Identity=alice" in q
    assert "PageSize=5" in q


# ---------------------------------------------------------------------------
# Service Configuration (singleton) + Notifications + Webhook Configuration
# ---------------------------------------------------------------------------


def test_phase4_service_configuration_fetch_update(httpx_mock: HTTPXMock):
    payload = {
        "chat_service_sid": SVC_SID,
        "default_chat_service_role_sid": "RL" + "0" * 32,
        "default_conversation_creator_role_sid": "RL" + "1" * 32,
        "default_conversation_role_sid": "RL" + "2" * 32,
        "reachability_enabled": True,
        "url": f"{BASE}/v1/Services/{SVC_SID}/Configuration",
    }
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Services/{SVC_SID}/Configuration",
        json=payload,
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Services/{SVC_SID}/Configuration",
        json=payload,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        scope = c.conversations_v1.services(SVC_SID)
        fetched = scope.configuration.fetch()
        scope.configuration.update(
            default_chat_service_role_sid="RL" + "0" * 32,
            reachability_enabled=True,
        )
    assert fetched.chat_service_sid == SVC_SID
    assert fetched.reachability_enabled is True

    update_body = parse_qs(
        httpx_mock.get_requests()[1].content.decode(), keep_blank_values=True
    )
    assert update_body == {
        "DefaultChatServiceRoleSid": ["RL" + "0" * 32],
        "ReachabilityEnabled": ["true"],
    }


def test_phase4_service_notifications_fetch_update(httpx_mock: HTTPXMock):
    payload = {
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "new_message": {"enabled": True, "template": "hi"},
        "added_to_conversation": {"enabled": True},
        "removed_from_conversation": {"enabled": False},
        "log_enabled": False,
        "url": f"{BASE}/v1/Services/{SVC_SID}/Configuration/Notifications",
    }
    path = f"{BASE}/v1/Services/{SVC_SID}/Configuration/Notifications"
    httpx_mock.add_response(method="GET", url=path, json=payload)
    httpx_mock.add_response(method="POST", url=path, json=payload)
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        scope = c.conversations_v1.services(SVC_SID)
        scope.configuration.notifications.fetch()
        scope.configuration.notifications.update(
            log_enabled=True,
            new_message_enabled=True,
            new_message_template="hi {name}",
            new_message_sound="default",
            new_message_badge_count_enabled=True,
            new_message_with_media_enabled=False,
            added_to_conversation_enabled=True,
            added_to_conversation_template="welcome",
            removed_from_conversation_enabled=False,
        )

    body = parse_qs(
        httpx_mock.get_requests()[1].content.decode(), keep_blank_values=True
    )
    assert body["LogEnabled"] == ["true"]
    assert body["NewMessage.Enabled"] == ["true"]
    assert body["NewMessage.Template"] == ["hi {name}"]
    assert body["NewMessage.Sound"] == ["default"]
    assert body["NewMessage.BadgeCountEnabled"] == ["true"]
    assert body["NewMessage.WithMedia.Enabled"] == ["false"]
    assert body["AddedToConversation.Enabled"] == ["true"]
    assert body["AddedToConversation.Template"] == ["welcome"]
    assert body["RemovedFromConversation.Enabled"] == ["false"]


def test_phase4_service_webhook_configuration_fetch_update(httpx_mock: HTTPXMock):
    payload = {
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "pre_webhook_url": "https://example.com/pre",
        "post_webhook_url": "https://example.com/post",
        "method": "POST",
        "filters": ["onMessageAdded"],
        "url": f"{BASE}/v1/Services/{SVC_SID}/Configuration/Webhooks",
    }
    path = f"{BASE}/v1/Services/{SVC_SID}/Configuration/Webhooks"
    httpx_mock.add_response(method="GET", url=path, json=payload)
    httpx_mock.add_response(method="POST", url=path, json=payload)
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        scope = c.conversations_v1.services(SVC_SID)
        scope.configuration.webhooks.fetch()
        scope.configuration.webhooks.update(
            pre_webhook_url="https://example.com/pre",
            method="POST",
            filters=["onMessageAdded", "onMessageUpdated"],
        )

    body = parse_qs(
        httpx_mock.get_requests()[1].content.decode(), keep_blank_values=True
    )
    assert body["PreWebhookUrl"] == ["https://example.com/pre"]
    assert body["Method"] == ["POST"]
    assert body["Filters"] == ["onMessageAdded", "onMessageUpdated"]


# ---------------------------------------------------------------------------
# Service ParticipantConversations + ConversationWithParticipants
# ---------------------------------------------------------------------------


def test_phase4_service_participant_conversations_list(httpx_mock: HTTPXMock):
    payload = {
        "account_sid": ACCOUNT_SID,
        "chat_service_sid": SVC_SID,
        "participant_identity": "alice",
        "conversation_sid": CH_SID,
        "conversation_state": "active",
        "conversation_date_created": "2026-06-27T00:00:00Z",
        "conversation_date_updated": "2026-06-27T00:00:00Z",
    }
    base_path = f"{BASE}/v1/Services/{SVC_SID}/ParticipantConversations"
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(base_path)}(\?.*)?$"),
        json={"conversations": [payload], "meta": _meta()},
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        listed = c.conversations_v1.services(SVC_SID).participant_conversations.list(
            identity="alice", address="+15551234567"
        )
    assert len(listed.conversations) == 1
    q = httpx_mock.get_requests()[0].url.query.decode()
    assert "Identity=alice" in q
    assert "Address=%2B15551234567" in q


def test_phase4_service_conversation_with_participants_create(httpx_mock: HTTPXMock):
    payload = _service_conversation_payload()
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Services/{SVC_SID}/ConversationWithParticipants",
        json=payload,
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        c.conversations_v1.services(SVC_SID).conversation_with_participants.create(
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
# Async smoke — one service-scoped round-trip on the AsyncClient.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_phase4_service_conversation_create(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Services/{SVC_SID}/Conversations",
        json=_service_conversation_payload(),
        status_code=201,
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        created = await c.conversations_v1.services(SVC_SID).conversations.create(
            friendly_name="Support"
        )
    assert created.sid == CH_SID
    assert created.chat_service_sid == SVC_SID


@pytest.mark.asyncio
async def test_async_phase4_service_configuration_fetch(httpx_mock: HTTPXMock):
    payload = {
        "chat_service_sid": SVC_SID,
        "reachability_enabled": False,
        "url": f"{BASE}/v1/Services/{SVC_SID}/Configuration",
    }
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Services/{SVC_SID}/Configuration",
        json=payload,
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        fetched = await c.conversations_v1.services(SVC_SID).configuration.fetch()
    assert fetched.chat_service_sid == SVC_SID
    assert fetched.reachability_enabled is False
