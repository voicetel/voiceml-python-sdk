"""Usage records (``/Usage/Records`` and its time-window variants)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from ._base import _Base
from .common import Page

UsageCategory = Literal[
    "calls",
    "calls-inbound",
    "calls-outbound",
    "mms",
    "mms-inbound",
    "mms-outbound",
    "sms",
    "sms-inbound",
    "sms-inbound-longcode",
    "sms-outbound",
    "sms-outbound-longcode",
    "totalprice",
]


class UsageRecord(_Base):
    """Usage of one category over one period. Numeric values are strings on the wire."""

    account_sid: str | None = None
    api_version: str | None = None
    as_of: str | None = None
    category: UsageCategory | str | None = None
    count: str | None = None
    count_unit: str | None = None
    description: str | None = None
    end_date: str | None = None
    price: str | None = None
    price_unit: str | None = None
    start_date: str | None = None
    subresource_uris: dict[str, Any] | None = None
    uri: str | None = None
    usage: str | None = None
    usage_unit: str | None = None


class UsageRecordList(Page[UsageRecord]):
    usage_records: list[UsageRecord] = Field(default_factory=list)
