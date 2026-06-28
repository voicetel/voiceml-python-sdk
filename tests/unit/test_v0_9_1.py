"""Wire-shape smoke tests for the v0.9.1 surface (Assistants v1).

One create/list/fetch/update/delete pass per resource family — verifies
the HTTP method, path, and JSON-body encoding against a stub transport.
"""

from __future__ import annotations

import json
import re

import pytest
from pytest_httpx import HTTPXMock

from voiceml import AsyncClient, Client

ACCOUNT_SID = "AC" + "f" * 32
API_KEY = "secret-key-1234"
BASE = "https://voiceml.voicetel.com"

ASST_ID = "aia_asst_" + "a" * 12
TOOL_ID = "aia_tool_" + "b" * 12
KNOW_ID = "aia_know_" + "c" * 12
SESSION_ID = "ses_" + "d" * 12
MSG_ID = "aia_msg_" + "e" * 12
FDBK_ID = "aia_fdbk_" + "f" * 12
POLICY_ID = "aia_plcy_" + "g" * 12


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
# Resource wiring
# ---------------------------------------------------------------------------


def test_v0_9_1_resources_wired_on_sync_client():
    c = Client(account_sid=ACCOUNT_SID, api_key=API_KEY)
    try:
        assert c.assistants_v1 is not None
        assert c.assistants_v1.assistants is not None
        assert c.assistants_v1.tools is not None
        assert c.assistants_v1.knowledge is not None
        assert c.assistants_v1.sessions is not None
        assert c.assistants_v1.policies is not None

        actx = c.assistants_v1.assistants(ASST_ID)
        assert actx.tools is not None
        assert actx.knowledge is not None
        assert actx.feedbacks is not None
        assert actx.messages is not None

        kctx = c.assistants_v1.knowledge(KNOW_ID)
        assert kctx.status is not None
        assert kctx.chunks is not None

        sctx = c.assistants_v1.sessions(SESSION_ID)
        assert sctx.messages is not None
    finally:
        c.close()


def test_v0_9_1_resources_wired_on_async_client():
    c = AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY)
    assert c.assistants_v1 is not None
    assert c.assistants_v1.assistants is not None
    assert c.assistants_v1.tools is not None
    assert c.assistants_v1.knowledge is not None
    assert c.assistants_v1.sessions is not None
    assert c.assistants_v1.policies is not None


# ---------------------------------------------------------------------------
# Assistants — CRUD
# ---------------------------------------------------------------------------


def _assistant_payload(id_: str = ASST_ID) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "customer_ai": {"perception_engine_enabled": True},
        "id": id_,
        "model": "gpt-4o",
        "name": "Support Bot",
        "owner": "alice",
        "url": f"{BASE}/v1/Assistants/{id_}",
        "personality_prompt": "be helpful",
        "date_created": "2026-06-28T00:00:00Z",
        "date_updated": "2026-06-28T00:00:00Z",
    }


