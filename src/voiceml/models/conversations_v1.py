"""Conversations v1 resources — Twilio ``conversations.twilio.com/v1`` REST surface.

Sits outside the ``/2010-04-01/`` Twilio-API-classic namespace at ``/v1/`` paths.
Account is resolved from HTTP Basic auth (no ``AccountSid`` segment in URLs).
List responses carry the shared ``meta`` envelope (:class:`VoiceV1Meta`).

The Conversations namespace covers a stateful multi-party messaging surface:

- ``Conversation`` (``CH``) — the threaded message store.
- ``Conversation/Messages`` (``IM``) with read-only per-channel ``Receipts``
  (``DY``).
- ``Conversation/Participants`` (``MB``) — chat identities and SMS bindings.
- ``Conversation/Webhooks`` (``WH``) — per-conversation event scoping.
- ``Roles`` (``RL``) — permission grants for users and participants.
- ``Users`` (``US``) and per-user ``UserConversations`` membership rows.
- ``Credentials`` (``CR``) — APN/GCM/FCM push credentials.
- ``Configuration`` (``account_sid``-keyed singleton), with nested
  ``Configuration/Webhooks`` and ``Configuration/Addresses`` (``IG``).
- ``ParticipantConversations`` — flat read of a participant's threads.
- ``ConversationWithParticipants`` — atomic create-with-roster.
- ``Services`` (``IS``) — chat-service tenancy boundary.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ._base import _Base
from .voice_v1 import VoiceV1Meta


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ConversationsV1Conversation(_Base):
    """A Twilio Conversation — stateful multi-party message thread (``CH…``)."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    messaging_service_sid: str | None = None
    sid: str | None = None
    friendly_name: str | None = None
    unique_name: str | None = None
    attributes: str | None = None
    state: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    timers: dict[str, Any] | None = None
    url: str | None = None
    links: dict[str, Any] | None = None
    bindings: dict[str, Any] | None = None


class ConversationsV1ConversationList(_Base):
    conversations: list[ConversationsV1Conversation] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1ConversationMessage(_Base):
    """A single message in a Conversation (``IM…``).

    ``index`` is a server-assigned monotonic counter within the thread.
    """

    account_sid: str | None = None
    conversation_sid: str | None = None
    sid: str | None = None
    index: int | None = None
    author: str | None = None
    body: str | None = None
    media: list[dict[str, Any]] | None = None
    attributes: str | None = None
    participant_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None
    delivery: dict[str, Any] | None = None
    links: dict[str, Any] | None = None
    content_sid: str | None = None


class ConversationsV1ConversationMessageList(_Base):
    messages: list[ConversationsV1ConversationMessage] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1ConversationParticipant(_Base):
    """A Participant in a Conversation (``MB…``).

    Either a chat ``identity`` or an SMS ``messaging_binding`` is set,
    depending on the participant's channel.
    """

    account_sid: str | None = None
    conversation_sid: str | None = None
    sid: str | None = None
    identity: str | None = None
    attributes: str | None = None
    messaging_binding: dict[str, Any] | None = None
    role_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None
    last_read_message_index: int | None = None
    last_read_timestamp: str | None = None


class ConversationsV1ConversationParticipantList(_Base):
    participants: list[ConversationsV1ConversationParticipant] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1ConversationMessageReceipt(_Base):
    """A per-channel delivery receipt for one Message (``DY…``)."""

    account_sid: str | None = None
    conversation_sid: str | None = None
    sid: str | None = None
    message_sid: str | None = None
    channel_message_sid: str | None = None
    participant_sid: str | None = None
    status: str | None = None
    error_code: int | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None


class ConversationsV1ConversationMessageReceiptList(_Base):
    delivery_receipts: list[ConversationsV1ConversationMessageReceipt] = Field(
        default_factory=list
    )
    meta: VoiceV1Meta | None = None


class ConversationsV1ConversationScopedWebhook(_Base):
    """A per-conversation event webhook binding (``WH…``)."""

    sid: str | None = None
    account_sid: str | None = None
    conversation_sid: str | None = None
    target: str | None = None
    url: str | None = None
    configuration: dict[str, Any] | None = None
    date_created: str | None = None
    date_updated: str | None = None


class ConversationsV1ConversationScopedWebhookList(_Base):
    webhooks: list[ConversationsV1ConversationScopedWebhook] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1Role(_Base):
    """A permission grant for a User or Participant (``RL…``).

    ``type`` is ``conversation`` or ``service``; ``permissions`` is a free-
    form set of grant strings (e.g. ``sendMessage``).
    """

    sid: str | None = None
    account_sid: str | None = None
    chat_service_sid: str | None = None
    friendly_name: str | None = None
    type: str | None = None
    permissions: list[str] | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None


