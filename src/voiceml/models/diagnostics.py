"""Notifications, call events, and /health — read-only diagnostic surfaces."""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator

from ._base import _Base
from .common import HealthFailure, Page


class Notification(_Base):
    """An alert-log entry (``NO…``) raised when a TwiML fetch or parse fails.

    ``error_code`` / ``more_info`` follow the Twilio-compatible error dictionary
    (11200 HTTP retrieval failure, 12100 document parse failure). ``log`` is a
    numeric string (``"0"`` / ``"1"``) on the wire.
    """

    sid: str | None = None
    account_sid: str | None = None
    call_sid: str | None = None
    api_version: str | None = None
    error_code: str | None = None
    log: str | None = None
    message_date: str | None = None
    message_text: str | None = None
    more_info: str | None = None
    request_method: str | None = None
    request_url: str | None = None
    uri: str | None = None
    date_created: str | None = None
    date_updated: str | None = None


class NotificationsList(Page[Notification]):
    """``GET /Notifications`` and ``GET /Calls/{sid}/Notifications``."""

    notifications: list[Notification] = Field(default_factory=list)


class CallEventRequest(_Base):
    """The REST request half of a :class:`CallEvent`."""

    method: str | None = None
    parameters: dict[str, str] | None = None
    url: str | None = None


class CallEventResponse(_Base):
    """The response half of a :class:`CallEvent`."""

    content_type: str | None = None
    date_created: str | None = None
    request_duration: int | None = None
    response_body: str | None = None
    response_code: int | None = None


class CallEvent(_Base):
    """One REST request/response recorded against a call (create + each update)."""

    request: CallEventRequest | None = None
    response: CallEventResponse | None = None


class EventsList(Page[CallEvent]):
    """``GET /Calls/{sid}/Events`` — list-only; there is no fetch-by-id."""

    events: list[CallEvent] = Field(default_factory=list)


class HealthStatus(_Base):
    """``GET /health`` response — composite probe.

    Hard-check failures flip ``ok`` to False (server returns 503, which the SDK raises
    as :class:`voiceml.ServerError`). Soft-check warnings surface in ``warnings`` only
    and don't take the host out of rotation. Both lists are optional on the wire and
    default to empty.
    """

    ok: bool
    warnings: list[HealthFailure] = Field(default_factory=list)
    failures: list[HealthFailure] = Field(default_factory=list)

    @field_validator("warnings", "failures", mode="before")
    @classmethod
    def _none_is_empty(cls, value: Any) -> Any:
        return [] if value is None else value
