"""Messaging v1 resources — Twilio ``messaging.twilio.com/v1`` REST surface (#16).

A Messaging Service (``MG…``) shares the ``/v1/Services`` path shape with the
Conversations Service (``IS…``); the two are disambiguated on the wire by host
(``messaging.voicetel.com`` vs ``conversations.voicetel.com``). This SDK routes
``client.messaging_v1.*`` at the messaging host automatically — see
:mod:`voiceml._hosts`.

Only the Messaging Service has an ``update`` verb; Conversation Service does
not, so ``POST /v1/Services/{sid}`` has no path collision.
"""

from __future__ import annotations

from pydantic import Field

from ._base import _Base
from .voice_v1 import VoiceV1Meta


class MessagingService(_Base):
    """A Messaging Service — Twilio ``MG…`` resource.

    The various feature-toggle fields (``sticky_sender``, ``mms_converter``, …)
    are accept-and-echo on VoiceML; the service's operative role is gating
    scheduled sends (a real ``messaging_service_sid`` is required on
    ``POST /Messages`` when ``send_at``/``schedule_type`` is set).
    """

    sid: str | None = None
    account_sid: str | None = None
    friendly_name: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    inbound_request_url: str | None = None
    inbound_method: str | None = None
    fallback_url: str | None = None
    fallback_method: str | None = None
    status_callback: str | None = None
    sticky_sender: bool | None = None
    mms_converter: bool | None = None
    smart_encoding: bool | None = None
    scan_message_content: str | None = None
    fallback_to_long_code: bool | None = None
    area_code_geomatch: bool | None = None
    synchronous_validation: bool | None = None
    validity_period: int | None = None
    url: str | None = None
    usecase: str | None = None
    use_inbound_webhook_on_number: bool | None = None


class MessagingServiceList(_Base):
    """List envelope for ``GET /v1/Services`` on the messaging host."""

    services: list[MessagingService] = Field(default_factory=list)
    meta: VoiceV1Meta | None = None


class CreateMessagingServiceRequest(_Base):
    """Body for ``POST /v1/Services`` (messaging host). ``FriendlyName`` required."""

    friendly_name: str = Field(alias="FriendlyName")
    inbound_request_url: str | None = Field(default=None, alias="InboundRequestUrl")
    inbound_method: str | None = Field(default=None, alias="InboundMethod")
    fallback_url: str | None = Field(default=None, alias="FallbackUrl")
    fallback_method: str | None = Field(default=None, alias="FallbackMethod")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    sticky_sender: bool | None = Field(default=None, alias="StickySender")
    mms_converter: bool | None = Field(default=None, alias="MmsConverter")
    smart_encoding: bool | None = Field(default=None, alias="SmartEncoding")
    scan_message_content: str | None = Field(default=None, alias="ScanMessageContent")
    fallback_to_long_code: bool | None = Field(default=None, alias="FallbackToLongCode")
    area_code_geomatch: bool | None = Field(default=None, alias="AreaCodeGeomatch")
    synchronous_validation: bool | None = Field(
        default=None, alias="SynchronousValidation"
    )
    validity_period: int | None = Field(default=None, alias="ValidityPeriod")
    usecase: str | None = Field(default=None, alias="Usecase")
    use_inbound_webhook_on_number: bool | None = Field(
        default=None, alias="UseInboundWebhookOnNumber"
    )


class UpdateMessagingServiceRequest(_Base):
    """Body for ``POST /v1/Services/{sid}`` (messaging host). All fields optional."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    inbound_request_url: str | None = Field(default=None, alias="InboundRequestUrl")
    inbound_method: str | None = Field(default=None, alias="InboundMethod")
    fallback_url: str | None = Field(default=None, alias="FallbackUrl")
    fallback_method: str | None = Field(default=None, alias="FallbackMethod")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    sticky_sender: bool | None = Field(default=None, alias="StickySender")
    mms_converter: bool | None = Field(default=None, alias="MmsConverter")
    smart_encoding: bool | None = Field(default=None, alias="SmartEncoding")
    scan_message_content: str | None = Field(default=None, alias="ScanMessageContent")
    fallback_to_long_code: bool | None = Field(default=None, alias="FallbackToLongCode")
    area_code_geomatch: bool | None = Field(default=None, alias="AreaCodeGeomatch")
    synchronous_validation: bool | None = Field(
        default=None, alias="SynchronousValidation"
    )
    validity_period: int | None = Field(default=None, alias="ValidityPeriod")
    usecase: str | None = Field(default=None, alias="Usecase")
    use_inbound_webhook_on_number: bool | None = Field(
        default=None, alias="UseInboundWebhookOnNumber"
    )