class ConversationsV1RoleList(_Base):
    roles: list[ConversationsV1Role] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1User(_Base):
    """A chat User identity (``US…``)."""

    sid: str | None = None
    account_sid: str | None = None
    chat_service_sid: str | None = None
    role_sid: str | None = None
    identity: str | None = None
    friendly_name: str | None = None
    attributes: str | None = None
    is_online: bool | None = None
    is_notifiable: bool | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None
    links: dict[str, Any] | None = None


class ConversationsV1UserList(_Base):
    users: list[ConversationsV1User] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1Credential(_Base):
    """A push-notification Credential (``CR…``) — APN, GCM, or FCM."""

    sid: str | None = None
    account_sid: str | None = None
    friendly_name: str | None = None
    type: str | None = None
    sandbox: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None


class ConversationsV1CredentialList(_Base):
    credentials: list[ConversationsV1Credential] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1Configuration(_Base):
    """Account-wide Conversations configuration (singleton)."""

    account_sid: str | None = None
    default_chat_service_sid: str | None = None
    default_messaging_service_sid: str | None = None
    default_inactive_timer: str | None = None
    default_closed_timer: str | None = None
    url: str | None = None
    links: dict[str, Any] | None = None


class ConversationsV1ConfigurationWebhook(_Base):
    """Account-global Conversations webhook config (singleton)."""

    account_sid: str | None = None
    method: str | None = None
    filters: list[str] | None = None
    pre_webhook_url: str | None = None
    post_webhook_url: str | None = None
    target: str | None = None
    url: str | None = None


class ConversationsV1ConfigAddress(_Base):
    """A Configuration Address that auto-creates Conversations on inbound (``IG…``)."""

    sid: str | None = None
    account_sid: str | None = None
    type: str | None = None
    address: str | None = None
    friendly_name: str | None = None
    auto_creation: dict[str, Any] | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None
    address_country: str | None = None


class ConversationsV1ConfigAddressList(_Base):
    addresses: list[ConversationsV1ConfigAddress] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1ParticipantConversation(_Base):
    """A flat row in the participant-conversations index (no own ``sid``).

    Lists every Conversation a participant belongs to with a single GET.
    """

    account_sid: str | None = None
    chat_service_sid: str | None = None
    participant_sid: str | None = None
    participant_user_sid: str | None = None
    participant_identity: str | None = None
    participant_messaging_binding: dict[str, Any] | None = None
    conversation_sid: str | None = None
    conversation_unique_name: str | None = None
    conversation_friendly_name: str | None = None
    conversation_attributes: str | None = None
    conversation_date_created: str | None = None
    conversation_date_updated: str | None = None
    conversation_created_by: str | None = None
    conversation_state: str | None = None
    conversation_timers: dict[str, Any] | None = None
    links: dict[str, Any] | None = None


class ConversationsV1ParticipantConversationList(_Base):
    conversations: list[ConversationsV1ParticipantConversation] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1ConversationWithParticipants(_Base):
    """A Conversation created with its initial participants in one atomic call."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    messaging_service_sid: str | None = None
    sid: str | None = None
    friendly_name: str | None = None
    unique_name: str | None = None
    attributes: str | None = None
    state: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    timers: dict[str, Any] | None = None
    links: dict[str, Any] | None = None
    bindings: dict[str, Any] | None = None
    url: str | None = None


class ConversationsV1UserConversation(_Base):
    """A User's per-Conversation membership state — unread counts, mute level."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    conversation_sid: str | None = None
    unread_messages_count: int | None = None
    last_read_message_index: int | None = None
    participant_sid: str | None = None
    user_sid: str | None = None
    friendly_name: str | None = None
    conversation_state: str | None = None
    timers: dict[str, Any] | None = None
    attributes: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    created_by: str | None = None
    notification_level: str | None = None
    unique_name: str | None = None
    url: str | None = None
    links: dict[str, Any] | None = None


class ConversationsV1UserConversationList(_Base):
    conversations: list[ConversationsV1UserConversation] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1Service(_Base):
    """A chat Service — tenancy boundary for Conversations (``IS…``)."""

    sid: str | None = None
    account_sid: str | None = None
    friendly_name: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None
    links: dict[str, Any] | None = None


class ConversationsV1ServiceList(_Base):
    services: list[ConversationsV1Service] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


