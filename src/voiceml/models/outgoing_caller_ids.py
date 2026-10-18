"""Outgoing caller IDs — verified numbers usable as ``From`` / ``CallerId``."""

from __future__ import annotations

from pydantic import Field

from ._base import _Base, _Request
from .common import Page


class OutgoingCallerId(_Base):
    """A verified caller ID (``PN…``)."""

    sid: str | None = None
    account_sid: str | None = None
    friendly_name: str | None = None
    phone_number: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None


class OutgoingCallerIdList(Page[OutgoingCallerId]):
    outgoing_caller_ids: list[OutgoingCallerId] = Field(default_factory=list)


class ValidationRequest(_Base):
    """Returned by ``POST /OutgoingCallerIds`` — the verification call in progress.

    ``validation_code`` is the code the callee must enter to verify the number.
    """

    account_sid: str | None = None
    phone_number: str | None = None
    friendly_name: str | None = None
    validation_code: str | None = None
    call_sid: str | None = None


class CreateOutgoingCallerIdRequest(_Request):
    """Body for ``POST /OutgoingCallerIds`` (starts verification)."""

    phone_number: str = Field(alias="PhoneNumber")
    friendly_name: str | None = Field(default=None, alias="FriendlyName")


class UpdateOutgoingCallerIdRequest(_Request):
    """Body for ``POST /OutgoingCallerIds/{Sid}``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
