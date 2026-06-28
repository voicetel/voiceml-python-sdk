"""Message resource — the Twilio-compatible ``/Messages`` REST surface.

VoiceML's outbound SMS today is fire-and-forget through the SDK 2.2 gateway —
``status`` pins to ``"sent"`` on successful dispatch and ``"failed"`` otherwise.
There is no in-flight ``queued``/``sending``/``delivered`` lifecycle. Inbound
delivery webhooks are not surfaced through this resource yet.

Two wire shapes deserve a note:

- ``num_segments`` and ``num_media`` are **strings** on the wire (Twilio-
  compatible) — not integers. ``num_media`` is always ``"0"`` because the
  gateway has no MMS support today.
- ``error_code`` is nullable integer; ``error_message`` / ``price`` /
  ``price_unit`` / ``date_sent`` / ``messaging_service_sid`` are nullable
  strings.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import Page

MessageStatus = Literal[
    "queued",
    "sending",
    "sent",
    "failed",
    "delivered",
    "undelivered",
    "receiving",
    "received",
    "accepted",
    "scheduled",
    "read",
    "canceled",
]
MessageDirection = Literal[
    "outbound-api",
    "outbound-call",
    "outbound-reply",
    "inbound",
]
UpdateMessageStatus = Literal["canceled"]


class Message(_Base):
    """A Twilio-compatible Message resource."""

    sid: str
    account_sid: str
    api_version: str
    to: str
    from_: str | None = Field(default=None, alias="from")
    body: str
    status: MessageStatus
    num_segments: str
    num_media: str
    direction: MessageDirection
    price: str | None = None
    price_unit: str | None = None
    error_code: int | None = None
    error_message: str | None = None
    messaging_service_sid: str | None = None
    date_created: str
    date_updated: str
    date_sent: str | None = None
    uri: str
    subresource_uris: dict[str, str] | None = None


class MessageList(Page[Message]):
    messages: list[Message] = Field(default_factory=list)


class CreateMessageRequest(_Base):
    """Body for ``POST /Messages``. Sent form-encoded.

    ``To`` and ``Body`` are required. ``From`` falls back to the tenant's
    configured default sender when omitted.
    """

    to: str = Field(alias="To")
    body: str = Field(alias="Body")
    from_: str | None = Field(default=None, alias="From")
    messaging_service_sid: str | None = Field(
        default=None, alias="MessagingServiceSid"
    )
    status_callback: str | None = Field(default=None, alias="StatusCallback")


class UpdateMessageRequest(_Base):
    """Body for ``POST /Messages/{Sid}``.

    Only ``Body=""`` (redaction) is honoured by the server today;
    ``Status=canceled`` returns 21610 because VoiceML's SMS gateway is
    fire-and-forget.
    """

    body: str | None = Field(default=None, alias="Body")
    status: UpdateMessageStatus | None = Field(default=None, alias="Status")
