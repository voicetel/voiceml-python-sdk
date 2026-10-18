"""Queue + queue-member resources."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request
from .common import Page


class Queue(_Base):
    sid: str | None = None
    account_sid: str | None = None
    friendly_name: str | None = None
    current_size: int
    max_size: int
    average_wait_time: int
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None


class QueueList(Page[Queue]):
    queues: list[Queue] = Field(default_factory=list)


class QueueMember(_Base):
    """A call waiting in a queue. ``account_sid`` is deprecated (no longer emitted)."""

    call_sid: str | None = None
    queue_sid: str | None = None
    account_sid: str | None = None
    date_enqueued: str | None = None
    wait_time: int
    position: int
    uri: str | None = None


class QueueMemberList(Page[QueueMember]):
    queue_members: list[QueueMember] = Field(default_factory=list)


class CreateQueueRequest(_Request):
    """Body for ``POST /Queues``. Idempotent on ``FriendlyName``."""

    friendly_name: str = Field(alias="FriendlyName", max_length=64)
    max_size: int | None = Field(default=None, alias="MaxSize", ge=0)


class UpdateQueueRequest(_Request):
    """Body for ``POST /Queues/{sid}``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName", max_length=64)
    max_size: int | None = Field(default=None, alias="MaxSize", ge=0)


class DequeueRequest(_Request):
    """Body for ``POST /Queues/{sid}/Members/Front`` and ``/Members/{CallSid}``."""

    url: str = Field(alias="Url")
    method: Literal["GET", "POST"] | None = Field(default=None, alias="Method")
