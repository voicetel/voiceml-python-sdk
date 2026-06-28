"""Assistants v1 resources — VoiceML ``/v1/Assistants…`` REST surface.

Sits at ``/v1/`` paths alongside Conversations v1 / Voice v1 / SIP Trunking,
with the account resolved from HTTP Basic auth (no ``AccountSid`` segment).

Seven resource families:

- ``Assistant`` (``aia_asst_…``) — the AI assistant itself (BYO-LLM model,
  personality prompt, customer-AI config).
- ``Tool`` (``aia_tool_…``) — callable tools the assistant can dispatch,
  with attach/detach + per-assistant list under
  ``/v1/Assistants/{id}/Tools``.
- ``Knowledge`` (``aia_know_…``) — retrieval sources (with read-only
  ``Status`` + ``Chunks`` sub-resources) and per-assistant attach.
- ``Session`` — a conversational session between an identity and an
  Assistant; messages are listed via ``/v1/Sessions/{id}/Messages``.
- ``Message`` — sent via ``POST /v1/Assistants/{id}/Messages``, returning
  a synchronous send-result envelope.
- ``Feedback`` (``aia_fdbk_…``) — per-assistant feedback rows.
- ``Policy`` (``aia_plcy_…``) — read-only authorization policy listing.

Unlike the form-encoded Twilio classic surfaces, every Assistants v1 request
body is ``application/json``. Request models therefore expose a ``to_json()``
helper that emits an ``exclude_unset`` snake-case dict suitable for the
transport's ``json=`` kwarg, while still inheriting ``to_form()`` from
:class:`_Base` for any caller that needs the form-encoded shape.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ._base import _Base
from .voice_v1 import VoiceV1Meta


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class AssistantsV1Assistant(_Base):
    """An AI Assistant — BYO-LLM agent with personality prompt and customer-AI knobs (``aia_asst_…``)."""

    account_sid: str | None = None
    customer_ai: dict[str, Any] | None = None
    id: str | None = None
    model: str | None = None
    name: str | None = None
    owner: str | None = None
    url: str | None = None
    personality_prompt: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class AssistantsV1AssistantList(_Base):
    assistants: list[AssistantsV1Assistant] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class AssistantsV1Tool(_Base):
    """A callable Tool the Assistant can dispatch (``aia_tool_…``)."""

    account_sid: str | None = None
    description: str | None = None
    enabled: bool | None = None
    id: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    requires_auth: bool | None = None
    type: str | None = None
    url: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class AssistantsV1ToolList(_Base):
    tools: list[AssistantsV1Tool] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class AssistantsV1Policy(_Base):
    """An authorization Policy attached to a Tool or Knowledge (``aia_plcy_…``)."""

    id: str | None = None
    name: str | None = None
    description: str | None = None
    account_sid: str | None = None
    user_sid: str | None = None
    type: str | None = None
    policy_details: dict[str, Any] | None = None
    date_created: str | None = None
    date_updated: str | None = None


class AssistantsV1PolicyList(_Base):
    policies: list[AssistantsV1Policy] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class AssistantsV1ToolWithPolicies(_Base):
    """A Tool plus its attached policies — returned by ``GET /v1/Tools/{id}``."""

    account_sid: str | None = None
    description: str | None = None
    enabled: bool | None = None
    id: str | None = None
    meta: dict[str, Any] | None = None
    name: str | None = None
    requires_auth: bool | None = None
    type: str | None = None
    url: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    policies: list[AssistantsV1Policy] | None = None


class AssistantsV1Knowledge(_Base):
    """A Knowledge source the Assistant can retrieve from (``aia_know_…``)."""

    description: str | None = None
    id: str | None = None
    account_sid: str | None = None
    knowledge_source_details: dict[str, Any] | None = None
    name: str | None = None
    status: str | None = None
    type: str | None = None
    url: str | None = None
    embedding_model: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class AssistantsV1KnowledgeList(_Base):
    knowledge: list[AssistantsV1Knowledge] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class AssistantsV1KnowledgeStatus(_Base):
    """Knowledge ingestion status — returned by ``GET /v1/Knowledge/{id}/Status``."""

    account_sid: str | None = None
    status: str | None = None
    last_status: str | None = None
    date_updated: str | None = None


class AssistantsV1KnowledgeChunk(_Base):
    """A single retrievable chunk inside a Knowledge source."""

    account_sid: str | None = None
    content: str | None = None
    metadata: dict[str, Any] | None = None
    date_created: str | None = None
    date_updated: str | None = None


class AssistantsV1KnowledgeChunkList(_Base):
    chunks: list[AssistantsV1KnowledgeChunk] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class AssistantsV1AssistantWithToolsAndKnowledge(_Base):
    """An Assistant plus its attached tools and knowledge — returned by ``GET /v1/Assistants/{id}``."""

    account_sid: str | None = None
    customer_ai: dict[str, Any] | None = None
    id: str | None = None
    model: str | None = None
    name: str | None = None
    owner: str | None = None
    url: str | None = None
    personality_prompt: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    tools: list[AssistantsV1Tool] | None = None
    knowledge: list[AssistantsV1Knowledge] | None = None


class AssistantsV1Session(_Base):
    """A conversational session between an identity and an Assistant."""

    id: str | None = None
    account_sid: str | None = None
    assistant_id: str | None = None
    verified: bool | None = None
    identity: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class AssistantsV1SessionList(_Base):
    sessions: list[AssistantsV1Session] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class AssistantsV1Message(_Base):
    """A single Message inside a Session (``aia_msg_…``)."""

    id: str | None = None
    account_sid: str | None = None
    assistant_id: str | None = None
    session_id: str | None = None
    identity: str | None = None
    role: str | None = None
    content: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None
    date_created: str | None = None
    date_updated: str | None = None


class AssistantsV1MessageList(_Base):
    messages: list[AssistantsV1Message] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class AssistantsV1SendMessageResponse(_Base):
    """Synchronous send-result envelope — returned by ``POST /v1/Assistants/{id}/Messages``."""

    status: str | None = None
    flagged: bool | None = None
    aborted: bool | None = None
    session_id: str | None = None
    account_sid: str | None = None
    body: str | None = None
    error: str | None = None


class AssistantsV1Feedback(_Base):
    """A piece of Feedback on an Assistant interaction (``aia_fdbk_…``)."""

    assistant_id: str | None = None
    id: str | None = None
    account_sid: str | None = None
    user_sid: str | None = None
    message_id: str | None = None
    score: float | None = None
    session_id: str | None = None
    text: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class AssistantsV1FeedbackList(_Base):
    feedbacks: list[AssistantsV1Feedback] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


# ---------------------------------------------------------------------------
# Request models — Assistants v1 uses application/json bodies, not form.
#
# Field names match the JSON keys on the wire (snake_case). ``to_json()`` is
# a thin convenience that mirrors ``_Base.to_form()`` but skips the
# form-encoding coercions (booleans stay native, lists stay lists).
# ---------------------------------------------------------------------------


class _JsonBody(_Base):
    """Request models for JSON-bodied endpoints."""

    def to_json(self) -> dict[str, Any]:
        """Render as a JSON-encodable dict — only fields the caller set to a
        non-``None`` value are emitted.

        ``None`` is filtered to match the form-encoded ``to_form()`` policy:
        the resource-layer helpers always pass every keyword arg through to
        the request model (including the unspecified ``... = None`` ones), so
        relying on ``exclude_unset`` alone would round-trip those nulls onto
        the wire. Twilio-shape callers expect omitted fields to be absent
        from the JSON body, not present as ``null``.
        """
        raw = self.model_dump(exclude_unset=True, by_alias=True, mode="json")
        return {k: v for k, v in raw.items() if v is not None}


class CreateAssistantsV1AssistantRequest(_JsonBody):
    """Body for ``POST /v1/Assistants``. ``name`` is required."""

    name: str
    owner: str | None = None
    personality_prompt: str | None = None
    model: str | None = None
    customer_ai: dict[str, Any] | None = None
    segment_credential: dict[str, Any] | None = None


class UpdateAssistantsV1AssistantRequest(_JsonBody):
    """Body for ``PUT /v1/Assistants/{id}``. All fields optional."""

    name: str | None = None
    owner: str | None = None
    personality_prompt: str | None = None
    model: str | None = None
    customer_ai: dict[str, Any] | None = None
    segment_credential: dict[str, Any] | None = None


class CreateAssistantsV1ToolRequest(_JsonBody):
    """Body for ``POST /v1/Tools``. ``name``, ``type``, ``enabled`` required."""

    name: str
    type: str
    enabled: bool
    assistant_id: str | None = None
    description: str | None = None
    meta: dict[str, Any] | None = None


class UpdateAssistantsV1ToolRequest(_JsonBody):
    """Body for ``PUT /v1/Tools/{id}``. All fields optional."""

    name: str | None = None
    type: str | None = None
    enabled: bool | None = None
    description: str | None = None
    meta: dict[str, Any] | None = None


class CreateAssistantsV1KnowledgeRequest(_JsonBody):
    """Body for ``POST /v1/Knowledge``. ``name`` and ``type`` required."""

    name: str
    type: str
    assistant_id: str | None = None
    description: str | None = None
    embedding_model: str | None = None
    knowledge_source_details: dict[str, Any] | None = None


class UpdateAssistantsV1KnowledgeRequest(_JsonBody):
    """Body for ``PUT /v1/Knowledge/{id}``. All fields optional."""

    name: str | None = None
    type: str | None = None
    description: str | None = None
    embedding_model: str | None = None
    knowledge_source_details: dict[str, Any] | None = None


class SendAssistantsV1MessageRequest(_JsonBody):
    """Body for ``POST /v1/Assistants/{id}/Messages``. ``identity``, ``body`` required."""

    identity: str
    body: str
    session_id: str | None = None
    webhook: str | None = None
    mode: str | None = None


class CreateAssistantsV1FeedbackRequest(_JsonBody):
    """Body for ``POST /v1/Assistants/{id}/Feedbacks``. ``session_id`` required."""

    session_id: str
    message_id: str | None = None
    score: float | None = None
    text: str | None = None