# ---------------------------------------------------------------------------
# Request models (form-encoded bodies)
#
# Fields whose wire names contain dots (e.g. ``Timers.Inactive``) keep the
# dotted form as the Pydantic ``alias=`` — that's what ``to_form()`` emits.
# The Python field name uses underscores so the model can be constructed
# with regular keyword args without resorting to ``**{"Timers.Inactive": …}``.
# ---------------------------------------------------------------------------


class CreateConversationsV1ConversationRequest(_Base):
    """Body for ``POST /v1/Conversations``. All fields optional."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    unique_name: str | None = Field(default=None, alias="UniqueName")
    messaging_service_sid: str | None = Field(default=None, alias="MessagingServiceSid")
    attributes: str | None = Field(default=None, alias="Attributes")
    state: str | None = Field(default=None, alias="State")
    timers_inactive: str | None = Field(default=None, alias="Timers.Inactive")
    timers_closed: str | None = Field(default=None, alias="Timers.Closed")
    bindings_email_address: str | None = Field(
        default=None, alias="Bindings.Email.Address"
    )
    bindings_email_name: str | None = Field(default=None, alias="Bindings.Email.Name")


class UpdateConversationsV1ConversationRequest(_Base):
    """Body for ``POST /v1/Conversations/{ConversationSid}``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    unique_name: str | None = Field(default=None, alias="UniqueName")
    messaging_service_sid: str | None = Field(default=None, alias="MessagingServiceSid")
    attributes: str | None = Field(default=None, alias="Attributes")
    state: str | None = Field(default=None, alias="State")
    timers_inactive: str | None = Field(default=None, alias="Timers.Inactive")
    timers_closed: str | None = Field(default=None, alias="Timers.Closed")


class CreateConversationsV1ConversationMessageRequest(_Base):
    """Body for ``POST /v1/Conversations/{ConversationSid}/Messages``."""

    author: str | None = Field(default=None, alias="Author")
    body: str | None = Field(default=None, alias="Body")
    attributes: str | None = Field(default=None, alias="Attributes")
    content_sid: str | None = Field(default=None, alias="ContentSid")


class UpdateConversationsV1ConversationMessageRequest(_Base):
    """Body for ``POST /v1/Conversations/{ConversationSid}/Messages/{MessageSid}``."""

    author: str | None = Field(default=None, alias="Author")
    body: str | None = Field(default=None, alias="Body")
    attributes: str | None = Field(default=None, alias="Attributes")


class CreateConversationsV1ConversationParticipantRequest(_Base):
    """Body for ``POST /v1/Conversations/{ConversationSid}/Participants``."""

    identity: str | None = Field(default=None, alias="Identity")
    attributes: str | None = Field(default=None, alias="Attributes")
    role_sid: str | None = Field(default=None, alias="RoleSid")
    messaging_binding_address: str | None = Field(
        default=None, alias="MessagingBinding.Address"
    )
    messaging_binding_proxy_address: str | None = Field(
        default=None, alias="MessagingBinding.ProxyAddress"
    )
    messaging_binding_projected_address: str | None = Field(
        default=None, alias="MessagingBinding.ProjectedAddress"
    )


class UpdateConversationsV1ConversationParticipantRequest(_Base):
    """Body for ``POST /v1/Conversations/{ConversationSid}/Participants/{ParticipantSid}``."""

    identity: str | None = Field(default=None, alias="Identity")
    attributes: str | None = Field(default=None, alias="Attributes")
    role_sid: str | None = Field(default=None, alias="RoleSid")
    last_read_message_index: int | None = Field(
        default=None, alias="LastReadMessageIndex"
    )
    last_read_timestamp: str | None = Field(default=None, alias="LastReadTimestamp")


class CreateConversationsV1ConversationScopedWebhookRequest(_Base):
    """Body for ``POST /v1/Conversations/{ConversationSid}/Webhooks``. ``Target`` required."""

    target: str = Field(alias="Target")
    configuration_url: str | None = Field(default=None, alias="Configuration.Url")
    configuration_method: str | None = Field(
        default=None, alias="Configuration.Method"
    )
    configuration_flow_sid: str | None = Field(
        default=None, alias="Configuration.FlowSid"
    )
    configuration_replay_after: int | None = Field(
        default=None, alias="Configuration.ReplayAfter"
    )


class UpdateConversationsV1ConversationScopedWebhookRequest(_Base):
    """Body for ``POST /v1/Conversations/{ConversationSid}/Webhooks/{WebhookSid}``."""

    configuration_url: str | None = Field(default=None, alias="Configuration.Url")
    configuration_method: str | None = Field(
        default=None, alias="Configuration.Method"
    )
    configuration_flow_sid: str | None = Field(
        default=None, alias="Configuration.FlowSid"
    )


