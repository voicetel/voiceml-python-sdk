"""Message resource — the Twilio-compatible ``/Messages`` REST surface (SMS and MMS).

Two wire shapes deserve a note:

- ``num_segments`` and ``num_media`` are **strings** on the wire (Twilio-
  compatible) — not integers.
- ``error_code`` is nullable integer; ``error_message`` / ``price`` /
  ``price_unit`` / ``date_sent`` / ``messaging_service_sid`` are nullable
  strings.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, model_validator

from ._base import _Base, _Request
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
MessageFeedbackOutcome = Literal["confirmed", "unconfirmed"]
HttpMethod = Literal["GET", "POST"]
ScheduleType = Literal["fixed"]


class Message(_Base):
    """A Twilio-compatible Message resource."""

    sid: str
    account_sid: str
    api_version: str
    to: str
    from_: str | None = Field(default=None, alias="from")
    body: str
    status: MessageStatus | str
    num_segments: str
    num_media: str
    direction: MessageDirection | str
    price: str | None = None
    price_unit: str | None = None
    error_code: int | None = None
    error_message: str | None = None
    messaging_service_sid: str | None = None
    date_created: str
    date_updated: str
    date_sent: str | None = None
    uri: str
    subresource_uris: dict[str, Any] | None = None


class MessageList(Page[Message]):
    messages: list[Message] = Field(default_factory=list)


class CreateMessageRequest(_Request):
    """Body for ``POST /Messages``. Sent form-encoded.

    ``To`` is required, plus at least one of ``Body`` or ``MediaUrl`` (MMS). ``From``
    falls back to the tenant's configured default sender when omitted. ``MediaUrl``
    is sent as repeated ``MediaUrl=`` keys.

    ``send_at`` schedules the message for a future UTC time; the server requires
    ``schedule_type`` (``"fixed"`` is the only accepted value) and
    ``messaging_service_sid`` alongside it.
    """

    to: str = Field(alias="To")
    body: str | None = Field(default=None, alias="Body")
    from_: str | None = Field(default=None, alias="From")
    media_url: list[str] | None = Field(default=None, alias="MediaUrl")
    messaging_service_sid: str | None = Field(default=None, alias="MessagingServiceSid")
    validity_period: int | None = Field(default=None, alias="ValidityPeriod", ge=1, le=36000)
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: HttpMethod | None = Field(default=None, alias="StatusCallbackMethod")
    send_at: datetime | None = Field(default=None, alias="SendAt")
    schedule_type: ScheduleType | None = Field(default=None, alias="ScheduleType")

    @model_validator(mode="after")
    def _body_or_media(self) -> CreateMessageRequest:
        if self.body is None and not self.media_url:
            raise ValueError("Body or MediaUrl is required")
        return self


class Media(_Base):
    """One media attachment of a Message (``ME…``)."""

    sid: str | None = None
    account_sid: str | None = None
    parent_sid: str | None = None
    content_type: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None


class MediaList(Page[Media]):
    """``GET /Messages/{MessageSid}/Media`` — note the wire key is ``media_list``."""

    media_list: list[Media] = Field(default_factory=list)


class MessageFeedback(_Base):
    """Delivery-quality feedback echoed back on a Message.

    VoiceML records the outcome on the response only; there is no separate
    downstream analytics surface.
    """

    account_sid: str
    message_sid: str
    outcome: MessageFeedbackOutcome | str
    date_created: str
    date_updated: str
    uri: str


class CreateMessageFeedbackRequest(_Request):
    """Body for ``POST /Messages/{Sid}/Feedback.json``.

    ``Outcome`` is optional: any value other than ``confirmed`` (including an
    omitted one) is echoed as ``unconfirmed``; feedback is not persisted.
    """

    outcome: MessageFeedbackOutcome | None = Field(default=None, alias="Outcome")


class UpdateMessageRequest(_Request):
    """Body for ``POST /Messages/{Sid}``.

    Only ``Body=""`` (redaction) is honoured by the server today;
    ``Status=canceled`` returns 21610 because VoiceML's SMS gateway is
    fire-and-forget.
    """

    body: str | None = Field(default=None, alias="Body")
    status: UpdateMessageStatus | None = Field(default=None, alias="Status")
