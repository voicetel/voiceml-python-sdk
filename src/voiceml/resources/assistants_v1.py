"""``/v1/Assistants…`` REST surface — VoiceML Assistants v1 (AI Assistants).

Top-level holder is :class:`AssistantsV1Resource` (sync) /
:class:`AssistantsV1AsyncResource` (async), wired under
``client.assistants_v1.*``.

Layout::

    client.assistants_v1.assistants.create / list / fetch / update / delete
    client.assistants_v1.assistants(asst_id).tools.list / attach / detach
    client.assistants_v1.assistants(asst_id).knowledge.list / attach / detach
    client.assistants_v1.assistants(asst_id).feedbacks.list / create
    client.assistants_v1.assistants(asst_id).messages.create

    client.assistants_v1.tools.create / list / fetch / update / delete
    client.assistants_v1.knowledge.create / list / fetch / update / delete
    client.assistants_v1.knowledge(know_id).status.fetch
    client.assistants_v1.knowledge(know_id).chunks.list

    client.assistants_v1.sessions.list / fetch
    client.assistants_v1.sessions(session_id).messages.list

    client.assistants_v1.policies.list

All paths sit at ``/v1/`` and request bodies are JSON
(``application/json``), unlike the form-encoded Twilio classic surfaces.
"""

from __future__ import annotations

from typing import Any

