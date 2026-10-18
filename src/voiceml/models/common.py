"""Pagination envelopes and error shape — shared building blocks across resources."""

from __future__ import annotations

import typing
from typing import Any, ClassVar, Generic, Literal, TypeVar

from ._base import _Base

T = TypeVar("T")

#: Which configured host serves a list resource (used to resolve next-page links).
Product = Literal["default", "messaging", "conversations"]

_ENVELOPE_FIELDS = frozenset(
    {
        "page",
        "page_size",
        "start",
        "end",
        "uri",
        "first_page_uri",
        "next_page_uri",
        "previous_page_uri",
        "meta",
    }
)


class ListResponse(_Base, Generic[T]):
    """Common behaviour of every list envelope.

    Subclasses declare exactly one list field named after the resource (``calls``,
    ``conferences``, ``roles``…); :attr:`items` returns it generically so pagination
    helpers can walk any list type.
    """

    product: ClassVar[Product] = "default"
    items_field: ClassVar[str] = ""

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        candidates = [
            name
            for name, info in cls.model_fields.items()
            if name not in _ENVELOPE_FIELDS and typing.get_origin(info.annotation) is list
        ]
        if len(candidates) == 1:
            cls.items_field = candidates[0]

    @property
    def items(self) -> list[T]:
        """The resources on this page, whatever the wire key is called."""
        if not self.items_field:
            return []
        value: list[T] = getattr(self, self.items_field)
        return value

    def next_link(self) -> str | None:
        """The raw next-page link from the envelope (relative or absolute), if any."""
        raise NotImplementedError


class Page(ListResponse[T], Generic[T]):
    """``/2010-04-01`` pagination envelope.

    Field names match the wire shape exactly. Subclasses bind the concrete resource
    list (``calls``, ``conferences``, ``recordings``…)::

        class CallList(Page[Call]):
            calls: list[Call] = Field(default_factory=list)

    ``next_page_uri`` is a relative link (path + query, carrying the server's
    ``PageToken``); the SDK follows it verbatim — see ``Client.next_page``.
    """

    page: int | None = None
    page_size: int | None = None
    start: int | None = None
    end: int | None = None
    uri: str | None = None
    first_page_uri: str | None = None
    next_page_uri: str | None = None
    previous_page_uri: str | None = None

    def next_link(self) -> str | None:
        return self.next_page_uri or None


class VoiceV1Meta(_Base):
    """``/v1`` list envelope (Voice, Conversations, Messaging, Assistants, Pricing).

    ``next_page_url`` is absolute; the SDK only follows it when it points at the
    configured product host.
    """

    first_page_url: str | None = None
    next_page_url: str | None = None
    previous_page_url: str | None = None
    url: str | None = None
    page: int | None = None
    page_size: int | None = None
    key: str | None = None


class V1Page(ListResponse[T], Generic[T]):
    """``/v1`` list envelope: a resource-named list plus ``meta``."""

    meta: VoiceV1Meta | None = None

    def next_link(self) -> str | None:
        if self.meta is None:
            return None
        return self.meta.next_page_url or None


class ErrorBody(_Base):
    """Twilio-compatible error body — what the server returns for non-2xx responses.

    Surface only — the transport raises :class:`voiceml.ApiError` (or a subclass) with
    this payload attached as ``error.body``. ``code`` is the numeric error code
    (e.g. 21211).
    """

    code: int | None = None
    message: str | None = None
    more_info: str | None = None
    status: int | None = None


class HealthFailure(_Base):
    """One tripped check from the ``/health`` deep probe."""

    check: str | None = None
    detail: str | None = None


__all__ = [
    "ErrorBody",
    "HealthFailure",
    "ListResponse",
    "Page",
    "Product",
    "V1Page",
    "VoiceV1Meta",
]