class CreateConversationsV1RoleRequest(_Base):
    """Body for ``POST /v1/Roles``. All three fields are required."""

    friendly_name: str = Field(alias="FriendlyName")
    type: str = Field(alias="Type")
    permission: list[str] = Field(alias="Permission")


class UpdateConversationsV1RoleRequest(_Base):
    """Body for ``POST /v1/Roles/{Sid}``. ``Permission`` is required."""

    permission: list[str] = Field(alias="Permission")


class CreateConversationsV1UserRequest(_Base):
    """Body for ``POST /v1/Users``. ``Identity`` is required."""

    identity: str = Field(alias="Identity")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    attributes: str | None = Field(default=None, alias="Attributes")
    role_sid: str | None = Field(default=None, alias="RoleSid")


class UpdateConversationsV1UserRequest(_Base):
    """Body for ``POST /v1/Users/{Sid}``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    attributes: str | None = Field(default=None, alias="Attributes")
    role_sid: str | None = Field(default=None, alias="RoleSid")


class UpdateConversationsV1UserConversationRequest(_Base):
    """Body for ``POST /v1/Users/{Sid}/Conversations/{ConversationSid}``."""

    notification_level: str | None = Field(default=None, alias="NotificationLevel")
    last_read_message_index: int | None = Field(
        default=None, alias="LastReadMessageIndex"
    )
    last_read_timestamp: str | None = Field(default=None, alias="LastReadTimestamp")


class CreateConversationsV1CredentialRequest(_Base):
    """Body for ``POST /v1/Credentials``. ``Type`` is required."""

    type: str = Field(alias="Type")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    certificate: str | None = Field(default=None, alias="Certificate")
    private_key: str | None = Field(default=None, alias="PrivateKey")
    sandbox: bool | None = Field(default=None, alias="Sandbox")
    api_key: str | None = Field(default=None, alias="ApiKey")
    secret: str | None = Field(default=None, alias="Secret")


class UpdateConversationsV1CredentialRequest(_Base):
    """Body for ``POST /v1/Credentials/{Sid}``."""

    type: str | None = Field(default=None, alias="Type")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    certificate: str | None = Field(default=None, alias="Certificate")
    private_key: str | None = Field(default=None, alias="PrivateKey")
    sandbox: bool | None = Field(default=None, alias="Sandbox")
    api_key: str | None = Field(default=None, alias="ApiKey")
    secret: str | None = Field(default=None, alias="Secret")


class UpdateConversationsV1ConfigurationRequest(_Base):
    """Body for ``POST /v1/Configuration``."""

    default_chat_service_sid: str | None = Field(
        default=None, alias="DefaultChatServiceSid"
    )
    default_messaging_service_sid: str | None = Field(
        default=None, alias="DefaultMessagingServiceSid"
    )
    default_inactive_timer: str | None = Field(
        default=None, alias="DefaultInactiveTimer"
    )
    default_closed_timer: str | None = Field(default=None, alias="DefaultClosedTimer")


class UpdateConversationsV1ConfigurationWebhookRequest(_Base):
    """Body for ``POST /v1/Configuration/Webhooks``.

    ``Filters`` is a repeated form param — the transport encodes the list
    as ``Filters=…&Filters=…``.
    """

    method: str | None = Field(default=None, alias="Method")
    filters: list[str] | None = Field(default=None, alias="Filters")
    pre_webhook_url: str | None = Field(default=None, alias="PreWebhookUrl")
    post_webhook_url: str | None = Field(default=None, alias="PostWebhookUrl")
    target: str | None = Field(default=None, alias="Target")


class CreateConversationsV1ConfigAddressRequest(_Base):
    """Body for ``POST /v1/Configuration/Addresses``. ``Type`` + ``Address`` required."""

    type: str = Field(alias="Type")
    address: str = Field(alias="Address")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    auto_creation_enabled: bool | None = Field(
        default=None, alias="AutoCreation.Enabled"
    )
    auto_creation_type: str | None = Field(default=None, alias="AutoCreation.Type")
    auto_creation_webhook_url: str | None = Field(
        default=None, alias="AutoCreation.WebhookUrl"
    )
    address_country: str | None = Field(default=None, alias="AddressCountry")


class UpdateConversationsV1ConfigAddressRequest(_Base):
    """Body for ``POST /v1/Configuration/Addresses/{Sid}``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    auto_creation_enabled: bool | None = Field(
        default=None, alias="AutoCreation.Enabled"
    )
    auto_creation_type: str | None = Field(default=None, alias="AutoCreation.Type")
    auto_creation_webhook_url: str | None = Field(
        default=None, alias="AutoCreation.WebhookUrl"
    )