from ..models import (
    AssistantsV1Assistant,
    AssistantsV1AssistantList,
    AssistantsV1AssistantWithToolsAndKnowledge,
    AssistantsV1Feedback,
    AssistantsV1FeedbackList,
    AssistantsV1Knowledge,
    AssistantsV1KnowledgeChunkList,
    AssistantsV1KnowledgeList,
    AssistantsV1KnowledgeStatus,
    AssistantsV1MessageList,
    AssistantsV1PolicyList,
    AssistantsV1SendMessageResponse,
    AssistantsV1Session,
    AssistantsV1SessionList,
    AssistantsV1Tool,
    AssistantsV1ToolList,
    AssistantsV1ToolWithPolicies,
    CreateAssistantsV1AssistantRequest,
    CreateAssistantsV1FeedbackRequest,
    CreateAssistantsV1KnowledgeRequest,
    CreateAssistantsV1ToolRequest,
    SendAssistantsV1MessageRequest,
    UpdateAssistantsV1AssistantRequest,
    UpdateAssistantsV1KnowledgeRequest,
    UpdateAssistantsV1ToolRequest,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _page_params(*, page_size: int | None) -> dict[str, object]:
    return {"PageSize": page_size}


def _assistant_create_body(
    *,
    name: str,
    owner: str | None,
    personality_prompt: str | None,
    model: str | None,
    customer_ai: dict[str, Any] | None,
    segment_credential: dict[str, Any] | None,
) -> dict[str, Any]:
    return CreateAssistantsV1AssistantRequest(
        name=name,
        owner=owner,
        personality_prompt=personality_prompt,
        model=model,
        customer_ai=customer_ai,
        segment_credential=segment_credential,
    ).to_json()


def _assistant_update_body(
    *,
    name: str | None,
    owner: str | None,
    personality_prompt: str | None,
    model: str | None,
    customer_ai: dict[str, Any] | None,
    segment_credential: dict[str, Any] | None,
) -> dict[str, Any]:
    return UpdateAssistantsV1AssistantRequest(
        name=name,
        owner=owner,
        personality_prompt=personality_prompt,
        model=model,
        customer_ai=customer_ai,
        segment_credential=segment_credential,
    ).to_json()


# ===========================================================================
# Sync sub-resources keyed by parent IDs
# ===========================================================================


class _AssistantsV1AssistantToolsResource:
    """``/v1/Assistants/{id}/Tools`` (sync) — list + attach/detach."""

    def __init__(self, transport: object, assistant_id: str) -> None:
        self._t = transport
        self._asst = assistant_id

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Assistants", self._asst, "Tools", *tail]
        return "/" + "/".join(parts)

    def list(self, *, page_size: int | None = None) -> AssistantsV1ToolList:
        return AssistantsV1ToolList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def attach(self, tool_id: str) -> None:
        self._t.request("POST", self._root(tool_id))

    def detach(self, tool_id: str) -> None:
        self._t.request("DELETE", self._root(tool_id))


class _AssistantsV1AssistantKnowledgeResource:
    """``/v1/Assistants/{id}/Knowledge`` (sync) — list + attach/detach."""

    def __init__(self, transport: object, assistant_id: str) -> None:
        self._t = transport
        self._asst = assistant_id

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Assistants", self._asst, "Knowledge", *tail]
        return "/" + "/".join(parts)

    def list(self, *, page_size: int | None = None) -> AssistantsV1KnowledgeList:
        return AssistantsV1KnowledgeList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def attach(self, knowledge_id: str) -> None:
        self._t.request("POST", self._root(knowledge_id))

    def detach(self, knowledge_id: str) -> None:
        self._t.request("DELETE", self._root(knowledge_id))


class _AssistantsV1AssistantFeedbacksResource:
    """``/v1/Assistants/{id}/Feedbacks`` (sync) — list + create."""

    def __init__(self, transport: object, assistant_id: str) -> None:
        self._t = transport
        self._asst = assistant_id

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Assistants", self._asst, "Feedbacks", *tail]
        return "/" + "/".join(parts)

    def list(self, *, page_size: int | None = None) -> AssistantsV1FeedbackList:
        return AssistantsV1FeedbackList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def create(
        self,
        *,
        session_id: str,
        message_id: str | None = None,
        score: float | None = None,
        text: str | None = None,
    ) -> AssistantsV1Feedback:
        body = CreateAssistantsV1FeedbackRequest(
            session_id=session_id,
            message_id=message_id,
            score=score,
            text=text,
        ).to_json()
        return AssistantsV1Feedback.model_validate(
            self._t.request("POST", self._root(), json=body)
        )


class _AssistantsV1AssistantMessagesResource:
    """``/v1/Assistants/{id}/Messages`` (sync) — send a message to the Assistant."""

    def __init__(self, transport: object, assistant_id: str) -> None:
        self._t = transport
        self._asst = assistant_id

    def _root(self) -> str:
        return f"/v1/Assistants/{self._asst}/Messages"

    def create(
        self,
        *,
        identity: str,
        body: str,
        session_id: str | None = None,
        webhook: str | None = None,
        mode: str | None = None,
    ) -> AssistantsV1SendMessageResponse:
        payload = SendAssistantsV1MessageRequest(
            identity=identity,
            body=body,
            session_id=session_id,
            webhook=webhook,
            mode=mode,
        ).to_json()
        return AssistantsV1SendMessageResponse.model_validate(
            self._t.request("POST", self._root(), json=payload)
        )


class _AssistantContext:
    """Returned by ``client.assistants_v1.assistants(id)`` — sub-resource factory."""

    def __init__(self, transport: object, assistant_id: str) -> None:
        self.tools = _AssistantsV1AssistantToolsResource(transport, assistant_id)
        self.knowledge = _AssistantsV1AssistantKnowledgeResource(transport, assistant_id)
        self.feedbacks = _AssistantsV1AssistantFeedbacksResource(transport, assistant_id)
        self.messages = _AssistantsV1AssistantMessagesResource(transport, assistant_id)


class _AssistantsV1AssistantsCallable:
    """Top-level ``client.assistants_v1.assistants`` — callable + namespace.

    Calling it (e.g. ``assistants("aia_asst_…")``) returns an
    :class:`_AssistantContext` bound to a parent assistant id. Accessing
    attributes drives the un-bound CRUD.
    """

    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, assistant_id: str) -> _AssistantContext:
        return _AssistantContext(self._t, assistant_id)

    def create(
        self,
        *,
        name: str,
        owner: str | None = None,
        personality_prompt: str | None = None,
        model: str | None = None,
        customer_ai: dict[str, Any] | None = None,
        segment_credential: dict[str, Any] | None = None,
    ) -> AssistantsV1Assistant:
        return AssistantsV1Assistant.model_validate(
            self._t.request(
                "POST",
                "/v1/Assistants",
                json=_assistant_create_body(
                    name=name,
                    owner=owner,
                    personality_prompt=personality_prompt,
                    model=model,
                    customer_ai=customer_ai,
                    segment_credential=segment_credential,
                ),
            )
        )

    def list(self, *, page_size: int | None = None) -> AssistantsV1AssistantList:
        return AssistantsV1AssistantList.model_validate(
            self._t.request(
                "GET",
                "/v1/Assistants",
                params=_page_params(page_size=page_size),
            )
        )

    def fetch(self, assistant_id: str) -> AssistantsV1AssistantWithToolsAndKnowledge:
        return AssistantsV1AssistantWithToolsAndKnowledge.model_validate(
            self._t.request("GET", f"/v1/Assistants/{assistant_id}")
        )

    def update(
        self,
        assistant_id: str,
        *,
        name: str | None = None,
        owner: str | None = None,
        personality_prompt: str | None = None,
        model: str | None = None,
        customer_ai: dict[str, Any] | None = None,
        segment_credential: dict[str, Any] | None = None,
    ) -> AssistantsV1Assistant:
        return AssistantsV1Assistant.model_validate(
            self._t.request(
                "PUT",
                f"/v1/Assistants/{assistant_id}",
                json=_assistant_update_body(
                    name=name,
                    owner=owner,
                    personality_prompt=personality_prompt,
                    model=model,
                    customer_ai=customer_ai,
                    segment_credential=segment_credential,
                ),
            )
        )

    def delete(self, assistant_id: str) -> None:
        self._t.request("DELETE", f"/v1/Assistants/{assistant_id}")


