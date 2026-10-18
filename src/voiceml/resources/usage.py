"""``/Usage/Records`` and its time-window variants (``AllTime``, ``Daily``, …)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import date

from ..models import UsageRecord, UsageRecordList
from ..models.usage import UsageCategory
from ._base import AsyncResource, Resource

DateFilter = str | date


class UsageRecordsResource(Resource):
    """``client.usage_records``."""

    def _records(
        self,
        window: str | None,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        parts = ("Usage", "Records") if window is None else ("Usage", "Records", window)
        return UsageRecordList.model_validate(
            self._t.request(
                "GET",
                self._path(*parts),
                params={
                    "Category": category,
                    "StartDate": start_date,
                    "EndDate": end_date,
                    "IncludeSubaccounts": include_subaccounts,
                    "Page": page,
                    "PageSize": page_size,
                    "PageToken": page_token,
                },
            )
        )

    def list(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records`` — usage per category over the requested range.

        ``date`` values for ``start_date`` / ``end_date`` are sent as ``YYYY-MM-DD``.
        """
        return self._records(
            None,
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    def list_all_time(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/AllTime`` — all time."""
        return self._records(
            "AllTime",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    def list_daily(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/Daily`` — one record per day."""
        return self._records(
            "Daily",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    def list_last_month(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/LastMonth`` — last month."""
        return self._records(
            "LastMonth",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    def list_monthly(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/Monthly`` — one record per month."""
        return self._records(
            "Monthly",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    def list_this_month(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/ThisMonth`` — this month."""
        return self._records(
            "ThisMonth",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    def list_today(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/Today`` — today."""
        return self._records(
            "Today",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    def list_yearly(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/Yearly`` — one record per year."""
        return self._records(
            "Yearly",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    def list_yesterday(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/Yesterday`` — yesterday."""
        return self._records(
            "Yesterday",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    def iter(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page_size: int | None = None,
    ) -> Iterator[UsageRecord]:
        """Lazily yield ``/Usage/Records`` entries, following ``next_page_uri``."""
        yield from self._paginate(
            self.list(
                category=category,
                start_date=start_date,
                end_date=end_date,
                include_subaccounts=include_subaccounts,
                page_size=page_size,
            )
        )


class UsageRecordsAsyncResource(AsyncResource):
    """Async counterpart to :class:`UsageRecordsResource`."""

    async def _records(
        self,
        window: str | None,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        parts = ("Usage", "Records") if window is None else ("Usage", "Records", window)
        return UsageRecordList.model_validate(
            await self._t.request(
                "GET",
                self._path(*parts),
                params={
                    "Category": category,
                    "StartDate": start_date,
                    "EndDate": end_date,
                    "IncludeSubaccounts": include_subaccounts,
                    "Page": page,
                    "PageSize": page_size,
                    "PageToken": page_token,
                },
            )
        )

    async def list(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records`` — usage per category over the requested range.

        ``date`` values for ``start_date`` / ``end_date`` are sent as ``YYYY-MM-DD``.
        """
        return await self._records(
            None,
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    async def list_all_time(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/AllTime`` — all time."""
        return await self._records(
            "AllTime",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    async def list_daily(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/Daily`` — one record per day."""
        return await self._records(
            "Daily",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    async def list_last_month(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/LastMonth`` — last month."""
        return await self._records(
            "LastMonth",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    async def list_monthly(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/Monthly`` — one record per month."""
        return await self._records(
            "Monthly",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    async def list_this_month(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/ThisMonth`` — this month."""
        return await self._records(
            "ThisMonth",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    async def list_today(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/Today`` — today."""
        return await self._records(
            "Today",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    async def list_yearly(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/Yearly`` — one record per year."""
        return await self._records(
            "Yearly",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    async def list_yesterday(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> UsageRecordList:
        """``GET /Usage/Records/Yesterday`` — yesterday."""
        return await self._records(
            "Yesterday",
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page=page,
            page_size=page_size,
            page_token=page_token,
        )

    async def iter(
        self,
        *,
        category: UsageCategory | str | None = None,
        start_date: DateFilter | None = None,
        end_date: DateFilter | None = None,
        include_subaccounts: bool | None = None,
        page_size: int | None = None,
    ) -> AsyncIterator[UsageRecord]:
        """Lazily yield ``/Usage/Records`` entries, following ``next_page_uri``."""
        first = await self.list(
            category=category,
            start_date=start_date,
            end_date=end_date,
            include_subaccounts=include_subaccounts,
            page_size=page_size,
        )
        async for item in self._paginate(first):
            yield item