class CreateConversationsV1ConversationWithParticipantsRequest(_Base):
    """Body for ``POST /v1/ConversationWithParticipants``.

    ``Participant`` is repeated; each entry is a JSON string describing one
    participant. The transport encodes the list as ``Participant=…&Participant=…``.
    """

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    unique_name: str | None = Field(default=None, alias="UniqueName")
    messaging_service_sid: str | None = Field(default=None, alias="MessagingServiceSid")
    attributes: str | None = Field(default=None, alias="Attributes")
    state: str | None = Field(default=None, alias="State")
    timers_inactive: str | None = Field(default=None, alias="Timers.Inactive")
    timers_closed: str | None = Field(default=None, alias="Timers.Closed")
    participant: list[str] | None = Field(default=None, alias="Participant")


class CreateConversationsV1ServiceRequest(_Base):
    """Body for ``POST /v1/Services``. ``FriendlyName`` is required."""

    friendly_name: str = Field(alias="FriendlyName")


# ---------------------------------------------------------------------------
# Phase 4 — service-scoped (``/v1/Services/{ChatServiceSid}/…``) response models
#
# Field shapes mirror the account-level equivalents (e.g. ``ServiceConversation``
# ≈ ``Conversation``) with the addition of ``chat_service_sid`` for tenancy.
# ---------------------------------------------------------------------------


class ConversationsV1ServiceConversation(_Base):
    """Service-scoped Conversation (``CH…``) under a chat Service tenant."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    messaging_service_sid: str | None = None
    sid: str | None = None
    friendly_name: str | None = None
    unique_name: str | None = None
    attributes: str | None = None
    state: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    timers: dict[str, Any] | None = None
    url: str | None = None
    links: dict[str, Any] | None = None
    bindings: dict[str, Any] | None = None


class ConversationsV1ServiceConversationList(_Base):
    conversations: list[ConversationsV1ServiceConversation] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1ServiceConversationMessage(_Base):
    """Service-scoped Conversation Message (``IM…``)."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    conversation_sid: str | None = None
    sid: str | None = None
    index: int | None = None
    author: str | None = None
    body: str | None = None
    media: list[dict[str, Any]] | None = None
    attributes: str | None = None
    participant_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None
    delivery: dict[str, Any] | None = None
    links: dict[str, Any] | None = None
    content_sid: str | None = None


class ConversationsV1ServiceConversationMessageList(_Base):
    messages: list[ConversationsV1ServiceConversationMessage] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1ServiceConversationParticipant(_Base):
    """Service-scoped Participant (``MB…``)."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    conversation_sid: str | None = None
    sid: str | None = None
    identity: str | None = None
    attributes: str | None = None
    messaging_binding: dict[str, Any] | None = None
    role_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None
    last_read_message_index: int | None = None
    last_read_timestamp: str | None = None


class ConversationsV1ServiceConversationParticipantList(_Base):
    participants: list[ConversationsV1ServiceConversationParticipant] = Field(
        default_factory=list
    )
    meta: VoiceV1Meta | None = None


class ConversationsV1ServiceConversationMessageReceipt(_Base):
    """Service-scoped per-channel delivery receipt for one Message (``DY…``)."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    conversation_sid: str | None = None
    sid: str | None = None
    message_sid: str | None = None
    channel_message_sid: str | None = None
    participant_sid: str | None = None
    status: str | None = None
    error_code: int | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None


class ConversationsV1ServiceConversationMessageReceiptList(_Base):
    delivery_receipts: list[ConversationsV1ServiceConversationMessageReceipt] = Field(
        default_factory=list
    )
    meta: VoiceV1Meta | None = None


class ConversationsV1ServiceConversationScopedWebhook(_Base):
    """Service-scoped per-conversation event webhook binding (``WH…``)."""

    sid: str | None = None
    account_sid: str | None = None
    chat_service_sid: str | None = None
    conversation_sid: str | None = None
    target: str | None = None
    url: str | None = None
    configuration: dict[str, Any] | None = None
    date_created: str | None = None
    date_updated: str | None = None


class ConversationsV1ServiceConversationScopedWebhookList(_Base):
    webhooks: list[ConversationsV1ServiceConversationScopedWebhook] = Field(
        default_factory=list
    )
    meta: VoiceV1Meta | None = None


