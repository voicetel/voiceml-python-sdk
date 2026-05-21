"""Queue + queue-member resources."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import Page


class Queue(_Base):
    sid: str
    account_sid: str
    friendly_name: str
    current_size: int
    max_size: int
    average_wait_time: int
    date_created: str
    date_updated: str
    uri: str


class QueueList(Page[Queue]):
    queues: list[Queue] = Field(default_factory=list)


class QueueMember(_Base):
    call_sid: str
    queue_sid: str
    account_sid: str
    date_enqueued: str
    wait_time: int
    position: int
    uri: str


class QueueMemberList(Page[QueueMember]):
    queue_members: list[QueueMember] = Field(default_factory=list)


class CreateQueueRequest(_Base):
    """Body for ``POST /Queues``. Idempotent on ``FriendlyName``."""

    friendly_name: str = Field(alias="FriendlyName", max_length=64)
    max_size: int | None = Field(default=None, alias="MaxSize", ge=0)


class UpdateQueueRequest(_Base):
    """Body for ``POST /Queues/{sid}``."""

    friendly_name: str | None = Field(default=None, alias="FriendlyName", max_length=64)
    max_size: int | None = Field(default=None, alias="MaxSize", ge=0)


class DequeueRequest(_Base):
    """Body for ``POST /Queues/{sid}/Members/Front`` and ``/Members/{CallSid}``."""

    url: str = Field(alias="Url")
    method: Literal["GET", "POST"] | None = Field(default=None, alias="Method")
