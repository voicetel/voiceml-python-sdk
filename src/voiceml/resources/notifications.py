"""Account-scoped ``/Notifications`` — compat stubs (always empty list, fetch returns 404)."""

from __future__ import annotations

from typing import Any

from ..models import NotificationsList
from ._base import AsyncResource, Resource


def _list_params(
    *,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
    log: int | None,
    message_date: str | None,
    message_date_lt: str | None,
    message_date_gt: str | None,
) -> dict[str, object]:
    return {
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
        "Log": log,
        "MessageDate": message_date,
        "MessageDate<": message_date_lt,
        "MessageDate>": message_date_gt,
    }


class NotificationsResource(Resource):
    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        log: int | None = None,
        message_date: str | None = None,
        message_date_lt: str | None = None,
        message_date_gt: str | None = None,
    ) -> NotificationsList:
        return NotificationsList.model_validate(
            self._t.request(
                "GET",
                self._path("Notifications"),
                params=_list_params(
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                    log=log,
                    message_date=message_date,
                    message_date_lt=message_date_lt,
                    message_date_gt=message_date_gt,
                ),
            )
        )

    def get(self, notification_sid: str) -> dict[str, Any]:
        result = self._t.request("GET", self._path("Notifications", notification_sid))
        if not isinstance(result, dict):
            raise TypeError("expected JSON object from Notifications.get")
        return result


class NotificationsAsyncResource(AsyncResource):
    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        log: int | None = None,
        message_date: str | None = None,
        message_date_lt: str | None = None,
        message_date_gt: str | None = None,
    ) -> NotificationsList:
        return NotificationsList.model_validate(
            await self._t.request(
                "GET",
                self._path("Notifications"),
                params=_list_params(
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                    log=log,
                    message_date=message_date,
                    message_date_lt=message_date_lt,
                    message_date_gt=message_date_gt,
                ),
            )
        )

    async def get(self, notification_sid: str) -> dict[str, Any]:
        result = await self._t.request(
            "GET", self._path("Notifications", notification_sid)
        )
        if not isinstance(result, dict):
            raise TypeError("expected JSON object from Notifications.get")
        return result