class _AssistantsV1ToolsResource:
    """``/v1/Tools`` (sync) — global Tool CRUD."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def create(
        self,
        *,
        name: str,
        type: str,
        enabled: bool,
        assistant_id: str | None = None,
        description: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> AssistantsV1Tool:
        body = CreateAssistantsV1ToolRequest(
            name=name,
            type=type,
            enabled=enabled,
            assistant_id=assistant_id,
            description=description,
            meta=meta,
        ).to_json()
        return AssistantsV1Tool.model_validate(
            self._t.request("POST", "/v1/Tools", json=body)
        )

    def list(
        self,
        *,
        assistant_id: str | None = None,
        page_size: int | None = None,
    ) -> AssistantsV1ToolList:
        return AssistantsV1ToolList.model_validate(
            self._t.request(
                "GET",
                "/v1/Tools",
                params={"AssistantId": assistant_id, "PageSize": page_size},
            )
        )

    def fetch(self, tool_id: str) -> AssistantsV1ToolWithPolicies:
        return AssistantsV1ToolWithPolicies.model_validate(
            self._t.request("GET", f"/v1/Tools/{tool_id}")
        )

    def update(
        self,
        tool_id: str,
        *,
        name: str | None = None,
        type: str | None = None,
        enabled: bool | None = None,
        description: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> AssistantsV1Tool:
        body = UpdateAssistantsV1ToolRequest(
            name=name,
            type=type,
            enabled=enabled,
            description=description,
            meta=meta,
        ).to_json()
        return AssistantsV1Tool.model_validate(
            self._t.request("PUT", f"/v1/Tools/{tool_id}", json=body)
        )

    def delete(self, tool_id: str) -> None:
        self._t.request("DELETE", f"/v1/Tools/{tool_id}")


class _AssistantsV1KnowledgeStatusResource:
    """``/v1/Knowledge/{id}/Status`` (sync) — read-only status singleton."""

    def __init__(self, transport: object, knowledge_id: str) -> None:
        self._t = transport
        self._know = knowledge_id

    def fetch(self) -> AssistantsV1KnowledgeStatus:
        return AssistantsV1KnowledgeStatus.model_validate(
            self._t.request("GET", f"/v1/Knowledge/{self._know}/Status")
        )


class _AssistantsV1KnowledgeChunksResource:
    """``/v1/Knowledge/{id}/Chunks`` (sync) — read-only chunk listing."""

    def __init__(self, transport: object, knowledge_id: str) -> None:
        self._t = transport
        self._know = knowledge_id

    def list(self, *, page_size: int | None = None) -> AssistantsV1KnowledgeChunkList:
        return AssistantsV1KnowledgeChunkList.model_validate(
            self._t.request(
                "GET",
                f"/v1/Knowledge/{self._know}/Chunks",
                params=_page_params(page_size=page_size),
            )
        )


class _KnowledgeContext:
    """Returned by ``client.assistants_v1.knowledge(id)`` — sub-resource factory."""

    def __init__(self, transport: object, knowledge_id: str) -> None:
        self.status = _AssistantsV1KnowledgeStatusResource(transport, knowledge_id)
        self.chunks = _AssistantsV1KnowledgeChunksResource(transport, knowledge_id)


class _AssistantsV1KnowledgeCallable:
    """Top-level ``client.assistants_v1.knowledge`` — callable + namespace."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, knowledge_id: str) -> _KnowledgeContext:
        return _KnowledgeContext(self._t, knowledge_id)

    def create(
        self,
        *,
        name: str,
        type: str,
        assistant_id: str | None = None,
        description: str | None = None,
        embedding_model: str | None = None,
        knowledge_source_details: dict[str, Any] | None = None,
    ) -> AssistantsV1Knowledge:
        body = CreateAssistantsV1KnowledgeRequest(
            name=name,
            type=type,
            assistant_id=assistant_id,
            description=description,
            embedding_model=embedding_model,
            knowledge_source_details=knowledge_source_details,
        ).to_json()
        return AssistantsV1Knowledge.model_validate(
            self._t.request("POST", "/v1/Knowledge", json=body)
        )

    def list(
        self,
        *,
        assistant_id: str | None = None,
        page_size: int | None = None,
    ) -> AssistantsV1KnowledgeList:
        return AssistantsV1KnowledgeList.model_validate(
            self._t.request(
                "GET",
                "/v1/Knowledge",
                params={"AssistantId": assistant_id, "PageSize": page_size},
            )
        )

    def fetch(self, knowledge_id: str) -> AssistantsV1Knowledge:
        return AssistantsV1Knowledge.model_validate(
            self._t.request("GET", f"/v1/Knowledge/{knowledge_id}")
        )

    def update(
        self,
        knowledge_id: str,
        *,
        name: str | None = None,
        type: str | None = None,
        description: str | None = None,
        embedding_model: str | None = None,
        knowledge_source_details: dict[str, Any] | None = None,
    ) -> AssistantsV1Knowledge:
        body = UpdateAssistantsV1KnowledgeRequest(
            name=name,
            type=type,
            description=description,
            embedding_model=embedding_model,
            knowledge_source_details=knowledge_source_details,
        ).to_json()
        return AssistantsV1Knowledge.model_validate(
            self._t.request("PUT", f"/v1/Knowledge/{knowledge_id}", json=body)
        )

    def delete(self, knowledge_id: str) -> None:
        self._t.request("DELETE", f"/v1/Knowledge/{knowledge_id}")