def test_assistants_v1_assistants_crud(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Assistants",
        json=_assistant_payload(),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Assistants(\?.*)?$"),
        json={"assistants": [_assistant_payload()], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Assistants/{ASST_ID}",
        json={**_assistant_payload(), "tools": [], "knowledge": []},
    )
    httpx_mock.add_response(
        method="PUT",
        url=f"{BASE}/v1/Assistants/{ASST_ID}",
        json=_assistant_payload(),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Assistants/{ASST_ID}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        created = c.assistants_v1.assistants.create(
            name="Support Bot",
            owner="alice",
            personality_prompt="be helpful",
            model="gpt-4o",
            customer_ai={"perception_engine_enabled": True},
        )
        listed = c.assistants_v1.assistants.list(page_size=25)
        fetched = c.assistants_v1.assistants.fetch(ASST_ID)
        updated = c.assistants_v1.assistants.update(ASST_ID, name="Renamed")
        c.assistants_v1.assistants.delete(ASST_ID)
    assert created.id == ASST_ID
    assert len(listed.assistants) == 1
    assert fetched.id == ASST_ID
    assert fetched.tools == []
    assert fetched.knowledge == []
    assert updated.id == ASST_ID

    requests = httpx_mock.get_requests()
    create_body = json.loads(requests[0].content.decode())
    assert create_body == {
        "name": "Support Bot",
        "owner": "alice",
        "personality_prompt": "be helpful",
        "model": "gpt-4o",
        "customer_ai": {"perception_engine_enabled": True},
    }
    assert "PageSize=25" in requests[1].url.query.decode()
    update_body = json.loads(requests[3].content.decode())
    assert update_body == {"name": "Renamed"}


# ---------------------------------------------------------------------------
# Tools — CRUD + assistant-scoped attach/detach
# ---------------------------------------------------------------------------


def _tool_payload(id_: str = TOOL_ID) -> dict:
    return {
        "account_sid": ACCOUNT_SID,
        "description": "Lookup a customer record.",
        "enabled": True,
        "id": id_,
        "meta": {"endpoint": "https://example.com/lookup"},
        "name": "customer-lookup",
        "requires_auth": True,
        "type": "webhook",
        "url": f"{BASE}/v1/Tools/{id_}",
        "date_created": "2026-06-28T00:00:00Z",
        "date_updated": "2026-06-28T00:00:00Z",
    }


def test_assistants_v1_tools_crud(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Tools",
        json=_tool_payload(),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Tools(\?.*)?$"),
        json={"tools": [_tool_payload()], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Tools/{TOOL_ID}",
        json={**_tool_payload(), "policies": []},
    )
    httpx_mock.add_response(
        method="PUT",
        url=f"{BASE}/v1/Tools/{TOOL_ID}",
        json=_tool_payload(),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Tools/{TOOL_ID}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        created = c.assistants_v1.tools.create(
            name="customer-lookup",
            type="webhook",
            enabled=True,
            description="Lookup a customer record.",
            meta={"endpoint": "https://example.com/lookup"},
        )
        listed = c.assistants_v1.tools.list(assistant_id=ASST_ID, page_size=10)
        fetched = c.assistants_v1.tools.fetch(TOOL_ID)
        updated = c.assistants_v1.tools.update(TOOL_ID, enabled=False)
        c.assistants_v1.tools.delete(TOOL_ID)
    assert created.id == TOOL_ID
    assert len(listed.tools) == 1
    assert fetched.id == TOOL_ID
    assert fetched.policies == []
    assert updated.id == TOOL_ID

    requests = httpx_mock.get_requests()
    create_body = json.loads(requests[0].content.decode())
    assert create_body == {
        "name": "customer-lookup",
        "type": "webhook",
        "enabled": True,
        "description": "Lookup a customer record.",
        "meta": {"endpoint": "https://example.com/lookup"},
    }
    q = requests[1].url.query.decode()
    assert f"AssistantId={ASST_ID}" in q
    assert "PageSize=10" in q
    update_body = json.loads(requests[3].content.decode())
    assert update_body == {"enabled": False}


def test_assistants_v1_assistant_tools_attach_detach(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Assistants/{ASST_ID}/Tools(\?.*)?$"
        ),
        json={"tools": [_tool_payload()], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Assistants/{ASST_ID}/Tools/{TOOL_ID}",
        status_code=204,
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Assistants/{ASST_ID}/Tools/{TOOL_ID}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ts = c.assistants_v1.assistants(ASST_ID).tools
        listed = ts.list(page_size=5)
        ts.attach(TOOL_ID)
        ts.detach(TOOL_ID)
    assert len(listed.tools) == 1
    assert "PageSize=5" in httpx_mock.get_requests()[0].url.query.decode()


# ---------------------------------------------------------------------------
# Knowledge — CRUD + Status/Chunks + assistant-scoped attach/detach
# ---------------------------------------------------------------------------


def _knowledge_payload(id_: str = KNOW_ID) -> dict:
    return {
        "id": id_,
        "account_sid": ACCOUNT_SID,
        "name": "Docs corpus",
        "type": "web",
        "description": "Public docs",
        "knowledge_source_details": {"url": "https://example.com/docs"},
        "status": "ready",
        "url": f"{BASE}/v1/Knowledge/{id_}",
        "embedding_model": "text-embedding-3-small",
        "date_created": "2026-06-28T00:00:00Z",
        "date_updated": "2026-06-28T00:00:00Z",
    }


def test_assistants_v1_knowledge_crud(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Knowledge",
        json=_knowledge_payload(),
        status_code=201,
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Knowledge(\?.*)?$"),
        json={"knowledge": [_knowledge_payload()], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Knowledge/{KNOW_ID}",
        json=_knowledge_payload(),
    )
    httpx_mock.add_response(
        method="PUT",
        url=f"{BASE}/v1/Knowledge/{KNOW_ID}",
        json=_knowledge_payload(),
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Knowledge/{KNOW_ID}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        created = c.assistants_v1.knowledge.create(
            name="Docs corpus",
            type="web",
            description="Public docs",
            embedding_model="text-embedding-3-small",
            knowledge_source_details={"url": "https://example.com/docs"},
        )
        listed = c.assistants_v1.knowledge.list(assistant_id=ASST_ID)
        fetched = c.assistants_v1.knowledge.fetch(KNOW_ID)
        updated = c.assistants_v1.knowledge.update(KNOW_ID, description="Updated")
        c.assistants_v1.knowledge.delete(KNOW_ID)
    assert created.id == KNOW_ID
    assert len(listed.knowledge) == 1
    assert fetched.id == KNOW_ID
    assert updated.id == KNOW_ID

    requests = httpx_mock.get_requests()
    create_body = json.loads(requests[0].content.decode())
    assert create_body == {
        "name": "Docs corpus",
        "type": "web",
        "description": "Public docs",
        "embedding_model": "text-embedding-3-small",
        "knowledge_source_details": {"url": "https://example.com/docs"},
    }
    update_body = json.loads(requests[3].content.decode())
    assert update_body == {"description": "Updated"}


def test_assistants_v1_knowledge_status_and_chunks(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Knowledge/{KNOW_ID}/Status",
        json={
            "account_sid": ACCOUNT_SID,
            "status": "ready",
            "last_status": "ingesting",
            "date_updated": "2026-06-28T00:00:00Z",
        },
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Knowledge/{KNOW_ID}/Chunks(\?.*)?$"
        ),
        json={
            "chunks": [
                {
                    "account_sid": ACCOUNT_SID,
                    "content": "Hello docs.",
                    "metadata": {"source": "docs/index.md"},
                    "date_created": "2026-06-28T00:00:00Z",
                    "date_updated": "2026-06-28T00:00:00Z",
                }
            ],
            "meta": _meta(),
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        kctx = c.assistants_v1.knowledge(KNOW_ID)
        status = kctx.status.fetch()
        chunks = kctx.chunks.list(page_size=20)
    assert status.status == "ready"
    assert status.last_status == "ingesting"
    assert len(chunks.chunks) == 1
    assert chunks.chunks[0].content == "Hello docs."
    assert "PageSize=20" in httpx_mock.get_requests()[1].url.query.decode()


def test_assistants_v1_assistant_knowledge_attach_detach(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Assistants/{ASST_ID}/Knowledge(\?.*)?$"
        ),
        json={"knowledge": [_knowledge_payload()], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Assistants/{ASST_ID}/Knowledge/{KNOW_ID}",
        status_code=204,
    )
    httpx_mock.add_response(
        method="DELETE",
        url=f"{BASE}/v1/Assistants/{ASST_ID}/Knowledge/{KNOW_ID}",
        status_code=204,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        ks = c.assistants_v1.assistants(ASST_ID).knowledge
        listed = ks.list()
        ks.attach(KNOW_ID)
        ks.detach(KNOW_ID)
    assert len(listed.knowledge) == 1


# ---------------------------------------------------------------------------
# Sessions — list + fetch + per-session messages
# ---------------------------------------------------------------------------


def _session_payload(id_: str = SESSION_ID) -> dict:
    return {
        "id": id_,
        "account_sid": ACCOUNT_SID,
        "assistant_id": ASST_ID,
        "verified": True,
        "identity": "user:alice",
        "date_created": "2026-06-28T00:00:00Z",
        "date_updated": "2026-06-28T00:00:00Z",
    }


def test_assistants_v1_sessions_list_fetch_messages(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Sessions(\?.*)?$"),
        json={"sessions": [_session_payload()], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Sessions/{SESSION_ID}",
        json=_session_payload(),
    )
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Sessions/{SESSION_ID}/Messages(\?.*)?$"
        ),
        json={
            "messages": [
                {
                    "id": MSG_ID,
                    "account_sid": ACCOUNT_SID,
                    "assistant_id": ASST_ID,
                    "session_id": SESSION_ID,
                    "identity": "user:alice",
                    "role": "user",
                    "content": {"body": "Hi"},
                    "meta": {},
                    "date_created": "2026-06-28T00:00:00Z",
                    "date_updated": "2026-06-28T00:00:00Z",
                }
            ],
            "meta": _meta(),
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        listed = c.assistants_v1.sessions.list(page_size=5)
        fetched = c.assistants_v1.sessions.fetch(SESSION_ID)
        msgs = c.assistants_v1.sessions(SESSION_ID).messages.list()
    assert len(listed.sessions) == 1
    assert fetched.id == SESSION_ID
    assert len(msgs.messages) == 1
    assert msgs.messages[0].role == "user"


# ---------------------------------------------------------------------------
# Messages — send via POST /v1/Assistants/{id}/Messages
# ---------------------------------------------------------------------------


def test_assistants_v1_assistant_send_message(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Assistants/{ASST_ID}/Messages",
        json={
            "status": "ok",
            "flagged": False,
            "aborted": False,
            "session_id": SESSION_ID,
            "account_sid": ACCOUNT_SID,
            "body": "Hello! How can I help?",
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        sent = c.assistants_v1.assistants(ASST_ID).messages.create(
            identity="user:alice",
            body="Hi there",
            session_id=SESSION_ID,
            mode="sync",
        )
    assert sent.status == "ok"
    assert sent.session_id == SESSION_ID
    assert sent.body == "Hello! How can I help?"

    body = json.loads(httpx_mock.get_requests()[0].content.decode())
    assert body == {
        "identity": "user:alice",
        "body": "Hi there",
        "session_id": SESSION_ID,
        "mode": "sync",
    }


# ---------------------------------------------------------------------------
# Feedback — list + create on /v1/Assistants/{id}/Feedbacks
# ---------------------------------------------------------------------------


def _feedback_payload(id_: str = FDBK_ID) -> dict:
    return {
        "assistant_id": ASST_ID,
        "id": id_,
        "account_sid": ACCOUNT_SID,
        "user_sid": "US" + "0" * 32,
        "message_id": MSG_ID,
        "score": 0.9,
        "session_id": SESSION_ID,
        "text": "Helpful!",
        "date_created": "2026-06-28T00:00:00Z",
        "date_updated": "2026-06-28T00:00:00Z",
    }


def test_assistants_v1_assistant_feedbacks_list_create(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(
            rf"{re.escape(BASE)}/v1/Assistants/{ASST_ID}/Feedbacks(\?.*)?$"
        ),
        json={"feedbacks": [_feedback_payload()], "meta": _meta()},
    )
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Assistants/{ASST_ID}/Feedbacks",
        json=_feedback_payload(),
        status_code=201,
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        fbs = c.assistants_v1.assistants(ASST_ID).feedbacks
        listed = fbs.list()
        created = fbs.create(
            session_id=SESSION_ID,
            message_id=MSG_ID,
            score=0.9,
            text="Helpful!",
        )
    assert len(listed.feedbacks) == 1
    assert created.id == FDBK_ID
    assert created.score == pytest.approx(0.9)

    body = json.loads(httpx_mock.get_requests()[1].content.decode())
    assert body == {
        "session_id": SESSION_ID,
        "message_id": MSG_ID,
        "score": 0.9,
        "text": "Helpful!",
    }


# ---------------------------------------------------------------------------
# Policies — list (read-only)
# ---------------------------------------------------------------------------


def test_assistants_v1_policies_list(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=re.compile(rf"{re.escape(BASE)}/v1/Policies(\?.*)?$"),
        json={
            "policies": [
                {
                    "id": POLICY_ID,
                    "name": "default",
                    "description": "Allow all",
                    "account_sid": ACCOUNT_SID,
                    "user_sid": "US" + "0" * 32,
                    "type": "tool",
                    "policy_details": {"allow": True},
                    "date_created": "2026-06-28T00:00:00Z",
                    "date_updated": "2026-06-28T00:00:00Z",
                }
            ],
            "meta": _meta(),
        },
    )
    with Client(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        listed = c.assistants_v1.policies.list(
            tool_id=TOOL_ID, knowledge_id=KNOW_ID, page_size=15
        )
    assert len(listed.policies) == 1
    assert listed.policies[0].id == POLICY_ID

    q = httpx_mock.get_requests()[0].url.query.decode()
    assert f"ToolId={TOOL_ID}" in q
    assert f"KnowledgeId={KNOW_ID}" in q
    assert "PageSize=15" in q


# ---------------------------------------------------------------------------
# Async smoke — verify Assistants v1 works on AsyncClient.
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_assistants_v1_assistant_create(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Assistants",
        json=_assistant_payload(),
        status_code=201,
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        created = await c.assistants_v1.assistants.create(name="Support Bot")
    assert created.id == ASST_ID


@pytest.mark.asyncio
async def test_async_assistants_v1_tool_attach(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Assistants/{ASST_ID}/Tools/{TOOL_ID}",
        status_code=204,
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        await c.assistants_v1.assistants(ASST_ID).tools.attach(TOOL_ID)


@pytest.mark.asyncio
async def test_async_assistants_v1_knowledge_status_fetch(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE}/v1/Knowledge/{KNOW_ID}/Status",
        json={
            "account_sid": ACCOUNT_SID,
            "status": "ready",
            "date_updated": "2026-06-28T00:00:00Z",
        },
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        status = await c.assistants_v1.knowledge(KNOW_ID).status.fetch()
    assert status.status == "ready"


@pytest.mark.asyncio
async def test_async_assistants_v1_send_message(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE}/v1/Assistants/{ASST_ID}/Messages",
        json={
            "status": "ok",
            "session_id": SESSION_ID,
            "account_sid": ACCOUNT_SID,
            "body": "ok",
        },
    )
    async with AsyncClient(account_sid=ACCOUNT_SID, api_key=API_KEY) as c:
        sent = await c.assistants_v1.assistants(ASST_ID).messages.create(
            identity="user:alice", body="Hi"
        )
    assert sent.status == "ok"
    body = json.loads(httpx_mock.get_requests()[0].content.decode())
    assert body == {"identity": "user:alice", "body": "Hi"}
