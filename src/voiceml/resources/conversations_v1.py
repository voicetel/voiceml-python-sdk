"""``/v1/*`` Conversations REST surface — Twilio conversations.twilio.com/v1.

Top-level holder is :class:`ConversationsV1Resource` (sync) /
:class:`ConversationsV1AsyncResource` (async), wired under
``client.conversations_v1.*``.

Layout::

    client.conversations_v1.conversations.create / list / fetch / update / delete
    client.conversations_v1.conversations(conv_sid).messages.create / list / fetch / update / delete
    client.conversations_v1.conversations(conv_sid).messages(msg_sid).receipts.list / fetch
    client.conversations_v1.conversations(conv_sid).participants.create / list / fetch / update / delete
    client.conversations_v1.conversations(conv_sid).webhooks.create / list / fetch / update / delete

    client.conversations_v1.roles.create / list / fetch / update / delete
    client.conversations_v1.users.create / list / fetch / update / delete
    client.conversations_v1.users(user_sid).conversations.list / fetch / update / delete
    client.conversations_v1.credentials.create / list / fetch / update / delete

    client.conversations_v1.configuration.fetch / update
    client.conversations_v1.configuration.webhooks.fetch / update
    client.conversations_v1.configuration.addresses.create / list / fetch / update / delete

    client.conversations_v1.participant_conversations.list
    client.conversations_v1.conversation_with_participants.create
    client.conversations_v1.services.create / list / fetch / delete

Where the parent SID gates the sub-resource (Messages / Participants /
Webhooks / Receipts / per-user Conversations), a factory method returns a
sid-bound sub-resource instance — mirroring the pattern used by ``client.sip``.

All paths sit at ``/v1/`` (no ``/2010-04-01/Accounts/{Sid}/`` prefix); the
account is resolved from HTTP Basic auth.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..models import (
    ConversationsV1ConfigAddress,
    ConversationsV1ConfigAddressList,
    ConversationsV1Configuration,
    ConversationsV1ConfigurationWebhook,
    ConversationsV1Conversation,
    ConversationsV1ConversationList,
    ConversationsV1ConversationMessage,
    ConversationsV1ConversationMessageList,
    ConversationsV1ConversationMessageReceipt,
    ConversationsV1ConversationMessageReceiptList,
    ConversationsV1ConversationParticipant,
    ConversationsV1ConversationParticipantList,
    ConversationsV1ConversationScopedWebhook,
    ConversationsV1ConversationScopedWebhookList,
    ConversationsV1ConversationWithParticipants,
    ConversationsV1Credential,
    ConversationsV1CredentialList,
    ConversationsV1ParticipantConversationList,
    ConversationsV1Role,
    ConversationsV1RoleList,
    ConversationsV1Service,
    ConversationsV1ServiceBinding,
    ConversationsV1ServiceBindingList,
    ConversationsV1ServiceConfiguration,
    ConversationsV1ServiceConversation,
    ConversationsV1ServiceConversationList,
    ConversationsV1ServiceConversationMessage,
    ConversationsV1ServiceConversationMessageList,
    ConversationsV1ServiceConversationMessageReceipt,
    ConversationsV1ServiceConversationMessageReceiptList,
    ConversationsV1ServiceConversationParticipant,
    ConversationsV1ServiceConversationParticipantList,
    ConversationsV1ServiceConversationScopedWebhook,
    ConversationsV1ServiceConversationScopedWebhookList,
    ConversationsV1ServiceConversationWithParticipants,
    ConversationsV1ServiceList,
    ConversationsV1ServiceNotification,
    ConversationsV1ServiceParticipantConversationList,
    ConversationsV1ServiceRole,
    ConversationsV1ServiceRoleList,
    ConversationsV1ServiceUser,
    ConversationsV1ServiceUserConversationList,
    ConversationsV1ServiceUserList,
    ConversationsV1ServiceWebhookConfiguration,
    ConversationsV1User,
    ConversationsV1UserConversation,
    ConversationsV1UserConversationList,
    ConversationsV1UserList,
    CreateConversationsV1ConfigAddressRequest,
    CreateConversationsV1ConversationMessageRequest,
    CreateConversationsV1ConversationParticipantRequest,
    CreateConversationsV1ConversationRequest,
    CreateConversationsV1ConversationScopedWebhookRequest,
    CreateConversationsV1ConversationWithParticipantsRequest,
    CreateConversationsV1CredentialRequest,
    CreateConversationsV1RoleRequest,
    CreateConversationsV1ServiceConversationMessageRequest,
    CreateConversationsV1ServiceConversationParticipantRequest,
    CreateConversationsV1ServiceConversationRequest,
    CreateConversationsV1ServiceConversationScopedWebhookRequest,
    CreateConversationsV1ServiceConversationWithParticipantsRequest,
    CreateConversationsV1ServiceRequest,
    CreateConversationsV1ServiceRoleRequest,
    CreateConversationsV1ServiceUserRequest,
    CreateConversationsV1UserRequest,
    UpdateConversationsV1ConfigAddressRequest,
    UpdateConversationsV1ConfigurationRequest,
    UpdateConversationsV1ConfigurationWebhookRequest,
    UpdateConversationsV1ConversationMessageRequest,
    UpdateConversationsV1ConversationParticipantRequest,
    UpdateConversationsV1ConversationRequest,
    UpdateConversationsV1ConversationScopedWebhookRequest,
    UpdateConversationsV1CredentialRequest,
    UpdateConversationsV1RoleRequest,
    UpdateConversationsV1ServiceConfigurationRequest,
    UpdateConversationsV1ServiceConversationMessageRequest,
    UpdateConversationsV1ServiceConversationParticipantRequest,
    UpdateConversationsV1ServiceConversationRequest,
    UpdateConversationsV1ServiceConversationScopedWebhookRequest,
    UpdateConversationsV1ServiceNotificationRequest,
    UpdateConversationsV1ServiceRoleRequest,
    UpdateConversationsV1ServiceUserRequest,
    UpdateConversationsV1ServiceWebhookConfigurationRequest,
    UpdateConversationsV1UserConversationRequest,
    UpdateConversationsV1UserRequest,
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _page_params(*, page_size: int | None) -> dict[str, object]:
    return {"PageSize": page_size}


def _conversation_create_form(
    *,
    friendly_name: str | None,
    unique_name: str | None,
    messaging_service_sid: str | None,
    attributes: str | None,
    state: str | None,
    timers_inactive: str | None,
    timers_closed: str | None,
    bindings_email_address: str | None,
    bindings_email_name: str | None,
) -> dict[str, object]:
    return CreateConversationsV1ConversationRequest(
        friendly_name=friendly_name,
        unique_name=unique_name,
        messaging_service_sid=messaging_service_sid,
        attributes=attributes,
        state=state,
        timers_inactive=timers_inactive,
        timers_closed=timers_closed,
        bindings_email_address=bindings_email_address,
        bindings_email_name=bindings_email_name,
    ).to_form()


def _conversation_update_form(
    *,
    friendly_name: str | None,
    unique_name: str | None,
    messaging_service_sid: str | None,
    attributes: str | None,
    state: str | None,
    timers_inactive: str | None,
    timers_closed: str | None,
) -> dict[str, object]:
    return UpdateConversationsV1ConversationRequest(
        friendly_name=friendly_name,
        unique_name=unique_name,
        messaging_service_sid=messaging_service_sid,
        attributes=attributes,
        state=state,
        timers_inactive=timers_inactive,
        timers_closed=timers_closed,
    ).to_form()


# ===========================================================================
# Sync sub-resources keyed by parent SIDs
# ===========================================================================


class _ConversationsV1MessageReceiptsResource:
    """Read-only ``/v1/Conversations/{ConvSid}/Messages/{MsgSid}/Receipts`` (sync)."""

    def __init__(self, transport: object, conversation_sid: str, message_sid: str) -> None:
        self._t = transport
        self._conv = conversation_sid
        self._msg = message_sid

    def _root(self, *tail: str) -> str:
        parts = [
            "v1", "Conversations", self._conv, "Messages", self._msg, "Receipts", *tail
        ]
        return "/" + "/".join(parts)

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConversationMessageReceiptList:
        return ConversationsV1ConversationMessageReceiptList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> ConversationsV1ConversationMessageReceipt:
        return ConversationsV1ConversationMessageReceipt.model_validate(
            self._t.request("GET", self._root(sid))
        )


class _ConversationsV1MessagesResource:
    """``/v1/Conversations/{ConvSid}/Messages`` (sync)."""

    def __init__(self, transport: object, conversation_sid: str) -> None:
        self._t = transport
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Conversations", self._conv, "Messages", *tail]
        return "/" + "/".join(parts)

    def create(
        self,
        *,
        author: str | None = None,
        body: str | None = None,
        attributes: str | None = None,
        content_sid: str | None = None,
    ) -> ConversationsV1ConversationMessage:
        body_form = CreateConversationsV1ConversationMessageRequest(
            Author=author,
            Body=body,
            Attributes=attributes,
            ContentSid=content_sid,
        ).to_form()
        return ConversationsV1ConversationMessage.model_validate(
            self._t.request("POST", self._root(), data=body_form)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConversationMessageList:
        return ConversationsV1ConversationMessageList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, message_sid: str) -> ConversationsV1ConversationMessage:
        return ConversationsV1ConversationMessage.model_validate(
            self._t.request("GET", self._root(message_sid))
        )

    def update(
        self,
        message_sid: str,
        *,
        author: str | None = None,
        body: str | None = None,
        attributes: str | None = None,
    ) -> ConversationsV1ConversationMessage:
        body_form = UpdateConversationsV1ConversationMessageRequest(
            Author=author, Body=body, Attributes=attributes
        ).to_form()
        return ConversationsV1ConversationMessage.model_validate(
            self._t.request("POST", self._root(message_sid), data=body_form)
        )

    def delete(self, message_sid: str) -> None:
        self._t.request("DELETE", self._root(message_sid))

    def receipts(self, message_sid: str) -> _ConversationsV1MessageReceiptsResource:
        return _ConversationsV1MessageReceiptsResource(self._t, self._conv, message_sid)


class _ConversationsV1ParticipantsResource:
    """``/v1/Conversations/{ConvSid}/Participants`` (sync)."""

    def __init__(self, transport: object, conversation_sid: str) -> None:
        self._t = transport
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Conversations", self._conv, "Participants", *tail]
        return "/" + "/".join(parts)

    def create(
        self,
        *,
        identity: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
        messaging_binding_address: str | None = None,
        messaging_binding_proxy_address: str | None = None,
        messaging_binding_projected_address: str | None = None,
    ) -> ConversationsV1ConversationParticipant:
        body = CreateConversationsV1ConversationParticipantRequest(
            identity=identity,
            attributes=attributes,
            role_sid=role_sid,
            messaging_binding_address=messaging_binding_address,
            messaging_binding_proxy_address=messaging_binding_proxy_address,
            messaging_binding_projected_address=messaging_binding_projected_address,
        ).to_form()
        return ConversationsV1ConversationParticipant.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConversationParticipantList:
        return ConversationsV1ConversationParticipantList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, participant_sid: str) -> ConversationsV1ConversationParticipant:
        return ConversationsV1ConversationParticipant.model_validate(
            self._t.request("GET", self._root(participant_sid))
        )

    def update(
        self,
        participant_sid: str,
        *,
        identity: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
        last_read_message_index: int | None = None,
        last_read_timestamp: str | None = None,
    ) -> ConversationsV1ConversationParticipant:
        body = UpdateConversationsV1ConversationParticipantRequest(
            Identity=identity,
            Attributes=attributes,
            RoleSid=role_sid,
            LastReadMessageIndex=last_read_message_index,
            LastReadTimestamp=last_read_timestamp,
        ).to_form()
        return ConversationsV1ConversationParticipant.model_validate(
            self._t.request("POST", self._root(participant_sid), data=body)
        )

    def delete(self, participant_sid: str) -> None:
        self._t.request("DELETE", self._root(participant_sid))


class _ConversationsV1WebhooksResource:
    """``/v1/Conversations/{ConvSid}/Webhooks`` (sync)."""

    def __init__(self, transport: object, conversation_sid: str) -> None:
        self._t = transport
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Conversations", self._conv, "Webhooks", *tail]
        return "/" + "/".join(parts)

    def create(
        self,
        *,
        target: str,
        configuration_url: str | None = None,
        configuration_method: str | None = None,
        configuration_flow_sid: str | None = None,
        configuration_replay_after: int | None = None,
    ) -> ConversationsV1ConversationScopedWebhook:
        body = CreateConversationsV1ConversationScopedWebhookRequest(
            target=target,
            configuration_url=configuration_url,
            configuration_method=configuration_method,
            configuration_flow_sid=configuration_flow_sid,
            configuration_replay_after=configuration_replay_after,
        ).to_form()
        return ConversationsV1ConversationScopedWebhook.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConversationScopedWebhookList:
        return ConversationsV1ConversationScopedWebhookList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, webhook_sid: str) -> ConversationsV1ConversationScopedWebhook:
        return ConversationsV1ConversationScopedWebhook.model_validate(
            self._t.request("GET", self._root(webhook_sid))
        )

    def update(
        self,
        webhook_sid: str,
        *,
        configuration_url: str | None = None,
        configuration_method: str | None = None,
        configuration_flow_sid: str | None = None,
    ) -> ConversationsV1ConversationScopedWebhook:
        body = UpdateConversationsV1ConversationScopedWebhookRequest(
            configuration_url=configuration_url,
            configuration_method=configuration_method,
            configuration_flow_sid=configuration_flow_sid,
        ).to_form()
        return ConversationsV1ConversationScopedWebhook.model_validate(
            self._t.request("POST", self._root(webhook_sid), data=body)
        )

    def delete(self, webhook_sid: str) -> None:
        self._t.request("DELETE", self._root(webhook_sid))


class _ConversationContext:
    """Returned by ``client.conversations_v1.conversations(sid)`` — sub-resource factory."""

    def __init__(self, transport: object, conversation_sid: str) -> None:
        self.messages = _ConversationsV1MessagesResource(transport, conversation_sid)
        self.participants = _ConversationsV1ParticipantsResource(transport, conversation_sid)
        self.webhooks = _ConversationsV1WebhooksResource(transport, conversation_sid)


class _ConversationsCallable:
    """Top-level ``client.conversations_v1.conversations`` — callable + namespace.

    Calling it (e.g. ``conversations("CH…")``) returns a :class:`_ConversationContext`
    bound to a parent conversation sid. Accessing attributes (``conversations.create``,
    ``conversations.list``, …) drives the un-bound CRUD.
    """

    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, conversation_sid: str) -> _ConversationContext:
        return _ConversationContext(self._t, conversation_sid)

    def create(
        self,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        messaging_service_sid: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
        bindings_email_address: str | None = None,
        bindings_email_name: str | None = None,
    ) -> ConversationsV1Conversation:
        return ConversationsV1Conversation.model_validate(
            self._t.request(
                "POST",
                "/v1/Conversations",
                data=_conversation_create_form(
                    friendly_name=friendly_name,
                    unique_name=unique_name,
                    messaging_service_sid=messaging_service_sid,
                    attributes=attributes,
                    state=state,
                    timers_inactive=timers_inactive,
                    timers_closed=timers_closed,
                    bindings_email_address=bindings_email_address,
                    bindings_email_name=bindings_email_name,
                ),
            )
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConversationList:
        return ConversationsV1ConversationList.model_validate(
            self._t.request(
                "GET",
                "/v1/Conversations",
                params=_page_params(page_size=page_size),
            )
        )

    def fetch(self, conversation_sid: str) -> ConversationsV1Conversation:
        return ConversationsV1Conversation.model_validate(
            self._t.request("GET", f"/v1/Conversations/{conversation_sid}")
        )

    def update(
        self,
        conversation_sid: str,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        messaging_service_sid: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
    ) -> ConversationsV1Conversation:
        return ConversationsV1Conversation.model_validate(
            self._t.request(
                "POST",
                f"/v1/Conversations/{conversation_sid}",
                data=_conversation_update_form(
                    friendly_name=friendly_name,
                    unique_name=unique_name,
                    messaging_service_sid=messaging_service_sid,
                    attributes=attributes,
                    state=state,
                    timers_inactive=timers_inactive,
                    timers_closed=timers_closed,
                ),
            )
        )

    def delete(self, conversation_sid: str) -> None:
        self._t.request("DELETE", f"/v1/Conversations/{conversation_sid}")


class _ConversationsV1RolesResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def create(
        self, *, friendly_name: str, type: str, permission: Sequence[str]
    ) -> ConversationsV1Role:
        body = CreateConversationsV1RoleRequest(
            FriendlyName=friendly_name,
            Type=type,
            Permission=list(permission),
        ).to_form()
        return ConversationsV1Role.model_validate(
            self._t.request("POST", "/v1/Roles", data=body)
        )

    def list(self, *, page_size: int | None = None) -> ConversationsV1RoleList:
        return ConversationsV1RoleList.model_validate(
            self._t.request(
                "GET", "/v1/Roles", params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> ConversationsV1Role:
        return ConversationsV1Role.model_validate(
            self._t.request("GET", f"/v1/Roles/{sid}")
        )

    def update(
        self, sid: str, *, permission: Sequence[str]
    ) -> ConversationsV1Role:
        body = UpdateConversationsV1RoleRequest(
            Permission=list(permission)
        ).to_form()
        return ConversationsV1Role.model_validate(
            self._t.request("POST", f"/v1/Roles/{sid}", data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", f"/v1/Roles/{sid}")


class _ConversationsV1UserConversationsResource:
    """Per-user ``/v1/Users/{Sid}/Conversations`` (sync)."""

    def __init__(self, transport: object, user_sid: str) -> None:
        self._t = transport
        self._user = user_sid

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Users", self._user, "Conversations", *tail]
        return "/" + "/".join(parts)

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1UserConversationList:
        return ConversationsV1UserConversationList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, conversation_sid: str) -> ConversationsV1UserConversation:
        return ConversationsV1UserConversation.model_validate(
            self._t.request("GET", self._root(conversation_sid))
        )

    def update(
        self,
        conversation_sid: str,
        *,
        notification_level: str | None = None,
        last_read_message_index: int | None = None,
        last_read_timestamp: str | None = None,
    ) -> ConversationsV1UserConversation:
        body = UpdateConversationsV1UserConversationRequest(
            NotificationLevel=notification_level,
            LastReadMessageIndex=last_read_message_index,
            LastReadTimestamp=last_read_timestamp,
        ).to_form()
        return ConversationsV1UserConversation.model_validate(
            self._t.request("POST", self._root(conversation_sid), data=body)
        )

    def delete(self, conversation_sid: str) -> None:
        self._t.request("DELETE", self._root(conversation_sid))


class _UserContext:
    """Returned by ``client.conversations_v1.users(sid)`` — sub-resource factory."""

    def __init__(self, transport: object, user_sid: str) -> None:
        self.conversations = _ConversationsV1UserConversationsResource(transport, user_sid)


class _ConversationsV1UsersCallable:
    """Top-level ``client.conversations_v1.users`` — callable + namespace."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, user_sid: str) -> _UserContext:
        return _UserContext(self._t, user_sid)

    def create(
        self,
        *,
        identity: str,
        friendly_name: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
    ) -> ConversationsV1User:
        body = CreateConversationsV1UserRequest(
            Identity=identity,
            FriendlyName=friendly_name,
            Attributes=attributes,
            RoleSid=role_sid,
        ).to_form()
        return ConversationsV1User.model_validate(
            self._t.request("POST", "/v1/Users", data=body)
        )

    def list(self, *, page_size: int | None = None) -> ConversationsV1UserList:
        return ConversationsV1UserList.model_validate(
            self._t.request(
                "GET", "/v1/Users", params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> ConversationsV1User:
        return ConversationsV1User.model_validate(
            self._t.request("GET", f"/v1/Users/{sid}")
        )

    def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
    ) -> ConversationsV1User:
        body = UpdateConversationsV1UserRequest(
            FriendlyName=friendly_name,
            Attributes=attributes,
            RoleSid=role_sid,
        ).to_form()
        return ConversationsV1User.model_validate(
            self._t.request("POST", f"/v1/Users/{sid}", data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", f"/v1/Users/{sid}")


class _ConversationsV1CredentialsResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def create(
        self,
        *,
        type: str,
        friendly_name: str | None = None,
        certificate: str | None = None,
        private_key: str | None = None,
        sandbox: bool | None = None,
        api_key: str | None = None,
        secret: str | None = None,
    ) -> ConversationsV1Credential:
        body = CreateConversationsV1CredentialRequest(
            Type=type,
            FriendlyName=friendly_name,
            Certificate=certificate,
            PrivateKey=private_key,
            Sandbox=sandbox,
            ApiKey=api_key,
            Secret=secret,
        ).to_form()
        return ConversationsV1Credential.model_validate(
            self._t.request("POST", "/v1/Credentials", data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1CredentialList:
        return ConversationsV1CredentialList.model_validate(
            self._t.request(
                "GET", "/v1/Credentials", params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> ConversationsV1Credential:
        return ConversationsV1Credential.model_validate(
            self._t.request("GET", f"/v1/Credentials/{sid}")
        )

    def update(
        self,
        sid: str,
        *,
        type: str | None = None,
        friendly_name: str | None = None,
        certificate: str | None = None,
        private_key: str | None = None,
        sandbox: bool | None = None,
        api_key: str | None = None,
        secret: str | None = None,
    ) -> ConversationsV1Credential:
        body = UpdateConversationsV1CredentialRequest(
            Type=type,
            FriendlyName=friendly_name,
            Certificate=certificate,
            PrivateKey=private_key,
            Sandbox=sandbox,
            ApiKey=api_key,
            Secret=secret,
        ).to_form()
        return ConversationsV1Credential.model_validate(
            self._t.request("POST", f"/v1/Credentials/{sid}", data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", f"/v1/Credentials/{sid}")


class _ConversationsV1ConfigWebhooksResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def fetch(self) -> ConversationsV1ConfigurationWebhook:
        return ConversationsV1ConfigurationWebhook.model_validate(
            self._t.request("GET", "/v1/Configuration/Webhooks")
        )

    def update(
        self,
        *,
        method: str | None = None,
        filters: Sequence[str] | None = None,
        pre_webhook_url: str | None = None,
        post_webhook_url: str | None = None,
        target: str | None = None,
    ) -> ConversationsV1ConfigurationWebhook:
        body = UpdateConversationsV1ConfigurationWebhookRequest(
            Method=method,
            Filters=list(filters) if filters is not None else None,
            PreWebhookUrl=pre_webhook_url,
            PostWebhookUrl=post_webhook_url,
            Target=target,
        ).to_form()
        return ConversationsV1ConfigurationWebhook.model_validate(
            self._t.request("POST", "/v1/Configuration/Webhooks", data=body)
        )


class _ConversationsV1ConfigAddressesResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def create(
        self,
        *,
        type: str,
        address: str,
        friendly_name: str | None = None,
        auto_creation_enabled: bool | None = None,
        auto_creation_type: str | None = None,
        auto_creation_webhook_url: str | None = None,
        address_country: str | None = None,
    ) -> ConversationsV1ConfigAddress:
        body = CreateConversationsV1ConfigAddressRequest(
            type=type,
            address=address,
            friendly_name=friendly_name,
            auto_creation_enabled=auto_creation_enabled,
            auto_creation_type=auto_creation_type,
            auto_creation_webhook_url=auto_creation_webhook_url,
            address_country=address_country,
        ).to_form()
        return ConversationsV1ConfigAddress.model_validate(
            self._t.request("POST", "/v1/Configuration/Addresses", data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConfigAddressList:
        return ConversationsV1ConfigAddressList.model_validate(
            self._t.request(
                "GET",
                "/v1/Configuration/Addresses",
                params=_page_params(page_size=page_size),
            )
        )

    def fetch(self, sid: str) -> ConversationsV1ConfigAddress:
        return ConversationsV1ConfigAddress.model_validate(
            self._t.request("GET", f"/v1/Configuration/Addresses/{sid}")
        )

    def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        auto_creation_enabled: bool | None = None,
        auto_creation_type: str | None = None,
        auto_creation_webhook_url: str | None = None,
    ) -> ConversationsV1ConfigAddress:
        body = UpdateConversationsV1ConfigAddressRequest(
            friendly_name=friendly_name,
            auto_creation_enabled=auto_creation_enabled,
            auto_creation_type=auto_creation_type,
            auto_creation_webhook_url=auto_creation_webhook_url,
        ).to_form()
        return ConversationsV1ConfigAddress.model_validate(
            self._t.request(
                "POST", f"/v1/Configuration/Addresses/{sid}", data=body
            )
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", f"/v1/Configuration/Addresses/{sid}")


class _ConversationsV1ConfigurationResource:
    """``/v1/Configuration`` singleton + nested ``.webhooks`` and ``.addresses``."""

    def __init__(self, transport: object) -> None:
        self._t = transport
        self.webhooks = _ConversationsV1ConfigWebhooksResource(transport)
        self.addresses = _ConversationsV1ConfigAddressesResource(transport)

    def fetch(self) -> ConversationsV1Configuration:
        return ConversationsV1Configuration.model_validate(
            self._t.request("GET", "/v1/Configuration")
        )

    def update(
        self,
        *,
        default_chat_service_sid: str | None = None,
        default_messaging_service_sid: str | None = None,
        default_inactive_timer: str | None = None,
        default_closed_timer: str | None = None,
    ) -> ConversationsV1Configuration:
        body = UpdateConversationsV1ConfigurationRequest(
            DefaultChatServiceSid=default_chat_service_sid,
            DefaultMessagingServiceSid=default_messaging_service_sid,
            DefaultInactiveTimer=default_inactive_timer,
            DefaultClosedTimer=default_closed_timer,
        ).to_form()
        return ConversationsV1Configuration.model_validate(
            self._t.request("POST", "/v1/Configuration", data=body)
        )


class _ConversationsV1ParticipantConversationsResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def list(
        self,
        *,
        identity: str | None = None,
        address: str | None = None,
        page_size: int | None = None,
    ) -> ConversationsV1ParticipantConversationList:
        return ConversationsV1ParticipantConversationList.model_validate(
            self._t.request(
                "GET",
                "/v1/ParticipantConversations",
                params={
                    "Identity": identity,
                    "Address": address,
                    "PageSize": page_size,
                },
            )
        )


class _ConversationsV1ConversationWithParticipantsResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def create(
        self,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        messaging_service_sid: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
        participant: Sequence[str] | None = None,
    ) -> ConversationsV1ConversationWithParticipants:
        body = CreateConversationsV1ConversationWithParticipantsRequest(
            friendly_name=friendly_name,
            unique_name=unique_name,
            messaging_service_sid=messaging_service_sid,
            attributes=attributes,
            state=state,
            timers_inactive=timers_inactive,
            timers_closed=timers_closed,
            participant=list(participant) if participant is not None else None,
        ).to_form()
        return ConversationsV1ConversationWithParticipants.model_validate(
            self._t.request(
                "POST", "/v1/ConversationWithParticipants", data=body
            )
        )


class _ConversationsV1ServicesResource:
    """``/v1/Services`` (sync) — top-level CRUD on chat Services.

    Calling the resource (``services("IS…")``) returns a
    :class:`_ConversationsV1ServiceScopeResource` bound to the given
    ChatServiceSid, which exposes the Phase 4 service-scoped sub-resources.
    """

    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, chat_service_sid: str) -> _ConversationsV1ServiceScopeResource:
        return _ConversationsV1ServiceScopeResource(self._t, chat_service_sid)

    def create(self, *, friendly_name: str) -> ConversationsV1Service:
        body = CreateConversationsV1ServiceRequest(
            FriendlyName=friendly_name
        ).to_form()
        return ConversationsV1Service.model_validate(
            self._t.request("POST", "/v1/Services", data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceList:
        return ConversationsV1ServiceList.model_validate(
            self._t.request(
                "GET", "/v1/Services", params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, chat_service_sid: str) -> ConversationsV1Service:
        return ConversationsV1Service.model_validate(
            self._t.request("GET", f"/v1/Services/{chat_service_sid}")
        )

    def delete(self, chat_service_sid: str) -> None:
        self._t.request("DELETE", f"/v1/Services/{chat_service_sid}")


class ConversationsV1Resource:
    """Holder for ``client.conversations_v1.*`` sub-resources (sync)."""

    def __init__(self, transport: object) -> None:
        self.conversations = _ConversationsCallable(transport)
        self.roles = _ConversationsV1RolesResource(transport)
        self.users = _ConversationsV1UsersCallable(transport)
        self.credentials = _ConversationsV1CredentialsResource(transport)
        self.configuration = _ConversationsV1ConfigurationResource(transport)
        self.participant_conversations = _ConversationsV1ParticipantConversationsResource(
            transport
        )
        self.conversation_with_participants = (
            _ConversationsV1ConversationWithParticipantsResource(transport)
        )
        self.services = _ConversationsV1ServicesResource(transport)


# ===========================================================================
# Async counterparts — same surface; methods are awaitable.
# ===========================================================================


class _AsyncConversationsV1MessageReceiptsResource:
    def __init__(self, transport: object, conversation_sid: str, message_sid: str) -> None:
        self._t = transport
        self._conv = conversation_sid
        self._msg = message_sid

    def _root(self, *tail: str) -> str:
        parts = [
            "v1", "Conversations", self._conv, "Messages", self._msg, "Receipts", *tail
        ]
        return "/" + "/".join(parts)

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConversationMessageReceiptList:
        return ConversationsV1ConversationMessageReceiptList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> ConversationsV1ConversationMessageReceipt:
        return ConversationsV1ConversationMessageReceipt.model_validate(
            await self._t.request("GET", self._root(sid))
        )


class _AsyncConversationsV1MessagesResource:
    def __init__(self, transport: object, conversation_sid: str) -> None:
        self._t = transport
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Conversations", self._conv, "Messages", *tail]
        return "/" + "/".join(parts)

    async def create(
        self,
        *,
        author: str | None = None,
        body: str | None = None,
        attributes: str | None = None,
        content_sid: str | None = None,
    ) -> ConversationsV1ConversationMessage:
        body_form = CreateConversationsV1ConversationMessageRequest(
            Author=author,
            Body=body,
            Attributes=attributes,
            ContentSid=content_sid,
        ).to_form()
        return ConversationsV1ConversationMessage.model_validate(
            await self._t.request("POST", self._root(), data=body_form)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConversationMessageList:
        return ConversationsV1ConversationMessageList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, message_sid: str) -> ConversationsV1ConversationMessage:
        return ConversationsV1ConversationMessage.model_validate(
            await self._t.request("GET", self._root(message_sid))
        )

    async def update(
        self,
        message_sid: str,
        *,
        author: str | None = None,
        body: str | None = None,
        attributes: str | None = None,
    ) -> ConversationsV1ConversationMessage:
        body_form = UpdateConversationsV1ConversationMessageRequest(
            Author=author, Body=body, Attributes=attributes
        ).to_form()
        return ConversationsV1ConversationMessage.model_validate(
            await self._t.request("POST", self._root(message_sid), data=body_form)
        )

    async def delete(self, message_sid: str) -> None:
        await self._t.request("DELETE", self._root(message_sid))

    def receipts(
        self, message_sid: str
    ) -> _AsyncConversationsV1MessageReceiptsResource:
        return _AsyncConversationsV1MessageReceiptsResource(
            self._t, self._conv, message_sid
        )


class _AsyncConversationsV1ParticipantsResource:
    def __init__(self, transport: object, conversation_sid: str) -> None:
        self._t = transport
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Conversations", self._conv, "Participants", *tail]
        return "/" + "/".join(parts)

    async def create(
        self,
        *,
        identity: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
        messaging_binding_address: str | None = None,
        messaging_binding_proxy_address: str | None = None,
        messaging_binding_projected_address: str | None = None,
    ) -> ConversationsV1ConversationParticipant:
        body = CreateConversationsV1ConversationParticipantRequest(
            identity=identity,
            attributes=attributes,
            role_sid=role_sid,
            messaging_binding_address=messaging_binding_address,
            messaging_binding_proxy_address=messaging_binding_proxy_address,
            messaging_binding_projected_address=messaging_binding_projected_address,
        ).to_form()
        return ConversationsV1ConversationParticipant.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConversationParticipantList:
        return ConversationsV1ConversationParticipantList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(
        self, participant_sid: str
    ) -> ConversationsV1ConversationParticipant:
        return ConversationsV1ConversationParticipant.model_validate(
            await self._t.request("GET", self._root(participant_sid))
        )

    async def update(
        self,
        participant_sid: str,
        *,
        identity: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
        last_read_message_index: int | None = None,
        last_read_timestamp: str | None = None,
    ) -> ConversationsV1ConversationParticipant:
        body = UpdateConversationsV1ConversationParticipantRequest(
            Identity=identity,
            Attributes=attributes,
            RoleSid=role_sid,
            LastReadMessageIndex=last_read_message_index,
            LastReadTimestamp=last_read_timestamp,
        ).to_form()
        return ConversationsV1ConversationParticipant.model_validate(
            await self._t.request("POST", self._root(participant_sid), data=body)
        )

    async def delete(self, participant_sid: str) -> None:
        await self._t.request("DELETE", self._root(participant_sid))


class _AsyncConversationsV1WebhooksResource:
    def __init__(self, transport: object, conversation_sid: str) -> None:
        self._t = transport
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Conversations", self._conv, "Webhooks", *tail]
        return "/" + "/".join(parts)

    async def create(
        self,
        *,
        target: str,
        configuration_url: str | None = None,
        configuration_method: str | None = None,
        configuration_flow_sid: str | None = None,
        configuration_replay_after: int | None = None,
    ) -> ConversationsV1ConversationScopedWebhook:
        body = CreateConversationsV1ConversationScopedWebhookRequest(
            target=target,
            configuration_url=configuration_url,
            configuration_method=configuration_method,
            configuration_flow_sid=configuration_flow_sid,
            configuration_replay_after=configuration_replay_after,
        ).to_form()
        return ConversationsV1ConversationScopedWebhook.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConversationScopedWebhookList:
        return ConversationsV1ConversationScopedWebhookList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(
        self, webhook_sid: str
    ) -> ConversationsV1ConversationScopedWebhook:
        return ConversationsV1ConversationScopedWebhook.model_validate(
            await self._t.request("GET", self._root(webhook_sid))
        )

    async def update(
        self,
        webhook_sid: str,
        *,
        configuration_url: str | None = None,
        configuration_method: str | None = None,
        configuration_flow_sid: str | None = None,
    ) -> ConversationsV1ConversationScopedWebhook:
        body = UpdateConversationsV1ConversationScopedWebhookRequest(
            configuration_url=configuration_url,
            configuration_method=configuration_method,
            configuration_flow_sid=configuration_flow_sid,
        ).to_form()
        return ConversationsV1ConversationScopedWebhook.model_validate(
            await self._t.request("POST", self._root(webhook_sid), data=body)
        )

    async def delete(self, webhook_sid: str) -> None:
        await self._t.request("DELETE", self._root(webhook_sid))


class _AsyncConversationContext:
    def __init__(self, transport: object, conversation_sid: str) -> None:
        self.messages = _AsyncConversationsV1MessagesResource(transport, conversation_sid)
        self.participants = _AsyncConversationsV1ParticipantsResource(
            transport, conversation_sid
        )
        self.webhooks = _AsyncConversationsV1WebhooksResource(
            transport, conversation_sid
        )


class _AsyncConversationsCallable:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, conversation_sid: str) -> _AsyncConversationContext:
        return _AsyncConversationContext(self._t, conversation_sid)

    async def create(
        self,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        messaging_service_sid: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
        bindings_email_address: str | None = None,
        bindings_email_name: str | None = None,
    ) -> ConversationsV1Conversation:
        return ConversationsV1Conversation.model_validate(
            await self._t.request(
                "POST",
                "/v1/Conversations",
                data=_conversation_create_form(
                    friendly_name=friendly_name,
                    unique_name=unique_name,
                    messaging_service_sid=messaging_service_sid,
                    attributes=attributes,
                    state=state,
                    timers_inactive=timers_inactive,
                    timers_closed=timers_closed,
                    bindings_email_address=bindings_email_address,
                    bindings_email_name=bindings_email_name,
                ),
            )
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConversationList:
        return ConversationsV1ConversationList.model_validate(
            await self._t.request(
                "GET",
                "/v1/Conversations",
                params=_page_params(page_size=page_size),
            )
        )

    async def fetch(self, conversation_sid: str) -> ConversationsV1Conversation:
        return ConversationsV1Conversation.model_validate(
            await self._t.request("GET", f"/v1/Conversations/{conversation_sid}")
        )

    async def update(
        self,
        conversation_sid: str,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        messaging_service_sid: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
    ) -> ConversationsV1Conversation:
        return ConversationsV1Conversation.model_validate(
            await self._t.request(
                "POST",
                f"/v1/Conversations/{conversation_sid}",
                data=_conversation_update_form(
                    friendly_name=friendly_name,
                    unique_name=unique_name,
                    messaging_service_sid=messaging_service_sid,
                    attributes=attributes,
                    state=state,
                    timers_inactive=timers_inactive,
                    timers_closed=timers_closed,
                ),
            )
        )

    async def delete(self, conversation_sid: str) -> None:
        await self._t.request("DELETE", f"/v1/Conversations/{conversation_sid}")


class _AsyncConversationsV1RolesResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def create(
        self, *, friendly_name: str, type: str, permission: Sequence[str]
    ) -> ConversationsV1Role:
        body = CreateConversationsV1RoleRequest(
            FriendlyName=friendly_name,
            Type=type,
            Permission=list(permission),
        ).to_form()
        return ConversationsV1Role.model_validate(
            await self._t.request("POST", "/v1/Roles", data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1RoleList:
        return ConversationsV1RoleList.model_validate(
            await self._t.request(
                "GET", "/v1/Roles", params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> ConversationsV1Role:
        return ConversationsV1Role.model_validate(
            await self._t.request("GET", f"/v1/Roles/{sid}")
        )

    async def update(
        self, sid: str, *, permission: Sequence[str]
    ) -> ConversationsV1Role:
        body = UpdateConversationsV1RoleRequest(
            Permission=list(permission)
        ).to_form()
        return ConversationsV1Role.model_validate(
            await self._t.request("POST", f"/v1/Roles/{sid}", data=body)
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", f"/v1/Roles/{sid}")


class _AsyncConversationsV1UserConversationsResource:
    def __init__(self, transport: object, user_sid: str) -> None:
        self._t = transport
        self._user = user_sid

    def _root(self, *tail: str) -> str:
        parts = ["v1", "Users", self._user, "Conversations", *tail]
        return "/" + "/".join(parts)

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1UserConversationList:
        return ConversationsV1UserConversationList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(
        self, conversation_sid: str
    ) -> ConversationsV1UserConversation:
        return ConversationsV1UserConversation.model_validate(
            await self._t.request("GET", self._root(conversation_sid))
        )

    async def update(
        self,
        conversation_sid: str,
        *,
        notification_level: str | None = None,
        last_read_message_index: int | None = None,
        last_read_timestamp: str | None = None,
    ) -> ConversationsV1UserConversation:
        body = UpdateConversationsV1UserConversationRequest(
            NotificationLevel=notification_level,
            LastReadMessageIndex=last_read_message_index,
            LastReadTimestamp=last_read_timestamp,
        ).to_form()
        return ConversationsV1UserConversation.model_validate(
            await self._t.request("POST", self._root(conversation_sid), data=body)
        )

    async def delete(self, conversation_sid: str) -> None:
        await self._t.request("DELETE", self._root(conversation_sid))


class _AsyncUserContext:
    def __init__(self, transport: object, user_sid: str) -> None:
        self.conversations = _AsyncConversationsV1UserConversationsResource(
            transport, user_sid
        )


class _AsyncConversationsV1UsersCallable:
    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(self, user_sid: str) -> _AsyncUserContext:
        return _AsyncUserContext(self._t, user_sid)

    async def create(
        self,
        *,
        identity: str,
        friendly_name: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
    ) -> ConversationsV1User:
        body = CreateConversationsV1UserRequest(
            Identity=identity,
            FriendlyName=friendly_name,
            Attributes=attributes,
            RoleSid=role_sid,
        ).to_form()
        return ConversationsV1User.model_validate(
            await self._t.request("POST", "/v1/Users", data=body)
        )

    async def list(self, *, page_size: int | None = None) -> ConversationsV1UserList:
        return ConversationsV1UserList.model_validate(
            await self._t.request(
                "GET", "/v1/Users", params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> ConversationsV1User:
        return ConversationsV1User.model_validate(
            await self._t.request("GET", f"/v1/Users/{sid}")
        )

    async def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
    ) -> ConversationsV1User:
        body = UpdateConversationsV1UserRequest(
            FriendlyName=friendly_name,
            Attributes=attributes,
            RoleSid=role_sid,
        ).to_form()
        return ConversationsV1User.model_validate(
            await self._t.request("POST", f"/v1/Users/{sid}", data=body)
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", f"/v1/Users/{sid}")


class _AsyncConversationsV1CredentialsResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def create(
        self,
        *,
        type: str,
        friendly_name: str | None = None,
        certificate: str | None = None,
        private_key: str | None = None,
        sandbox: bool | None = None,
        api_key: str | None = None,
        secret: str | None = None,
    ) -> ConversationsV1Credential:
        body = CreateConversationsV1CredentialRequest(
            Type=type,
            FriendlyName=friendly_name,
            Certificate=certificate,
            PrivateKey=private_key,
            Sandbox=sandbox,
            ApiKey=api_key,
            Secret=secret,
        ).to_form()
        return ConversationsV1Credential.model_validate(
            await self._t.request("POST", "/v1/Credentials", data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1CredentialList:
        return ConversationsV1CredentialList.model_validate(
            await self._t.request(
                "GET", "/v1/Credentials", params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> ConversationsV1Credential:
        return ConversationsV1Credential.model_validate(
            await self._t.request("GET", f"/v1/Credentials/{sid}")
        )

    async def update(
        self,
        sid: str,
        *,
        type: str | None = None,
        friendly_name: str | None = None,
        certificate: str | None = None,
        private_key: str | None = None,
        sandbox: bool | None = None,
        api_key: str | None = None,
        secret: str | None = None,
    ) -> ConversationsV1Credential:
        body = UpdateConversationsV1CredentialRequest(
            Type=type,
            FriendlyName=friendly_name,
            Certificate=certificate,
            PrivateKey=private_key,
            Sandbox=sandbox,
            ApiKey=api_key,
            Secret=secret,
        ).to_form()
        return ConversationsV1Credential.model_validate(
            await self._t.request("POST", f"/v1/Credentials/{sid}", data=body)
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", f"/v1/Credentials/{sid}")


class _AsyncConversationsV1ConfigWebhooksResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def fetch(self) -> ConversationsV1ConfigurationWebhook:
        return ConversationsV1ConfigurationWebhook.model_validate(
            await self._t.request("GET", "/v1/Configuration/Webhooks")
        )

    async def update(
        self,
        *,
        method: str | None = None,
        filters: Sequence[str] | None = None,
        pre_webhook_url: str | None = None,
        post_webhook_url: str | None = None,
        target: str | None = None,
    ) -> ConversationsV1ConfigurationWebhook:
        body = UpdateConversationsV1ConfigurationWebhookRequest(
            Method=method,
            Filters=list(filters) if filters is not None else None,
            PreWebhookUrl=pre_webhook_url,
            PostWebhookUrl=post_webhook_url,
            Target=target,
        ).to_form()
        return ConversationsV1ConfigurationWebhook.model_validate(
            await self._t.request("POST", "/v1/Configuration/Webhooks", data=body)
        )


class _AsyncConversationsV1ConfigAddressesResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def create(
        self,
        *,
        type: str,
        address: str,
        friendly_name: str | None = None,
        auto_creation_enabled: bool | None = None,
        auto_creation_type: str | None = None,
        auto_creation_webhook_url: str | None = None,
        address_country: str | None = None,
    ) -> ConversationsV1ConfigAddress:
        body = CreateConversationsV1ConfigAddressRequest(
            type=type,
            address=address,
            friendly_name=friendly_name,
            auto_creation_enabled=auto_creation_enabled,
            auto_creation_type=auto_creation_type,
            auto_creation_webhook_url=auto_creation_webhook_url,
            address_country=address_country,
        ).to_form()
        return ConversationsV1ConfigAddress.model_validate(
            await self._t.request("POST", "/v1/Configuration/Addresses", data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ConfigAddressList:
        return ConversationsV1ConfigAddressList.model_validate(
            await self._t.request(
                "GET",
                "/v1/Configuration/Addresses",
                params=_page_params(page_size=page_size),
            )
        )

    async def fetch(self, sid: str) -> ConversationsV1ConfigAddress:
        return ConversationsV1ConfigAddress.model_validate(
            await self._t.request("GET", f"/v1/Configuration/Addresses/{sid}")
        )

    async def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        auto_creation_enabled: bool | None = None,
        auto_creation_type: str | None = None,
        auto_creation_webhook_url: str | None = None,
    ) -> ConversationsV1ConfigAddress:
        body = UpdateConversationsV1ConfigAddressRequest(
            friendly_name=friendly_name,
            auto_creation_enabled=auto_creation_enabled,
            auto_creation_type=auto_creation_type,
            auto_creation_webhook_url=auto_creation_webhook_url,
        ).to_form()
        return ConversationsV1ConfigAddress.model_validate(
            await self._t.request(
                "POST", f"/v1/Configuration/Addresses/{sid}", data=body
            )
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", f"/v1/Configuration/Addresses/{sid}")


class _AsyncConversationsV1ConfigurationResource:
    def __init__(self, transport: object) -> None:
        self._t = transport
        self.webhooks = _AsyncConversationsV1ConfigWebhooksResource(transport)
        self.addresses = _AsyncConversationsV1ConfigAddressesResource(transport)

    async def fetch(self) -> ConversationsV1Configuration:
        return ConversationsV1Configuration.model_validate(
            await self._t.request("GET", "/v1/Configuration")
        )

    async def update(
        self,
        *,
        default_chat_service_sid: str | None = None,
        default_messaging_service_sid: str | None = None,
        default_inactive_timer: str | None = None,
        default_closed_timer: str | None = None,
    ) -> ConversationsV1Configuration:
        body = UpdateConversationsV1ConfigurationRequest(
            DefaultChatServiceSid=default_chat_service_sid,
            DefaultMessagingServiceSid=default_messaging_service_sid,
            DefaultInactiveTimer=default_inactive_timer,
            DefaultClosedTimer=default_closed_timer,
        ).to_form()
        return ConversationsV1Configuration.model_validate(
            await self._t.request("POST", "/v1/Configuration", data=body)
        )


class _AsyncConversationsV1ParticipantConversationsResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def list(
        self,
        *,
        identity: str | None = None,
        address: str | None = None,
        page_size: int | None = None,
    ) -> ConversationsV1ParticipantConversationList:
        return ConversationsV1ParticipantConversationList.model_validate(
            await self._t.request(
                "GET",
                "/v1/ParticipantConversations",
                params={
                    "Identity": identity,
                    "Address": address,
                    "PageSize": page_size,
                },
            )
        )


class _AsyncConversationsV1ConversationWithParticipantsResource:
    def __init__(self, transport: object) -> None:
        self._t = transport

    async def create(
        self,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        messaging_service_sid: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
        participant: Sequence[str] | None = None,
    ) -> ConversationsV1ConversationWithParticipants:
        body = CreateConversationsV1ConversationWithParticipantsRequest(
            friendly_name=friendly_name,
            unique_name=unique_name,
            messaging_service_sid=messaging_service_sid,
            attributes=attributes,
            state=state,
            timers_inactive=timers_inactive,
            timers_closed=timers_closed,
            participant=list(participant) if participant is not None else None,
        ).to_form()
        return ConversationsV1ConversationWithParticipants.model_validate(
            await self._t.request(
                "POST", "/v1/ConversationWithParticipants", data=body
            )
        )


class _AsyncConversationsV1ServicesResource:
    """``/v1/Services`` (async) — see sync sibling for behaviour."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def __call__(
        self, chat_service_sid: str
    ) -> _AsyncConversationsV1ServiceScopeResource:
        return _AsyncConversationsV1ServiceScopeResource(self._t, chat_service_sid)

    async def create(self, *, friendly_name: str) -> ConversationsV1Service:
        body = CreateConversationsV1ServiceRequest(
            FriendlyName=friendly_name
        ).to_form()
        return ConversationsV1Service.model_validate(
            await self._t.request("POST", "/v1/Services", data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceList:
        return ConversationsV1ServiceList.model_validate(
            await self._t.request(
                "GET", "/v1/Services", params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, chat_service_sid: str) -> ConversationsV1Service:
        return ConversationsV1Service.model_validate(
            await self._t.request("GET", f"/v1/Services/{chat_service_sid}")
        )

    async def delete(self, chat_service_sid: str) -> None:
        await self._t.request("DELETE", f"/v1/Services/{chat_service_sid}")


class ConversationsV1AsyncResource:
    """Holder for ``client.conversations_v1.*`` sub-resources (async)."""

    def __init__(self, transport: object) -> None:
        self.conversations = _AsyncConversationsCallable(transport)
        self.roles = _AsyncConversationsV1RolesResource(transport)
        self.users = _AsyncConversationsV1UsersCallable(transport)
        self.credentials = _AsyncConversationsV1CredentialsResource(transport)
        self.configuration = _AsyncConversationsV1ConfigurationResource(transport)
        self.participant_conversations = (
            _AsyncConversationsV1ParticipantConversationsResource(transport)
        )
        self.conversation_with_participants = (
            _AsyncConversationsV1ConversationWithParticipantsResource(transport)
        )
        self.services = _AsyncConversationsV1ServicesResource(transport)


# ===========================================================================
# Phase 4 — service-scoped sub-resources under
# ``/v1/Services/{ChatServiceSid}/…``
#
# Returned from ``client.conversations_v1.services(chat_service_sid)``.
# Layout mirrors the account-level surface, with ``chat_service_sid`` bound
# at scope construction time so callers don't repeat it.
# ===========================================================================


def _service_root(service_sid: str, *tail: str) -> str:
    parts = ["v1", "Services", service_sid, *tail]
    return "/" + "/".join(parts)


# ---------------------------------------------------------------------------
# Sync service-scoped resources
# ---------------------------------------------------------------------------


class _ConversationsV1ServiceMessageReceiptsResource:
    """``/v1/Services/{Sid}/Conversations/{ConvSid}/Messages/{MsgSid}/Receipts`` (sync)."""

    def __init__(
        self, transport: object, service_sid: str, conversation_sid: str, message_sid: str
    ) -> None:
        self._t = transport
        self._svc = service_sid
        self._conv = conversation_sid
        self._msg = message_sid

    def _root(self, *tail: str) -> str:
        return _service_root(
            self._svc,
            "Conversations", self._conv,
            "Messages", self._msg,
            "Receipts", *tail,
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceConversationMessageReceiptList:
        return ConversationsV1ServiceConversationMessageReceiptList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> ConversationsV1ServiceConversationMessageReceipt:
        return ConversationsV1ServiceConversationMessageReceipt.model_validate(
            self._t.request("GET", self._root(sid))
        )


class _ConversationsV1ServiceMessagesResource:
    """``/v1/Services/{Sid}/Conversations/{ConvSid}/Messages`` (sync)."""

    def __init__(
        self, transport: object, service_sid: str, conversation_sid: str
    ) -> None:
        self._t = transport
        self._svc = service_sid
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        return _service_root(
            self._svc, "Conversations", self._conv, "Messages", *tail
        )

    def create(
        self,
        *,
        author: str | None = None,
        body: str | None = None,
        attributes: str | None = None,
        content_sid: str | None = None,
    ) -> ConversationsV1ServiceConversationMessage:
        body_form = CreateConversationsV1ServiceConversationMessageRequest(
            author=author,
            body=body,
            attributes=attributes,
            content_sid=content_sid,
        ).to_form()
        return ConversationsV1ServiceConversationMessage.model_validate(
            self._t.request("POST", self._root(), data=body_form)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceConversationMessageList:
        return ConversationsV1ServiceConversationMessageList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, message_sid: str) -> ConversationsV1ServiceConversationMessage:
        return ConversationsV1ServiceConversationMessage.model_validate(
            self._t.request("GET", self._root(message_sid))
        )

    def update(
        self,
        message_sid: str,
        *,
        author: str | None = None,
        body: str | None = None,
        attributes: str | None = None,
    ) -> ConversationsV1ServiceConversationMessage:
        body_form = UpdateConversationsV1ServiceConversationMessageRequest(
            author=author, body=body, attributes=attributes
        ).to_form()
        return ConversationsV1ServiceConversationMessage.model_validate(
            self._t.request("POST", self._root(message_sid), data=body_form)
        )

    def delete(self, message_sid: str) -> None:
        self._t.request("DELETE", self._root(message_sid))

    def receipts(
        self, message_sid: str
    ) -> _ConversationsV1ServiceMessageReceiptsResource:
        return _ConversationsV1ServiceMessageReceiptsResource(
            self._t, self._svc, self._conv, message_sid
        )


class _ConversationsV1ServiceParticipantsResource:
    """``/v1/Services/{Sid}/Conversations/{ConvSid}/Participants`` (sync)."""

    def __init__(
        self, transport: object, service_sid: str, conversation_sid: str
    ) -> None:
        self._t = transport
        self._svc = service_sid
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        return _service_root(
            self._svc, "Conversations", self._conv, "Participants", *tail
        )

    def create(
        self,
        *,
        identity: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
        messaging_binding_address: str | None = None,
        messaging_binding_proxy_address: str | None = None,
        messaging_binding_projected_address: str | None = None,
    ) -> ConversationsV1ServiceConversationParticipant:
        body = CreateConversationsV1ServiceConversationParticipantRequest(
            identity=identity,
            attributes=attributes,
            role_sid=role_sid,
            messaging_binding_address=messaging_binding_address,
            messaging_binding_proxy_address=messaging_binding_proxy_address,
            messaging_binding_projected_address=messaging_binding_projected_address,
        ).to_form()
        return ConversationsV1ServiceConversationParticipant.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceConversationParticipantList:
        return ConversationsV1ServiceConversationParticipantList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(
        self, participant_sid: str
    ) -> ConversationsV1ServiceConversationParticipant:
        return ConversationsV1ServiceConversationParticipant.model_validate(
            self._t.request("GET", self._root(participant_sid))
        )

    def update(
        self,
        participant_sid: str,
        *,
        attributes: str | None = None,
        role_sid: str | None = None,
    ) -> ConversationsV1ServiceConversationParticipant:
        body = UpdateConversationsV1ServiceConversationParticipantRequest(
            attributes=attributes,
            role_sid=role_sid,
        ).to_form()
        return ConversationsV1ServiceConversationParticipant.model_validate(
            self._t.request("POST", self._root(participant_sid), data=body)
        )

    def delete(self, participant_sid: str) -> None:
        self._t.request("DELETE", self._root(participant_sid))


class _ConversationsV1ServiceConversationWebhooksResource:
    """``/v1/Services/{Sid}/Conversations/{ConvSid}/Webhooks`` (sync)."""

    def __init__(
        self, transport: object, service_sid: str, conversation_sid: str
    ) -> None:
        self._t = transport
        self._svc = service_sid
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        return _service_root(
            self._svc, "Conversations", self._conv, "Webhooks", *tail
        )

    def create(
        self,
        *,
        target: str,
        configuration_url: str | None = None,
        configuration_method: str | None = None,
        configuration_flow_sid: str | None = None,
    ) -> ConversationsV1ServiceConversationScopedWebhook:
        body = CreateConversationsV1ServiceConversationScopedWebhookRequest(
            target=target,
            configuration_url=configuration_url,
            configuration_method=configuration_method,
            configuration_flow_sid=configuration_flow_sid,
        ).to_form()
        return ConversationsV1ServiceConversationScopedWebhook.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceConversationScopedWebhookList:
        return ConversationsV1ServiceConversationScopedWebhookList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(
        self, webhook_sid: str
    ) -> ConversationsV1ServiceConversationScopedWebhook:
        return ConversationsV1ServiceConversationScopedWebhook.model_validate(
            self._t.request("GET", self._root(webhook_sid))
        )

    def update(
        self,
        webhook_sid: str,
        *,
        configuration_url: str | None = None,
        configuration_method: str | None = None,
        configuration_flow_sid: str | None = None,
    ) -> ConversationsV1ServiceConversationScopedWebhook:
        body = UpdateConversationsV1ServiceConversationScopedWebhookRequest(
            configuration_url=configuration_url,
            configuration_method=configuration_method,
            configuration_flow_sid=configuration_flow_sid,
        ).to_form()
        return ConversationsV1ServiceConversationScopedWebhook.model_validate(
            self._t.request("POST", self._root(webhook_sid), data=body)
        )

    def delete(self, webhook_sid: str) -> None:
        self._t.request("DELETE", self._root(webhook_sid))


class _ServiceConversationContext:
    """Returned by ``services(svc).conversations(conv_sid)`` — sub-resource factory (sync)."""

    def __init__(
        self, transport: object, service_sid: str, conversation_sid: str
    ) -> None:
        self.messages = _ConversationsV1ServiceMessagesResource(
            transport, service_sid, conversation_sid
        )
        self.participants = _ConversationsV1ServiceParticipantsResource(
            transport, service_sid, conversation_sid
        )
        self.webhooks = _ConversationsV1ServiceConversationWebhooksResource(
            transport, service_sid, conversation_sid
        )


class _ConversationsV1ServiceConversationsCallable:
    """``services(svc).conversations`` — callable + namespace (sync)."""

    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def __call__(self, conversation_sid: str) -> _ServiceConversationContext:
        return _ServiceConversationContext(self._t, self._svc, conversation_sid)

    def _root(self, *tail: str) -> str:
        return _service_root(self._svc, "Conversations", *tail)

    def create(
        self,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        messaging_service_sid: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
    ) -> ConversationsV1ServiceConversation:
        body = CreateConversationsV1ServiceConversationRequest(
            friendly_name=friendly_name,
            unique_name=unique_name,
            messaging_service_sid=messaging_service_sid,
            attributes=attributes,
            state=state,
            timers_inactive=timers_inactive,
            timers_closed=timers_closed,
        ).to_form()
        return ConversationsV1ServiceConversation.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceConversationList:
        return ConversationsV1ServiceConversationList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, conversation_sid: str) -> ConversationsV1ServiceConversation:
        return ConversationsV1ServiceConversation.model_validate(
            self._t.request("GET", self._root(conversation_sid))
        )

    def update(
        self,
        conversation_sid: str,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
    ) -> ConversationsV1ServiceConversation:
        body = UpdateConversationsV1ServiceConversationRequest(
            friendly_name=friendly_name,
            unique_name=unique_name,
            attributes=attributes,
            state=state,
            timers_inactive=timers_inactive,
            timers_closed=timers_closed,
        ).to_form()
        return ConversationsV1ServiceConversation.model_validate(
            self._t.request("POST", self._root(conversation_sid), data=body)
        )

    def delete(self, conversation_sid: str) -> None:
        self._t.request("DELETE", self._root(conversation_sid))


class _ConversationsV1ServiceRolesResource:
    """``/v1/Services/{Sid}/Roles`` (sync)."""

    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _root(self, *tail: str) -> str:
        return _service_root(self._svc, "Roles", *tail)

    def create(
        self, *, friendly_name: str, type: str, permission: Sequence[str]
    ) -> ConversationsV1ServiceRole:
        body = CreateConversationsV1ServiceRoleRequest(
            friendly_name=friendly_name,
            type=type,
            permission=list(permission),
        ).to_form()
        return ConversationsV1ServiceRole.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceRoleList:
        return ConversationsV1ServiceRoleList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> ConversationsV1ServiceRole:
        return ConversationsV1ServiceRole.model_validate(
            self._t.request("GET", self._root(sid))
        )

    def update(
        self, sid: str, *, permission: Sequence[str]
    ) -> ConversationsV1ServiceRole:
        body = UpdateConversationsV1ServiceRoleRequest(
            permission=list(permission)
        ).to_form()
        return ConversationsV1ServiceRole.model_validate(
            self._t.request("POST", self._root(sid), data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", self._root(sid))


class _ConversationsV1ServiceUserConversationsResource:
    """``/v1/Services/{Sid}/Users/{UserSid}/Conversations`` (sync) — list only."""

    def __init__(
        self, transport: object, service_sid: str, user_sid: str
    ) -> None:
        self._t = transport
        self._svc = service_sid
        self._user = user_sid

    def _root(self, *tail: str) -> str:
        return _service_root(
            self._svc, "Users", self._user, "Conversations", *tail
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceUserConversationList:
        return ConversationsV1ServiceUserConversationList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )


class _ServiceUserContext:
    """Returned by ``services(svc).users(user_sid)`` (sync)."""

    def __init__(
        self, transport: object, service_sid: str, user_sid: str
    ) -> None:
        self.conversations = _ConversationsV1ServiceUserConversationsResource(
            transport, service_sid, user_sid
        )


class _ConversationsV1ServiceUsersCallable:
    """``services(svc).users`` — callable + namespace (sync)."""

    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def __call__(self, user_sid: str) -> _ServiceUserContext:
        return _ServiceUserContext(self._t, self._svc, user_sid)

    def _root(self, *tail: str) -> str:
        return _service_root(self._svc, "Users", *tail)

    def create(
        self,
        *,
        identity: str,
        friendly_name: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
    ) -> ConversationsV1ServiceUser:
        body = CreateConversationsV1ServiceUserRequest(
            identity=identity,
            friendly_name=friendly_name,
            attributes=attributes,
            role_sid=role_sid,
        ).to_form()
        return ConversationsV1ServiceUser.model_validate(
            self._t.request("POST", self._root(), data=body)
        )

    def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceUserList:
        return ConversationsV1ServiceUserList.model_validate(
            self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> ConversationsV1ServiceUser:
        return ConversationsV1ServiceUser.model_validate(
            self._t.request("GET", self._root(sid))
        )

    def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
    ) -> ConversationsV1ServiceUser:
        body = UpdateConversationsV1ServiceUserRequest(
            friendly_name=friendly_name,
            attributes=attributes,
            role_sid=role_sid,
        ).to_form()
        return ConversationsV1ServiceUser.model_validate(
            self._t.request("POST", self._root(sid), data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", self._root(sid))


class _ConversationsV1ServiceBindingsResource:
    """``/v1/Services/{Sid}/Bindings`` (sync) — list+fetch+delete only."""

    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _root(self, *tail: str) -> str:
        return _service_root(self._svc, "Bindings", *tail)

    def list(
        self,
        *,
        binding_type: str | None = None,
        identity: str | None = None,
        page_size: int | None = None,
    ) -> ConversationsV1ServiceBindingList:
        return ConversationsV1ServiceBindingList.model_validate(
            self._t.request(
                "GET",
                self._root(),
                params={
                    "BindingType": binding_type,
                    "Identity": identity,
                    "PageSize": page_size,
                },
            )
        )

    def fetch(self, sid: str) -> ConversationsV1ServiceBinding:
        return ConversationsV1ServiceBinding.model_validate(
            self._t.request("GET", self._root(sid))
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", self._root(sid))


class _ConversationsV1ServiceNotificationsResource:
    """``/v1/Services/{Sid}/Configuration/Notifications`` (sync) — singleton."""

    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _path(self) -> str:
        return _service_root(self._svc, "Configuration", "Notifications")

    def fetch(self) -> ConversationsV1ServiceNotification:
        return ConversationsV1ServiceNotification.model_validate(
            self._t.request("GET", self._path())
        )

    def update(
        self,
        *,
        log_enabled: bool | None = None,
        new_message_enabled: bool | None = None,
        new_message_template: str | None = None,
        new_message_sound: str | None = None,
        new_message_badge_count_enabled: bool | None = None,
        new_message_with_media_enabled: bool | None = None,
        new_message_with_media_template: str | None = None,
        added_to_conversation_enabled: bool | None = None,
        added_to_conversation_template: str | None = None,
        added_to_conversation_sound: str | None = None,
        removed_from_conversation_enabled: bool | None = None,
        removed_from_conversation_template: str | None = None,
        removed_from_conversation_sound: str | None = None,
    ) -> ConversationsV1ServiceNotification:
        body = UpdateConversationsV1ServiceNotificationRequest(
            log_enabled=log_enabled,
            new_message_enabled=new_message_enabled,
            new_message_template=new_message_template,
            new_message_sound=new_message_sound,
            new_message_badge_count_enabled=new_message_badge_count_enabled,
            new_message_with_media_enabled=new_message_with_media_enabled,
            new_message_with_media_template=new_message_with_media_template,
            added_to_conversation_enabled=added_to_conversation_enabled,
            added_to_conversation_template=added_to_conversation_template,
            added_to_conversation_sound=added_to_conversation_sound,
            removed_from_conversation_enabled=removed_from_conversation_enabled,
            removed_from_conversation_template=removed_from_conversation_template,
            removed_from_conversation_sound=removed_from_conversation_sound,
        ).to_form()
        return ConversationsV1ServiceNotification.model_validate(
            self._t.request("POST", self._path(), data=body)
        )


class _ConversationsV1ServiceWebhookConfigurationResource:
    """``/v1/Services/{Sid}/Configuration/Webhooks`` (sync) — singleton."""

    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _path(self) -> str:
        return _service_root(self._svc, "Configuration", "Webhooks")

    def fetch(self) -> ConversationsV1ServiceWebhookConfiguration:
        return ConversationsV1ServiceWebhookConfiguration.model_validate(
            self._t.request("GET", self._path())
        )

    def update(
        self,
        *,
        pre_webhook_url: str | None = None,
        post_webhook_url: str | None = None,
        method: str | None = None,
        filters: Sequence[str] | None = None,
    ) -> ConversationsV1ServiceWebhookConfiguration:
        body = UpdateConversationsV1ServiceWebhookConfigurationRequest(
            pre_webhook_url=pre_webhook_url,
            post_webhook_url=post_webhook_url,
            method=method,
            filters=list(filters) if filters is not None else None,
        ).to_form()
        return ConversationsV1ServiceWebhookConfiguration.model_validate(
            self._t.request("POST", self._path(), data=body)
        )


class _ConversationsV1ServiceConfigurationResource:
    """``/v1/Services/{Sid}/Configuration`` (sync) + nested ``.notifications`` / ``.webhooks``."""

    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid
        self.notifications = _ConversationsV1ServiceNotificationsResource(
            transport, service_sid
        )
        self.webhooks = _ConversationsV1ServiceWebhookConfigurationResource(
            transport, service_sid
        )

    def _path(self) -> str:
        return _service_root(self._svc, "Configuration")

    def fetch(self) -> ConversationsV1ServiceConfiguration:
        return ConversationsV1ServiceConfiguration.model_validate(
            self._t.request("GET", self._path())
        )

    def update(
        self,
        *,
        default_chat_service_role_sid: str | None = None,
        default_conversation_creator_role_sid: str | None = None,
        default_conversation_role_sid: str | None = None,
        reachability_enabled: bool | None = None,
    ) -> ConversationsV1ServiceConfiguration:
        body = UpdateConversationsV1ServiceConfigurationRequest(
            default_chat_service_role_sid=default_chat_service_role_sid,
            default_conversation_creator_role_sid=default_conversation_creator_role_sid,
            default_conversation_role_sid=default_conversation_role_sid,
            reachability_enabled=reachability_enabled,
        ).to_form()
        return ConversationsV1ServiceConfiguration.model_validate(
            self._t.request("POST", self._path(), data=body)
        )


class _ConversationsV1ServiceParticipantConversationsResource:
    """``/v1/Services/{Sid}/ParticipantConversations`` (sync) — list only."""

    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _path(self) -> str:
        return _service_root(self._svc, "ParticipantConversations")

    def list(
        self,
        *,
        identity: str | None = None,
        address: str | None = None,
        page_size: int | None = None,
    ) -> ConversationsV1ServiceParticipantConversationList:
        return ConversationsV1ServiceParticipantConversationList.model_validate(
            self._t.request(
                "GET",
                self._path(),
                params={
                    "Identity": identity,
                    "Address": address,
                    "PageSize": page_size,
                },
            )
        )


class _ConversationsV1ServiceConversationWithParticipantsResource:
    """``/v1/Services/{Sid}/ConversationWithParticipants`` (sync) — create only."""

    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _path(self) -> str:
        return _service_root(self._svc, "ConversationWithParticipants")

    def create(
        self,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        messaging_service_sid: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
        participant: Sequence[str] | None = None,
    ) -> ConversationsV1ServiceConversationWithParticipants:
        body = CreateConversationsV1ServiceConversationWithParticipantsRequest(
            friendly_name=friendly_name,
            unique_name=unique_name,
            messaging_service_sid=messaging_service_sid,
            attributes=attributes,
            state=state,
            timers_inactive=timers_inactive,
            timers_closed=timers_closed,
            participant=list(participant) if participant is not None else None,
        ).to_form()
        return ConversationsV1ServiceConversationWithParticipants.model_validate(
            self._t.request("POST", self._path(), data=body)
        )


class _ConversationsV1ServiceScopeResource:
    """Per-service Conversations v1 surface (sync).

    Returned from ``client.conversations_v1.services(chat_service_sid)``;
    every attribute is bound to ``chat_service_sid`` so callers don't repeat it.
    """

    def __init__(self, transport: object, chat_service_sid: str) -> None:
        self._t = transport
        self._svc = chat_service_sid
        self.conversations = _ConversationsV1ServiceConversationsCallable(
            transport, chat_service_sid
        )
        self.roles = _ConversationsV1ServiceRolesResource(transport, chat_service_sid)
        self.users = _ConversationsV1ServiceUsersCallable(transport, chat_service_sid)
        self.bindings = _ConversationsV1ServiceBindingsResource(
            transport, chat_service_sid
        )
        self.configuration = _ConversationsV1ServiceConfigurationResource(
            transport, chat_service_sid
        )
        self.participant_conversations = (
            _ConversationsV1ServiceParticipantConversationsResource(
                transport, chat_service_sid
            )
        )
        self.conversation_with_participants = (
            _ConversationsV1ServiceConversationWithParticipantsResource(
                transport, chat_service_sid
            )
        )


# ---------------------------------------------------------------------------
# Async service-scoped resources — same surface; methods are awaitable.
# ---------------------------------------------------------------------------


class _AsyncConversationsV1ServiceMessageReceiptsResource:
    def __init__(
        self, transport: object, service_sid: str, conversation_sid: str, message_sid: str
    ) -> None:
        self._t = transport
        self._svc = service_sid
        self._conv = conversation_sid
        self._msg = message_sid

    def _root(self, *tail: str) -> str:
        return _service_root(
            self._svc,
            "Conversations", self._conv,
            "Messages", self._msg,
            "Receipts", *tail,
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceConversationMessageReceiptList:
        return ConversationsV1ServiceConversationMessageReceiptList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(
        self, sid: str
    ) -> ConversationsV1ServiceConversationMessageReceipt:
        return ConversationsV1ServiceConversationMessageReceipt.model_validate(
            await self._t.request("GET", self._root(sid))
        )


class _AsyncConversationsV1ServiceMessagesResource:
    def __init__(
        self, transport: object, service_sid: str, conversation_sid: str
    ) -> None:
        self._t = transport
        self._svc = service_sid
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        return _service_root(
            self._svc, "Conversations", self._conv, "Messages", *tail
        )

    async def create(
        self,
        *,
        author: str | None = None,
        body: str | None = None,
        attributes: str | None = None,
        content_sid: str | None = None,
    ) -> ConversationsV1ServiceConversationMessage:
        body_form = CreateConversationsV1ServiceConversationMessageRequest(
            author=author,
            body=body,
            attributes=attributes,
            content_sid=content_sid,
        ).to_form()
        return ConversationsV1ServiceConversationMessage.model_validate(
            await self._t.request("POST", self._root(), data=body_form)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceConversationMessageList:
        return ConversationsV1ServiceConversationMessageList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(
        self, message_sid: str
    ) -> ConversationsV1ServiceConversationMessage:
        return ConversationsV1ServiceConversationMessage.model_validate(
            await self._t.request("GET", self._root(message_sid))
        )

    async def update(
        self,
        message_sid: str,
        *,
        author: str | None = None,
        body: str | None = None,
        attributes: str | None = None,
    ) -> ConversationsV1ServiceConversationMessage:
        body_form = UpdateConversationsV1ServiceConversationMessageRequest(
            author=author, body=body, attributes=attributes
        ).to_form()
        return ConversationsV1ServiceConversationMessage.model_validate(
            await self._t.request("POST", self._root(message_sid), data=body_form)
        )

    async def delete(self, message_sid: str) -> None:
        await self._t.request("DELETE", self._root(message_sid))

    def receipts(
        self, message_sid: str
    ) -> _AsyncConversationsV1ServiceMessageReceiptsResource:
        return _AsyncConversationsV1ServiceMessageReceiptsResource(
            self._t, self._svc, self._conv, message_sid
        )


class _AsyncConversationsV1ServiceParticipantsResource:
    def __init__(
        self, transport: object, service_sid: str, conversation_sid: str
    ) -> None:
        self._t = transport
        self._svc = service_sid
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        return _service_root(
            self._svc, "Conversations", self._conv, "Participants", *tail
        )

    async def create(
        self,
        *,
        identity: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
        messaging_binding_address: str | None = None,
        messaging_binding_proxy_address: str | None = None,
        messaging_binding_projected_address: str | None = None,
    ) -> ConversationsV1ServiceConversationParticipant:
        body = CreateConversationsV1ServiceConversationParticipantRequest(
            identity=identity,
            attributes=attributes,
            role_sid=role_sid,
            messaging_binding_address=messaging_binding_address,
            messaging_binding_proxy_address=messaging_binding_proxy_address,
            messaging_binding_projected_address=messaging_binding_projected_address,
        ).to_form()
        return ConversationsV1ServiceConversationParticipant.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceConversationParticipantList:
        return ConversationsV1ServiceConversationParticipantList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(
        self, participant_sid: str
    ) -> ConversationsV1ServiceConversationParticipant:
        return ConversationsV1ServiceConversationParticipant.model_validate(
            await self._t.request("GET", self._root(participant_sid))
        )

    async def update(
        self,
        participant_sid: str,
        *,
        attributes: str | None = None,
        role_sid: str | None = None,
    ) -> ConversationsV1ServiceConversationParticipant:
        body = UpdateConversationsV1ServiceConversationParticipantRequest(
            attributes=attributes,
            role_sid=role_sid,
        ).to_form()
        return ConversationsV1ServiceConversationParticipant.model_validate(
            await self._t.request("POST", self._root(participant_sid), data=body)
        )

    async def delete(self, participant_sid: str) -> None:
        await self._t.request("DELETE", self._root(participant_sid))


class _AsyncConversationsV1ServiceConversationWebhooksResource:
    def __init__(
        self, transport: object, service_sid: str, conversation_sid: str
    ) -> None:
        self._t = transport
        self._svc = service_sid
        self._conv = conversation_sid

    def _root(self, *tail: str) -> str:
        return _service_root(
            self._svc, "Conversations", self._conv, "Webhooks", *tail
        )

    async def create(
        self,
        *,
        target: str,
        configuration_url: str | None = None,
        configuration_method: str | None = None,
        configuration_flow_sid: str | None = None,
    ) -> ConversationsV1ServiceConversationScopedWebhook:
        body = CreateConversationsV1ServiceConversationScopedWebhookRequest(
            target=target,
            configuration_url=configuration_url,
            configuration_method=configuration_method,
            configuration_flow_sid=configuration_flow_sid,
        ).to_form()
        return ConversationsV1ServiceConversationScopedWebhook.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceConversationScopedWebhookList:
        return ConversationsV1ServiceConversationScopedWebhookList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(
        self, webhook_sid: str
    ) -> ConversationsV1ServiceConversationScopedWebhook:
        return ConversationsV1ServiceConversationScopedWebhook.model_validate(
            await self._t.request("GET", self._root(webhook_sid))
        )

    async def update(
        self,
        webhook_sid: str,
        *,
        configuration_url: str | None = None,
        configuration_method: str | None = None,
        configuration_flow_sid: str | None = None,
    ) -> ConversationsV1ServiceConversationScopedWebhook:
        body = UpdateConversationsV1ServiceConversationScopedWebhookRequest(
            configuration_url=configuration_url,
            configuration_method=configuration_method,
            configuration_flow_sid=configuration_flow_sid,
        ).to_form()
        return ConversationsV1ServiceConversationScopedWebhook.model_validate(
            await self._t.request("POST", self._root(webhook_sid), data=body)
        )

    async def delete(self, webhook_sid: str) -> None:
        await self._t.request("DELETE", self._root(webhook_sid))


class _AsyncServiceConversationContext:
    def __init__(
        self, transport: object, service_sid: str, conversation_sid: str
    ) -> None:
        self.messages = _AsyncConversationsV1ServiceMessagesResource(
            transport, service_sid, conversation_sid
        )
        self.participants = _AsyncConversationsV1ServiceParticipantsResource(
            transport, service_sid, conversation_sid
        )
        self.webhooks = _AsyncConversationsV1ServiceConversationWebhooksResource(
            transport, service_sid, conversation_sid
        )


class _AsyncConversationsV1ServiceConversationsCallable:
    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def __call__(self, conversation_sid: str) -> _AsyncServiceConversationContext:
        return _AsyncServiceConversationContext(self._t, self._svc, conversation_sid)

    def _root(self, *tail: str) -> str:
        return _service_root(self._svc, "Conversations", *tail)

    async def create(
        self,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        messaging_service_sid: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
    ) -> ConversationsV1ServiceConversation:
        body = CreateConversationsV1ServiceConversationRequest(
            friendly_name=friendly_name,
            unique_name=unique_name,
            messaging_service_sid=messaging_service_sid,
            attributes=attributes,
            state=state,
            timers_inactive=timers_inactive,
            timers_closed=timers_closed,
        ).to_form()
        return ConversationsV1ServiceConversation.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceConversationList:
        return ConversationsV1ServiceConversationList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(
        self, conversation_sid: str
    ) -> ConversationsV1ServiceConversation:
        return ConversationsV1ServiceConversation.model_validate(
            await self._t.request("GET", self._root(conversation_sid))
        )

    async def update(
        self,
        conversation_sid: str,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
    ) -> ConversationsV1ServiceConversation:
        body = UpdateConversationsV1ServiceConversationRequest(
            friendly_name=friendly_name,
            unique_name=unique_name,
            attributes=attributes,
            state=state,
            timers_inactive=timers_inactive,
            timers_closed=timers_closed,
        ).to_form()
        return ConversationsV1ServiceConversation.model_validate(
            await self._t.request("POST", self._root(conversation_sid), data=body)
        )

    async def delete(self, conversation_sid: str) -> None:
        await self._t.request("DELETE", self._root(conversation_sid))


class _AsyncConversationsV1ServiceRolesResource:
    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _root(self, *tail: str) -> str:
        return _service_root(self._svc, "Roles", *tail)

    async def create(
        self, *, friendly_name: str, type: str, permission: Sequence[str]
    ) -> ConversationsV1ServiceRole:
        body = CreateConversationsV1ServiceRoleRequest(
            friendly_name=friendly_name,
            type=type,
            permission=list(permission),
        ).to_form()
        return ConversationsV1ServiceRole.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceRoleList:
        return ConversationsV1ServiceRoleList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> ConversationsV1ServiceRole:
        return ConversationsV1ServiceRole.model_validate(
            await self._t.request("GET", self._root(sid))
        )

    async def update(
        self, sid: str, *, permission: Sequence[str]
    ) -> ConversationsV1ServiceRole:
        body = UpdateConversationsV1ServiceRoleRequest(
            permission=list(permission)
        ).to_form()
        return ConversationsV1ServiceRole.model_validate(
            await self._t.request("POST", self._root(sid), data=body)
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", self._root(sid))


class _AsyncConversationsV1ServiceUserConversationsResource:
    def __init__(
        self, transport: object, service_sid: str, user_sid: str
    ) -> None:
        self._t = transport
        self._svc = service_sid
        self._user = user_sid

    def _root(self, *tail: str) -> str:
        return _service_root(
            self._svc, "Users", self._user, "Conversations", *tail
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceUserConversationList:
        return ConversationsV1ServiceUserConversationList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )


class _AsyncServiceUserContext:
    def __init__(
        self, transport: object, service_sid: str, user_sid: str
    ) -> None:
        self.conversations = _AsyncConversationsV1ServiceUserConversationsResource(
            transport, service_sid, user_sid
        )


class _AsyncConversationsV1ServiceUsersCallable:
    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def __call__(self, user_sid: str) -> _AsyncServiceUserContext:
        return _AsyncServiceUserContext(self._t, self._svc, user_sid)

    def _root(self, *tail: str) -> str:
        return _service_root(self._svc, "Users", *tail)

    async def create(
        self,
        *,
        identity: str,
        friendly_name: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
    ) -> ConversationsV1ServiceUser:
        body = CreateConversationsV1ServiceUserRequest(
            identity=identity,
            friendly_name=friendly_name,
            attributes=attributes,
            role_sid=role_sid,
        ).to_form()
        return ConversationsV1ServiceUser.model_validate(
            await self._t.request("POST", self._root(), data=body)
        )

    async def list(
        self, *, page_size: int | None = None
    ) -> ConversationsV1ServiceUserList:
        return ConversationsV1ServiceUserList.model_validate(
            await self._t.request(
                "GET", self._root(), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> ConversationsV1ServiceUser:
        return ConversationsV1ServiceUser.model_validate(
            await self._t.request("GET", self._root(sid))
        )

    async def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        attributes: str | None = None,
        role_sid: str | None = None,
    ) -> ConversationsV1ServiceUser:
        body = UpdateConversationsV1ServiceUserRequest(
            friendly_name=friendly_name,
            attributes=attributes,
            role_sid=role_sid,
        ).to_form()
        return ConversationsV1ServiceUser.model_validate(
            await self._t.request("POST", self._root(sid), data=body)
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", self._root(sid))


class _AsyncConversationsV1ServiceBindingsResource:
    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _root(self, *tail: str) -> str:
        return _service_root(self._svc, "Bindings", *tail)

    async def list(
        self,
        *,
        binding_type: str | None = None,
        identity: str | None = None,
        page_size: int | None = None,
    ) -> ConversationsV1ServiceBindingList:
        return ConversationsV1ServiceBindingList.model_validate(
            await self._t.request(
                "GET",
                self._root(),
                params={
                    "BindingType": binding_type,
                    "Identity": identity,
                    "PageSize": page_size,
                },
            )
        )

    async def fetch(self, sid: str) -> ConversationsV1ServiceBinding:
        return ConversationsV1ServiceBinding.model_validate(
            await self._t.request("GET", self._root(sid))
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", self._root(sid))


class _AsyncConversationsV1ServiceNotificationsResource:
    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _path(self) -> str:
        return _service_root(self._svc, "Configuration", "Notifications")

    async def fetch(self) -> ConversationsV1ServiceNotification:
        return ConversationsV1ServiceNotification.model_validate(
            await self._t.request("GET", self._path())
        )

    async def update(
        self,
        *,
        log_enabled: bool | None = None,
        new_message_enabled: bool | None = None,
        new_message_template: str | None = None,
        new_message_sound: str | None = None,
        new_message_badge_count_enabled: bool | None = None,
        new_message_with_media_enabled: bool | None = None,
        new_message_with_media_template: str | None = None,
        added_to_conversation_enabled: bool | None = None,
        added_to_conversation_template: str | None = None,
        added_to_conversation_sound: str | None = None,
        removed_from_conversation_enabled: bool | None = None,
        removed_from_conversation_template: str | None = None,
        removed_from_conversation_sound: str | None = None,
    ) -> ConversationsV1ServiceNotification:
        body = UpdateConversationsV1ServiceNotificationRequest(
            log_enabled=log_enabled,
            new_message_enabled=new_message_enabled,
            new_message_template=new_message_template,
            new_message_sound=new_message_sound,
            new_message_badge_count_enabled=new_message_badge_count_enabled,
            new_message_with_media_enabled=new_message_with_media_enabled,
            new_message_with_media_template=new_message_with_media_template,
            added_to_conversation_enabled=added_to_conversation_enabled,
            added_to_conversation_template=added_to_conversation_template,
            added_to_conversation_sound=added_to_conversation_sound,
            removed_from_conversation_enabled=removed_from_conversation_enabled,
            removed_from_conversation_template=removed_from_conversation_template,
            removed_from_conversation_sound=removed_from_conversation_sound,
        ).to_form()
        return ConversationsV1ServiceNotification.model_validate(
            await self._t.request("POST", self._path(), data=body)
        )


class _AsyncConversationsV1ServiceWebhookConfigurationResource:
    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _path(self) -> str:
        return _service_root(self._svc, "Configuration", "Webhooks")

    async def fetch(self) -> ConversationsV1ServiceWebhookConfiguration:
        return ConversationsV1ServiceWebhookConfiguration.model_validate(
            await self._t.request("GET", self._path())
        )

    async def update(
        self,
        *,
        pre_webhook_url: str | None = None,
        post_webhook_url: str | None = None,
        method: str | None = None,
        filters: Sequence[str] | None = None,
    ) -> ConversationsV1ServiceWebhookConfiguration:
        body = UpdateConversationsV1ServiceWebhookConfigurationRequest(
            pre_webhook_url=pre_webhook_url,
            post_webhook_url=post_webhook_url,
            method=method,
            filters=list(filters) if filters is not None else None,
        ).to_form()
        return ConversationsV1ServiceWebhookConfiguration.model_validate(
            await self._t.request("POST", self._path(), data=body)
        )


class _AsyncConversationsV1ServiceConfigurationResource:
    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid
        self.notifications = _AsyncConversationsV1ServiceNotificationsResource(
            transport, service_sid
        )
        self.webhooks = _AsyncConversationsV1ServiceWebhookConfigurationResource(
            transport, service_sid
        )

    def _path(self) -> str:
        return _service_root(self._svc, "Configuration")

    async def fetch(self) -> ConversationsV1ServiceConfiguration:
        return ConversationsV1ServiceConfiguration.model_validate(
            await self._t.request("GET", self._path())
        )

    async def update(
        self,
        *,
        default_chat_service_role_sid: str | None = None,
        default_conversation_creator_role_sid: str | None = None,
        default_conversation_role_sid: str | None = None,
        reachability_enabled: bool | None = None,
    ) -> ConversationsV1ServiceConfiguration:
        body = UpdateConversationsV1ServiceConfigurationRequest(
            default_chat_service_role_sid=default_chat_service_role_sid,
            default_conversation_creator_role_sid=default_conversation_creator_role_sid,
            default_conversation_role_sid=default_conversation_role_sid,
            reachability_enabled=reachability_enabled,
        ).to_form()
        return ConversationsV1ServiceConfiguration.model_validate(
            await self._t.request("POST", self._path(), data=body)
        )


class _AsyncConversationsV1ServiceParticipantConversationsResource:
    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _path(self) -> str:
        return _service_root(self._svc, "ParticipantConversations")

    async def list(
        self,
        *,
        identity: str | None = None,
        address: str | None = None,
        page_size: int | None = None,
    ) -> ConversationsV1ServiceParticipantConversationList:
        return ConversationsV1ServiceParticipantConversationList.model_validate(
            await self._t.request(
                "GET",
                self._path(),
                params={
                    "Identity": identity,
                    "Address": address,
                    "PageSize": page_size,
                },
            )
        )


class _AsyncConversationsV1ServiceConversationWithParticipantsResource:
    def __init__(self, transport: object, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def _path(self) -> str:
        return _service_root(self._svc, "ConversationWithParticipants")

    async def create(
        self,
        *,
        friendly_name: str | None = None,
        unique_name: str | None = None,
        messaging_service_sid: str | None = None,
        attributes: str | None = None,
        state: str | None = None,
        timers_inactive: str | None = None,
        timers_closed: str | None = None,
        participant: Sequence[str] | None = None,
    ) -> ConversationsV1ServiceConversationWithParticipants:
        body = CreateConversationsV1ServiceConversationWithParticipantsRequest(
            friendly_name=friendly_name,
            unique_name=unique_name,
            messaging_service_sid=messaging_service_sid,
            attributes=attributes,
            state=state,
            timers_inactive=timers_inactive,
            timers_closed=timers_closed,
            participant=list(participant) if participant is not None else None,
        ).to_form()
        return ConversationsV1ServiceConversationWithParticipants.model_validate(
            await self._t.request("POST", self._path(), data=body)
        )


class _AsyncConversationsV1ServiceScopeResource:
    """Per-service Conversations v1 surface (async)."""

    def __init__(self, transport: object, chat_service_sid: str) -> None:
        self._t = transport
        self._svc = chat_service_sid
        self.conversations = _AsyncConversationsV1ServiceConversationsCallable(
            transport, chat_service_sid
        )
        self.roles = _AsyncConversationsV1ServiceRolesResource(
            transport, chat_service_sid
        )
        self.users = _AsyncConversationsV1ServiceUsersCallable(
            transport, chat_service_sid
        )
        self.bindings = _AsyncConversationsV1ServiceBindingsResource(
            transport, chat_service_sid
        )
        self.configuration = _AsyncConversationsV1ServiceConfigurationResource(
            transport, chat_service_sid
        )
        self.participant_conversations = (
            _AsyncConversationsV1ServiceParticipantConversationsResource(
                transport, chat_service_sid
            )
        )
        self.conversation_with_participants = (
            _AsyncConversationsV1ServiceConversationWithParticipantsResource(
                transport, chat_service_sid
            )
        )