class _AssistantsV1SessionMessagesResource:
    """``/v1/Sessions/{id}/Messages`` (sync) — read-only message listing."""

    def __init__(self, transport: object, session_id: str) -> None:
        self._t = transport
        self._session = session_id

    def list(self, *, page_size: int | None = None) -> AssistantsV1MessageList:
        return AssistantsV1MessageList.model_validate(
            self._t.request(
                "GET",
                f"/v1/Sessions/{self._session}/Messages",
                params=_page_params(page_size=page_size),
            )
        )


class _SessionContext:
    """Returned by ``client.assistants_v1.sessions(id)`` — sub-resource factory."""

    def __init__(self, transport: object, session_id: str) -> None:
        self.messages = _AssistantsV1SessionMessagesResource(transport, session_id)


class _AssistantsV1SessionsCallable:
    """Top-level ``client.assistants_v1.sessions`` — callable + namespace."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, session_id: str) -> _SessionContext:
        return _SessionContext(self._t, session_id)

    def list(self, *, page_size: int | None = None) -> AssistantsV1SessionList:
        return AssistantsV1SessionList.model_validate(
            self._t.request(
                "GET",
                "/v1/Sessions",
                params=_page_params(page_size=page_size),
            )
        )

    def fetch(self, session_id: str) -> AssistantsV1Session:
        return AssistantsV1Session.model_validate(
            self._t.request("GET", f"/v1/Sessions/{session_id}")
        )


class _AssistantsV1PoliciesResource:
    """``/v1/Policies`` (sync) — read-only listing, filter by tool or knowledge."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def list(
        self,
        *,
        tool_id: str | None = None,
        knowledge_id: str | None = None,
        page_size: int | None = None,
    ) -> AssistantsV1PolicyList:
        return AssistantsV1PolicyList.model_validate(
            self._t.request(
                "GET",
                "/v1/Policies",
                params={
                    "ToolId": tool_id,
                    "KnowledgeId": knowledge_id,
                    "PageSize": page_size,
                },
            )
        )