class ConversationsV1ServiceRole(_Base):
    """Service-scoped Role (``RL…``) — permission grant within a Service tenant."""

    sid: str | None = None
    account_sid: str | None = None
    chat_service_sid: str | None = None
    friendly_name: str | None = None
    type: str | None = None
    permissions: list[str] | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None


class ConversationsV1ServiceRoleList(_Base):
    roles: list[ConversationsV1ServiceRole] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1ServiceUser(_Base):
    """Service-scoped User identity (``US…``)."""

    sid: str | None = None
    account_sid: str | None = None
    chat_service_sid: str | None = None
    role_sid: str | None = None
    identity: str | None = None
    friendly_name: str | None = None
    attributes: str | None = None
    is_online: bool | None = None
    is_notifiable: bool | None = None
    date_created: str | None = None
    date_updated: str | None = None
    url: str | None = None
    links: dict[str, Any] | None = None


class ConversationsV1ServiceUserList(_Base):
    users: list[ConversationsV1ServiceUser] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1ServiceConversationWithParticipants(_Base):
    """Service-scoped Conversation created with its initial participants atomically."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    messaging_service_sid: str | None = None
    sid: str | None = None
    friendly_name: str | None = None
    unique_name: str | None = None
    attributes: str | None = None
    state: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    timers: dict[str, Any] | None = None
    links: dict[str, Any] | None = None
    bindings: dict[str, Any] | None = None
    url: str | None = None


class ConversationsV1ServiceParticipantConversation(_Base):
    """A flat row in the service-scoped participant-conversations index."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    participant_sid: str | None = None
    participant_user_sid: str | None = None
    participant_identity: str | None = None
    participant_messaging_binding: dict[str, Any] | None = None
    conversation_sid: str | None = None
    conversation_unique_name: str | None = None
    conversation_friendly_name: str | None = None
    conversation_attributes: str | None = None
    conversation_date_created: str | None = None
    conversation_date_updated: str | None = None
    conversation_created_by: str | None = None
    conversation_state: str | None = None
    conversation_timers: dict[str, Any] | None = None
    links: dict[str, Any] | None = None


class ConversationsV1ServiceParticipantConversationList(_Base):
    conversations: list[ConversationsV1ServiceParticipantConversation] = Field(
        default_factory=list
    )
    meta: VoiceV1Meta | None = None


class ConversationsV1ServiceUserConversation(_Base):
    """A User's per-Conversation membership state inside a Service tenant."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    conversation_sid: str | None = None
    unread_messages_count: int | None = None
    last_read_message_index: int | None = None
    participant_sid: str | None = None
    user_sid: str | None = None
    friendly_name: str | None = None
    conversation_state: str | None = None
    timers: dict[str, Any] | None = None
    attributes: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    created_by: str | None = None
    notification_level: str | None = None
    unique_name: str | None = None
    url: str | None = None
    links: dict[str, Any] | None = None


class ConversationsV1ServiceUserConversationList(_Base):
    conversations: list[ConversationsV1ServiceUserConversation] = Field(
        default_factory=list
    )
    meta: VoiceV1Meta | None = None


class ConversationsV1ServiceBinding(_Base):
    """Service-scoped push Binding (``BS…``) — read/delete only.

    Bindings are system-created when an endpoint registers for push.
    """

    sid: str | None = None
    account_sid: str | None = None
    chat_service_sid: str | None = None
    credential_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    endpoint: str | None = None
    identity: str | None = None
    binding_type: str | None = None
    message_types: list[str] | None = None
    url: str | None = None


class ConversationsV1ServiceBindingList(_Base):
    bindings: list[ConversationsV1ServiceBinding] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class ConversationsV1ServiceConfiguration(_Base):
    """Per-service Configuration singleton — default roles + reachability."""

    chat_service_sid: str | None = None
    default_conversation_creator_role_sid: str | None = None
    default_conversation_role_sid: str | None = None
    default_chat_service_role_sid: str | None = None
    url: str | None = None
    links: dict[str, Any] | None = None
    reachability_enabled: bool | None = None


class ConversationsV1ServiceNotification(_Base):
    """Per-service push Notification configuration singleton."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    new_message: dict[str, Any] | None = None
    added_to_conversation: dict[str, Any] | None = None
    removed_from_conversation: dict[str, Any] | None = None
    log_enabled: bool | None = None
    url: str | None = None


class ConversationsV1ServiceWebhookConfiguration(_Base):
    """Per-service Webhook configuration singleton (pre/post + filters)."""

    account_sid: str | None = None
    chat_service_sid: str | None = None
    pre_webhook_url: str | None = None
    post_webhook_url: str | None = None
    filters: list[str] | None = None
    method: str | None = None
    url: str | None = None


