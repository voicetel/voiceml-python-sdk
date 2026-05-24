"""Pagination envelope and error shape — shared building blocks across resources."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import Field

from ._base import _Base

T = TypeVar("T")


class Page(_Base, Generic[T]):
    """Twilio-compatible pagination envelope.

    Field names match the wire shape exactly. ``items`` is a generic alias that subclasses
    bind to the concrete resource name (``calls``, ``conferences``, ``recordings``...).

    Subclass to specialize, e.g.::

        class CallList(Page[Call]):
            calls: list[Call] = Field(default_factory=list)

    The concrete resource list field is what callers iterate; ``next_page_uri`` drives
    auto-pagination helpers.
    """

    page: int = 0
    page_size: int = Field(default=50, alias="page_size")
    num_pages: int | None = None
    total: int | None = None
    start: int | None = None
    end: int | None = None
    first_page_uri: str | None = None
    next_page_uri: str | None = None
    previous_page_uri: str | None = None
    uri: str | None = None


class ErrorBody(_Base):
    """Twilio-compatible error body — what the server returns for non-2xx responses.

    Surface only — the transport raises :class:`voiceml.ApiError` (or a subclass) with
    this payload attached as ``error.body``. Code is the numeric Twilio code (e.g. 21211).
    """

    code: int | None = None
    message: str | None = None
    more_info: str | None = None
    status: int | None = None


class HealthFailure(_Base):
    """One tripped check from the ``/health`` deep probe."""

    check: str
    detail: str