class AssistantsV1Resource:
    """Holder for ``client.assistants_v1.*`` sub-resources (sync)."""

    def __init__(self, transport: object) -> None:
        self.assistants = _AssistantsV1AssistantsCallable(transport)
        self.tools = _AssistantsV1ToolsResource(transport)
        self.knowledge = _AssistantsV1KnowledgeCallable(transport)
        self.sessions = _AssistantsV1SessionsCallable(transport)
        self.policies = _AssistantsV1PoliciesResource(transport)


# ===========================================================================
# Async counterparts — same surface; methods are awaitable.
# ===========================================================================


class _AsyncAssistantsV1AssistantToolsResource:
    def __init__(self, transport: object, assistant_id: str) -> None:
        self._t = transport
        self._asst = assistant_id

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Assistants", self._asst, "Tools", *tail]
        return "/" + "/".join(parts)

    async def list(self, *, page_size: int | None = None) -> AssistantsV1ToolList:
        return AssistantsV1ToolList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def attach(self, tool_id: str) -> None:
        await self._t.request("POST", self._root(tool_id))

    async def detach(self, tool_id: str) -> None:
        await self._t.request("DELETE", self._root(tool_id))


class _AsyncAssistantsV1AssistantKnowledgeResource:
    def __init__(self, transport: object, assistant_id: str) -> None:
        self._t = transport
        self._asst = assistant_id

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Assistants", self._asst, "Knowledge", *tail]
        return "/" + "/".join(parts)

    async def list(self, *, page_size: int | None = None) -> AssistantsV1KnowledgeList:
        return AssistantsV1KnowledgeList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def attach(self, knowledge_id: str) -> None:
        await self._t.request("POST", self._root(knowledge_id))

    async def detach(self, knowledge_id: str) -> None:
        await self._t.request("DELETE", self._root(knowledge_id))


