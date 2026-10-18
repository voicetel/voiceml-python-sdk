"""``/v1/Alerts`` — the Monitor v1 Alert surface.

``client.monitor_v1.alerts`` lists and fetches failure events (call-scoped
errors and messaging delivery failures). Paths sit at ``/v1/`` (no
``/2010-04-01/Accounts/{Sid}/`` prefix); the account is resolved from HTTP
Basic auth, so the resource classes use bare path strings rather than the
:meth:`Resource._path` helper that prepends the AccountSid namespace.

The server currently answers a single page (``meta.next_page_url`` is always
``null``); ``iter()`` and ``next_page()`` follow the standard ``/v1``
envelope regardless, so they keep working if continuation ever appears.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from .._http import AsyncTransport, Transport
from ..models import MonitorV1Alert, MonitorV1AlertList
from ..models.monitor_v1 import MonitorV1LogLevel
from ._base import AsyncResource, Resource, path


def _list_params(
    *,
    log_level: MonitorV1LogLevel | None,
    start_date: str | None,
    end_date: str | None,
    page_size: int | None,
) -> dict[str, object]:
    return {
        "LogLevel": log_level,
        "StartDate": start_date,
        "EndDate": end_date,
        "PageSize": page_size,
    }


class MonitorV1AlertsResource(Resource):
    """Operations on ``/v1/Alerts`` (sync)."""

    def list(
        self,
        *,
        log_level: MonitorV1LogLevel | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page_size: int | None = None,
    ) -> MonitorV1AlertList:
        """Return a single page of alerts, optionally filtered.

        ``start_date`` / ``end_date`` take ``YYYY-MM-DD`` or a full ISO-8601
        timestamp. The server answers one page only (no continuation link).
        """
        return MonitorV1AlertList.model_validate(
            self._t.request(
                "GET",
                path("v1", "Alerts"),
                params=_list_params(
                    log_level=log_level,
                    start_date=start_date,
                    end_date=end_date,
                    page_size=page_size,
                ),
            )
        )

    def iter(
        self,
        *,
        log_level: MonitorV1LogLevel | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page_size: int | None = None,
    ) -> Iterator[MonitorV1Alert]:
        """Lazily yield alerts, following ``meta.next_page_url`` page by page.

        The server currently returns a single page, so this yields that page's
        rows and stops.
        """
        yield from self._paginate(
            self.list(
                log_level=log_level,
                start_date=start_date,
                end_date=end_date,
                page_size=page_size,
            )
        )

    def fetch(self, sid: str) -> MonitorV1Alert:
        """Fetch one alert, including any stored request/response detail."""
        return MonitorV1Alert.model_validate(self._t.request("GET", path("v1", "Alerts", sid)))


class MonitorV1Resource:
    """Holder for ``client.monitor_v1.*`` sub-resources (sync)."""

    def __init__(self, transport: Transport) -> None:
        self.alerts = MonitorV1AlertsResource(transport)


class MonitorV1AlertsAsyncResource(AsyncResource):
    """Operations on ``/v1/Alerts`` (async)."""

    async def list(
        self,
        *,
        log_level: MonitorV1LogLevel | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page_size: int | None = None,
    ) -> MonitorV1AlertList:
        return MonitorV1AlertList.model_validate(
            await self._t.request(
                "GET",
                path("v1", "Alerts"),
                params=_list_params(
                    log_level=log_level,
                    start_date=start_date,
                    end_date=end_date,
                    page_size=page_size,
                ),
            )
        )

    async def iter(
        self,
        *,
        log_level: MonitorV1LogLevel | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page_size: int | None = None,
    ) -> AsyncIterator[MonitorV1Alert]:
        """Lazily yield alerts, following ``meta.next_page_url`` page by page."""
        first = await self.list(
            log_level=log_level,
            start_date=start_date,
            end_date=end_date,
            page_size=page_size,
        )
        async for item in self._paginate(first):
            yield item

    async def fetch(self, sid: str) -> MonitorV1Alert:
        return MonitorV1Alert.model_validate(
            await self._t.request("GET", path("v1", "Alerts", sid))
        )


class MonitorV1AsyncResource:
    """Holder for ``client.monitor_v1.*`` sub-resources (async)."""

    def __init__(self, transport: AsyncTransport) -> None:
        self.alerts = MonitorV1AlertsAsyncResource(transport)
