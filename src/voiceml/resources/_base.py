from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, TypeVar
from urllib.parse import quote, urlsplit

from .._http import AsyncTransport, Transport, _ScopedTransport, origin_of
from ..exceptions import PaginationError
from ..models.common import ListResponse

ItemT = TypeVar("ItemT")
PageT = TypeVar("PageT", bound=ListResponse[Any])


def seg(value: str | int) -> str:
    """Percent-encode one caller-supplied path segment.

    Keeps only the RFC 3986 unreserved set (``A-Z a-z 0-9 - . _ ~``); everything else
    is encoded as UTF-8 ``%XX`` — ``+`` → ``%2B``, space → ``%20``, ``/`` → ``%2F``,
    ``?`` → ``%3F``, ``#`` → ``%23``, ``%`` → ``%25``. A sid can therefore never
    escape its segment or inject a query string.
    """
    return quote(str(value), safe="-._~")


def path(*parts: str | int) -> str:
    """Join already-literal and caller-supplied segments into ``/a/b/c``, encoding each."""
    return "/" + "/".join(seg(p) for p in parts)


def account_path(acct: str, *parts: str | int, suffix: str = ".json") -> str:
    """Build ``/2010-04-01/Accounts/{acct}/<parts…>{suffix}``.

    Every JSON route in the ``/2010-04-01`` namespace ends in ``.json``; the suffix is
    appended to the route regardless of what the last segment contains (so
    ``Recordings/Twilio.CURRENT`` becomes ``Recordings/Twilio.CURRENT.json``). Binary
    routes pass their own suffix (``.wav``) or ``suffix=""`` (``Exports/{Date}``).
    """
    return path("2010-04-01", "Accounts", acct, *parts) + suffix


def next_page_url(page: ListResponse[Any], product_base_url: str) -> str | None:
    """Return the absolute URL of the page after ``page``, or ``None`` at the end.

    * ``/2010-04-01`` lists: ``next_page_uri`` (path + query) is followed verbatim,
      resolved against the scheme and host of the product host that served the page.
    * ``/v1`` lists: ``meta.next_page_url`` is absolute; it is followed only when its
      scheme and host equal the product host, otherwise :class:`PaginationError`.
    """
    link = page.next_link()
    if not link:
        return None
    parts = urlsplit(product_base_url)
    if link.startswith("/"):
        return f"{parts.scheme}://{parts.netloc}{link}"
    if origin_of(link) != origin_of(product_base_url):
        raise PaginationError(
            f"refusing to follow next page link to a different origin: {link!r} "
            f"(configured host {parts.scheme}://{parts.netloc})"
        )
    return link


class Resource:
    """Base class for sync resources: holds the transport + path/pagination helpers."""

    _t: Transport | _ScopedTransport

    def __init__(self, transport: Transport | _ScopedTransport) -> None:
        self._t = transport

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"

    @property
    def _acct(self) -> str:
        return self._t.account_sid

    def _path(self, *parts: str | int) -> str:
        """``/2010-04-01/Accounts/{AccountSid}/<parts…>.json`` with every segment encoded."""
        return account_path(self._acct, *parts)

    def next_page(self, page: PageT) -> PageT | None:
        """Fetch the page after ``page`` (``None`` when ``page`` is the last one)."""
        url = next_page_url(page, self._t.base_url)
        if url is None:
            return None
        return type(page).model_validate(self._t.request("GET", url))

    def _paginate(self, first: ListResponse[ItemT]) -> Iterator[ItemT]:
        page: ListResponse[ItemT] | None = first
        while page is not None:
            yield from page.items
            page = self.next_page(page)


class AsyncResource:
    """Base class for async resources: holds the transport + path/pagination helpers."""

    _t: AsyncTransport | _ScopedTransport

    def __init__(self, transport: AsyncTransport | _ScopedTransport) -> None:
        self._t = transport

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"

    @property
    def _acct(self) -> str:
        return self._t.account_sid

    def _path(self, *parts: str | int) -> str:
        return account_path(self._acct, *parts)

    async def next_page(self, page: PageT) -> PageT | None:
        """Fetch the page after ``page`` (``None`` when ``page`` is the last one)."""
        url = next_page_url(page, self._t.base_url)
        if url is None:
            return None
        return type(page).model_validate(await self._t.request("GET", url))

    async def _paginate(self, first: ListResponse[ItemT]) -> AsyncIterator[ItemT]:
        page: ListResponse[ItemT] | None = first
        while page is not None:
            for item in page.items:
                yield item
            page = await self.next_page(page)