class _AsyncAssistantsV1AssistantFeedbacksResource:
    def __init__(self, transport: object, assistant_id: str) -> None:
        self._t = transport
        self._asst = assistant_id

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Assistants", self._asst, "Feedbacks", *tail]
        return "/" + "/".join(parts)

    async def list(self, *, page_size: int | None = None) -> AssistantsV1FeedbackList:
        return AssistantsV1FeedbackList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def create(
        self,
        *,
        session_id: str,
        message_id: str | None = None,
        score: float | None = None,
        text: str | None = None,
    ) -> AssistantsV1Feedback:
        body = CreateAssistantsV1FeedbackRequest(
            session_id=session_id,
            message_id=message_id,
            score=score,
            text=text,
        ).to_json()
        return AssistantsV1Feedback.model_validate(
            await self._t.request("POST", self._root(), json=body)
        )


class _AsyncAssistantsV1AssistantMessagesResource:
    def __init__(self, transport: object, assistant_id: str) -> None:
        self._t = transport
        self._asst = assistant_id

    def _root(self) -> str:
        return f"/v1/Assistants/{self._asst}/Messages"

    async def create(
        self,
        *,
        identity: str,
        body: str,
        session_id: str | None = None,
        webhook: str | None = None,
        mode: str | None = None,
    ) -> AssistantsV1SendMessageResponse:
        payload = SendAssistantsV1MessageRequest(
            identity=identity,
            body=body,
            session_id=session_id,
            webhook=webhook,
            mode=mode,
        ).to_json()
        return AssistantsV1SendMessageResponse.model_validate(
            await self._t.request("POST", self._root(), json=payload)
        )


class _AsyncAssistantContext:
    def __init__(self, transport: object, assistant_id: str) -> None:
        self.tools = _AsyncAssistantsV1AssistantToolsResource(transport, assistant_id)
        self.knowledge = _AsyncAssistantsV1AssistantKnowledgeResource(
            transport, assistant_id
        )
        self.feedbacks = _AsyncAssistantsV1AssistantFeedbacksResource(
            transport, assistant_id
        )
        self.messages = _AsyncAssistantsV1AssistantMessagesResource(
            transport, assistant_id
        )