# ---------------------------------------------------------------------------
# Phase 4 — service-scoped request models
#
# Some shapes diverge from the account-level equivalents (e.g. the service-
# scoped Conversation update omits ``MessagingServiceSid``; the Participant
# update accepts only ``Attributes`` and ``RoleSid``). New models keep those
# differences explicit at the type level rather than relying on caller
# discipline.
# ---------------------------------------------------------------------------


class CreateConversationsV1ServiceConversationRequest(_Base):
    """Body for ``POST /v1/Services/{ChatServiceSid}/Conversations``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    unique_name: str | None = Field(default=None, alias="UniqueName")
    messaging_service_sid: str | None = Field(default=None, alias="MessagingServiceSid")
    attributes: str | None = Field(default=None, alias="Attributes")
    state: str | None = Field(default=None, alias="State")
    timers_inactive: str | None = Field(default=None, alias="Timers.Inactive")
    timers_closed: str | None = Field(default=None, alias="Timers.Closed")


class UpdateConversationsV1ServiceConversationRequest(_Base):
    """Body for ``POST /v1/Services/{ChatServiceSid}/Conversations/{ConversationSid}``.

    No ``MessagingServiceSid`` — it's pinned at create time for service-scoped
    Conversations and cannot be re-assigned through this endpoint.
    """

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    unique_name: str | None = Field(default=None, alias="UniqueName")
    attributes: str | None = Field(default=None, alias="Attributes")
    state: str | None = Field(default=None, alias="State")
    timers_inactive: str | None = Field(default=None, alias="Timers.Inactive")
    timers_closed: str | None = Field(default=None, alias="Timers.Closed")


class CreateConversationsV1ServiceConversationMessageRequest(_Base):
    """Body for the service-scoped Messages create endpoint."""

    author: str | None = Field(default=None, alias="Author")
    body: str | None = Field(default=None, alias="Body")
    attributes: str | None = Field(default=None, alias="Attributes")
    content_sid: str | None = Field(default=None, alias="ContentSid")


class UpdateConversationsV1ServiceConversationMessageRequest(_Base):
    """Body for the service-scoped Messages update endpoint."""

    author: str | None = Field(default=None, alias="Author")
    body: str | None = Field(default=None, alias="Body")
    attributes: str | None = Field(default=None, alias="Attributes")


class CreateConversationsV1ServiceConversationParticipantRequest(_Base):
    """Body for the service-scoped Participants create endpoint."""

    identity: str | None = Field(default=None, alias="Identity")
    attributes: str | None = Field(default=None, alias="Attributes")
    role_sid: str | None = Field(default=None, alias="RoleSid")
    messaging_binding_address: str | None = Field(
        default=None, alias="MessagingBinding.Address"
    )
    messaging_binding_proxy_address: str | None = Field(
        default=None, alias="MessagingBinding.ProxyAddress"
    )
    messaging_binding_projected_address: str | None = Field(
        default=None, alias="MessagingBinding.ProjectedAddress"
    )


class UpdateConversationsV1ServiceConversationParticipantRequest(_Base):
    """Body for the service-scoped Participants update endpoint.

    Service-scoped variant accepts only ``Attributes`` and ``RoleSid``.
    """

    attributes: str | None = Field(default=None, alias="Attributes")
    role_sid: str | None = Field(default=None, alias="RoleSid")


class CreateConversationsV1ServiceConversationScopedWebhookRequest(_Base):
    """Body for the service-scoped Scoped-Webhook create endpoint."""

    target: str = Field(alias="Target")
    configuration_url: str | None = Field(default=None, alias="Configuration.Url")
    configuration_method: str | None = Field(
        default=None, alias="Configuration.Method"
    )
    configuration_flow_sid: str | None = Field(
        default=None, alias="Configuration.FlowSid"
    )


class UpdateConversationsV1ServiceConversationScopedWebhookRequest(_Base):
    """Body for the service-scoped Scoped-Webhook update endpoint."""

    configuration_url: str | None = Field(default=None, alias="Configuration.Url")
    configuration_method: str | None = Field(
        default=None, alias="Configuration.Method"
    )
    configuration_flow_sid: str | None = Field(
        default=None, alias="Configuration.FlowSid"
    )


class CreateConversationsV1ServiceRoleRequest(_Base):
    """Body for ``POST /v1/Services/{ChatServiceSid}/Roles``."""

    friendly_name: str = Field(alias="FriendlyName")
    type: str = Field(alias="Type")
    permission: list[str] = Field(alias="Permission")


class UpdateConversationsV1ServiceRoleRequest(_Base):
    """Body for ``POST /v1/Services/{ChatServiceSid}/Roles/{Sid}``."""

    permission: list[str] = Field(alias="Permission")


class CreateConversationsV1ServiceUserRequest(_Base):
    """Body for ``POST /v1/Services/{ChatServiceSid}/Users``."""

    identity: str = Field(alias="Identity")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    attributes: str | None = Field(default=None, alias="Attributes")
    role_sid: str | None = Field(default=None, alias="RoleSid")


class UpdateConversationsV1ServiceUserRequest(_Base):
    """Body for ``POST /v1/Services/{ChatServiceSid}/Users/{Sid}``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    attributes: str | None = Field(default=None, alias="Attributes")
    role_sid: str | None = Field(default=None, alias="RoleSid")