class _AsyncAssistantsV1AssistantsCallable:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, assistant_id: str) -> _AsyncAssistantContext:
        return _AsyncAssistantContext(self._t, assistant_id)

    async def create(
        self,
        *,
        name: str,
        owner: str | None = None,
        personality_prompt: str | None = None,
        model: str | None = None,
        customer_ai: dict[str, Any] | None = None,
        segment_credential: dict[str, Any] | None = None,
    ) -> AssistantsV1Assistant:
        return AssistantsV1Assistant.model_validate(
            await self._t.request(
                "POST",
                "/v1/Assistants",
                json=_assistant_create_body(
                    name=name,
                    owner=owner,
                    personality_prompt=personality_prompt,
                    model=model,
                    customer_ai=customer_ai,
                    segment_credential=segment_credential,
                ),
            )
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> AssistantsV1AssistantList:
        return AssistantsV1AssistantList.model_validate(
            await self._t.request(
                "GET",
                "/v1/Assistants",
                params=_page_params(page_size=page_size),
            )
        )

    async def fetch(
        self, assistant_id: str
    ) -> AssistantsV1AssistantWithToolsAndKnowledge:
        return AssistantsV1AssistantWithToolsAndKnowledge.model_validate(
            await self._t.request("GET", f"/v1/Assistants/{assistant_id}")
        )

    async def update(
        self,
        assistant_id: str,
        *,
        name: str | None = None,
        owner: str | None = None,
        personality_prompt: str | None = None,
        model: str | None = None,
        customer_ai: dict[str, Any] | None = None,
        segment_credential: dict[str, Any] | None = None,
    ) -> AssistantsV1Assistant:
        return AssistantsV1Assistant.model_validate(
            await self._t.request(
                "PUT",
                f"/v1/Assistants/{assistant_id}",
                json=_assistant_update_body(
                    name=name,
                    owner=owner,
                    personality_prompt=personality_prompt,
                    model=model,
                    customer_ai=customer_ai,
                    segment_credential=segment_credential,
                ),
            )
        )

    async def delete(self, assistant_id: str) -> None:
        await self._t.request("DELETE", f"/v1/Assistants/{assistant_id}")


class _AsyncAssistantsV1ToolsResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def create(
        self,
        *,
        name: str,
        type: str,
        enabled: bool,
        assistant_id: str | None = None,
        description: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> AssistantsV1Tool:
        body = CreateAssistantsV1ToolRequest(
            name=name,
            type=type,
            enabled=enabled,
            assistant_id=assistant_id,
            description=description,
            meta=meta,
        ).to_json()
        return AssistantsV1Tool.model_validate(
            await self._t.request("POST", "/v1/Tools", json=body)
        )

    async def list(
        self,
        *,
        assistant_id: str | None = None,
        page_size: int | None = None,
    ) -> AssistantsV1ToolList:
        return AssistantsV1ToolList.model_validate(
            await self._t.request(
                "GET",
                "/v1/Tools",
                params={"AssistantId": assistant_id, "PageSize": page_size},
            )
        )

    async def fetch(self, tool_id: str) -> AssistantsV1ToolWithPolicies:
        return AssistantsV1ToolWithPolicies.model_validate(
            await self._t.request("GET", f"/v1/Tools/{tool_id}")
        )

    async def update(
        self,
        tool_id: str,
        *,
        name: str | None = None,
        type: str | None = None,
        enabled: bool | None = None,
        description: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> AssistantsV1Tool:
        body = UpdateAssistantsV1ToolRequest(
            name=name,
            type=type,
            enabled=enabled,
            description=description,
            meta=meta,
        ).to_json()
        return AssistantsV1Tool.model_validate(
            await self._t.request("PUT", f"/v1/Tools/{tool_id}", json=body)
        )

    async def delete(self, tool_id: str) -> None:
        await self._t.request("DELETE", f"/v1/Tools/{tool_id}")


class _AsyncAssistantsV1KnowledgeStatusResource:
    def __init__(self, transport: object, knowledge_id: str) -> None:
        self._t = transport
        self._know = knowledge_id

    async def fetch(self) -> AssistantsV1KnowledgeStatus:
        return AssistantsV1KnowledgeStatus.model_validate(
            await self._t.request("GET", f"/v1/Knowledge/{self._know}/Status")
        )


class _AsyncAssistantsV1KnowledgeChunksResource:
    def __init__(self, transport: object, knowledge_id: str) -> None:
        self._t = transport
        self._know = knowledge_id

    async def list(
        self, *, page_size: int | None = None
    ) -> AssistantsV1KnowledgeChunkList:
        return AssistantsV1KnowledgeChunkList.model_validate(
            await self._t.request(
                "GET",
                f"/v1/Knowledge/{self._know}/Chunks",
                params=_page_params(page_size=page_size),
            )
        )


class _AsyncKnowledgeContext:
    def __init__(self, transport: object, knowledge_id: str) -> None:
        self.status = _AsyncAssistantsV1KnowledgeStatusResource(
            transport, knowledge_id
        )
        self.chunks = _AsyncAssistantsV1KnowledgeChunksResource(
            transport, knowledge_id
        )


class _AsyncAssistantsV1KnowledgeCallable:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, knowledge_id: str) -> _AsyncKnowledgeContext:
        return _AsyncKnowledgeContext(self._t, knowledge_id)

    async def create(
        self,
        *,
        name: str,
        type: str,
        assistant_id: str | None = None,
        description: str | None = None,
        embedding_model: str | None = None,
        knowledge_source_details: dict[str, Any] | None = None,
    ) -> AssistantsV1Knowledge:
        body = CreateAssistantsV1KnowledgeRequest(
            name=name,
            type=type,
            assistant_id=assistant_id,
            description=description,
            embedding_model=embedding_model,
            knowledge_source_details=knowledge_source_details,
        ).to_json()
        return AssistantsV1Knowledge.model_validate(
            await self._t.request("POST", "/v1/Knowledge", json=body)
        )

    async def list(
        self,
        *,
        assistant_id: str | None = None,
        page_size: int | None = None,
    ) -> AssistantsV1KnowledgeList:
        return AssistantsV1KnowledgeList.model_validate(
            await self._t.request(
                "GET",
                "/v1/Knowledge",
                params={"AssistantId": assistant_id, "PageSize": page_size},
            )
        )

    async def fetch(self, knowledge_id: str) -> AssistantsV1Knowledge:
        return AssistantsV1Knowledge.model_validate(
            await self._t.request("GET", f"/v1/Knowledge/{knowledge_id}")
        )

    async def update(
        self,
        knowledge_id: str,
        *,
        name: str | None = None,
        type: str | None = None,
        description: str | None = None,
        embedding_model: str | None = None,
        knowledge_source_details: dict[str, Any] | None = None,
    ) -> AssistantsV1Knowledge:
        body = UpdateAssistantsV1KnowledgeRequest(
            name=name,
            type=type,
            description=description,
            embedding_model=embedding_model,
            knowledge_source_details=knowledge_source_details,
        ).to_json()
        return AssistantsV1Knowledge.model_validate(
            await self._t.request("PUT", f"/v1/Knowledge/{knowledge_id}", json=body)
        )

    async def delete(self, knowledge_id: str) -> None:
        await self._t.request("DELETE", f"/v1/Knowledge/{knowledge_id}")


class _AsyncAssistantsV1SessionMessagesResource:
    def __init__(self, transport: object, session_id: str) -> None:
        self._t = transport
        self._session = session_id

    async def list(self, *, page_size: int | None = None) -> AssistantsV1MessageList:
        return AssistantsV1MessageList.model_validate(
            await self._t.request(
                "GET",
                f"/v1/Sessions/{self._session}/Messages",
                params=_page_params(page_size=page_size),
            )
        )


class _AsyncSessionContext:
    def __init__(self, transport: object, session_id: str) -> None:
        self.messages = _AsyncAssistantsV1SessionMessagesResource(transport, session_id)


class _AsyncAssistantsV1SessionsCallable:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, session_id: str) -> _AsyncSessionContext:
        return _AsyncSessionContext(self._t, session_id)

    async def list(self, *, page_size: int | None = None) -> AssistantsV1SessionList:
        return AssistantsV1SessionList.model_validate(
            await self._t.request(
                "GET",
                "/v1/Sessions",
                params=_page_params(page_size=page_size),
            )
        )

    async def fetch(self, session_id: str) -> AssistantsV1Session:
        return AssistantsV1Session.model_validate(
            await self._t.request("GET", f"/v1/Sessions/{session_id}")
        )


class _AsyncAssistantsV1PoliciesResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def list(
        self,
        *,
        tool_id: str | None = None,
        knowledge_id: str | None = None,
        page_size: int | None = None,
    ) -> AssistantsV1PolicyList:
        return AssistantsV1PolicyList.model_validate(
            await self._t.request(
                "GET",
                "/v1/Policies",
                params={
                    "ToolId": tool_id,
                    "KnowledgeId": knowledge_id,
                    "PageSize": page_size,
                },
            )
        )


class AssistantsV1AsyncResource:
    """Holder for ``client.assistants_v1.*`` sub-resources (async)."""

    def __init__(self, transport: object) -> None:
        self.assistants = _AsyncAssistantsV1AssistantsCallable(transport)
        self.tools = _AsyncAssistantsV1ToolsResource(transport)
        self.knowledge = _AsyncAssistantsV1KnowledgeCallable(transport)
        self.sessions = _AsyncAssistantsV1SessionsCallable(transport)
        self.policies = _AsyncAssistantsV1PoliciesResource(transport)