class CreateConversationsV1ServiceConversationWithParticipantsRequest(_Base):
    """Body for the service-scoped ConversationWithParticipants endpoint.

    ``Participant`` is repeated; each entry is a JSON string. The transport
    encodes the list as ``Participant=…&Participant=…``.
    """

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    unique_name: str | None = Field(default=None, alias="UniqueName")
    messaging_service_sid: str | None = Field(default=None, alias="MessagingServiceSid")
    attributes: str | None = Field(default=None, alias="Attributes")
    state: str | None = Field(default=None, alias="State")
    timers_inactive: str | None = Field(default=None, alias="Timers.Inactive")
    timers_closed: str | None = Field(default=None, alias="Timers.Closed")
    participant: list[str] | None = Field(default=None, alias="Participant")


class UpdateConversationsV1ServiceConfigurationRequest(_Base):
    """Body for ``POST /v1/Services/{ChatServiceSid}/Configuration``."""

    default_chat_service_role_sid: str | None = Field(
        default=None, alias="DefaultChatServiceRoleSid"
    )
    default_conversation_creator_role_sid: str | None = Field(
        default=None, alias="DefaultConversationCreatorRoleSid"
    )
    default_conversation_role_sid: str | None = Field(
        default=None, alias="DefaultConversationRoleSid"
    )
    reachability_enabled: bool | None = Field(default=None, alias="ReachabilityEnabled")


class UpdateConversationsV1ServiceNotificationRequest(_Base):
    """Body for ``POST /v1/Services/{ChatServiceSid}/Configuration/Notifications``.

    Push notification settings keyed by event name; fields whose wire names
    contain dots (e.g. ``NewMessage.Enabled``) keep the dotted form as the
    Pydantic ``alias=``.
    """

    log_enabled: bool | None = Field(default=None, alias="LogEnabled")
    new_message_enabled: bool | None = Field(
        default=None, alias="NewMessage.Enabled"
    )
    new_message_template: str | None = Field(
        default=None, alias="NewMessage.Template"
    )
    new_message_sound: str | None = Field(default=None, alias="NewMessage.Sound")
    new_message_badge_count_enabled: bool | None = Field(
        default=None, alias="NewMessage.BadgeCountEnabled"
    )
    new_message_with_media_enabled: bool | None = Field(
        default=None, alias="NewMessage.WithMedia.Enabled"
    )
    new_message_with_media_template: str | None = Field(
        default=None, alias="NewMessage.WithMedia.Template"
    )
    added_to_conversation_enabled: bool | None = Field(
        default=None, alias="AddedToConversation.Enabled"
    )
    added_to_conversation_template: str | None = Field(
        default=None, alias="AddedToConversation.Template"
    )
    added_to_conversation_sound: str | None = Field(
        default=None, alias="AddedToConversation.Sound"
    )
    removed_from_conversation_enabled: bool | None = Field(
        default=None, alias="RemovedFromConversation.Enabled"
    )
    removed_from_conversation_template: str | None = Field(
        default=None, alias="RemovedFromConversation.Template"
    )
    removed_from_conversation_sound: str | None = Field(
        default=None, alias="RemovedFromConversation.Sound"
    )


class UpdateConversationsV1ServiceWebhookConfigurationRequest(_Base):
    """Body for ``POST /v1/Services/{ChatServiceSid}/Configuration/Webhooks``.

    ``Filters`` is a repeated form param — the transport encodes the list
    as ``Filters=…&Filters=…``.
    """

    pre_webhook_url: str | None = Field(default=None, alias="PreWebhookUrl")
    post_webhook_url: str | None = Field(default=None, alias="PostWebhookUrl")
    method: str | None = Field(default=None, alias="Method")
    filters: list[str] | None = Field(default=None, alias="Filters")
