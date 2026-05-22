"""``/Queues`` and ``/Queues/{sid}/Members``."""

from __future__ import annotations

from ..models import (
    CreateQueueRequest,
    DequeueRequest,
    Queue,
    QueueList,
    QueueMember,
    QueueMemberList,
    UpdateQueueRequest,
)
from ._base import AsyncResource, Resource


def _page_params(
    *, page: int | None, page_size: int | None, page_token: str | None
) -> dict[str, object]:
    return {"Page": page, "PageSize": page_size, "PageToken": page_token}


class QueuesResource(Resource):
    def create(self, body: CreateQueueRequest) -> Queue:
        return Queue.model_validate(
            self._t.request("POST", self._path("Queues"), data=body.to_form())
        )

    def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> QueueList:
        return QueueList.model_validate(
            self._t.request(
                "GET",
                self._path("Queues"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    def get(self, queue_sid: str) -> Queue:
        return Queue.model_validate(
            self._t.request("GET", self._path("Queues", queue_sid))
        )

    def update(self, queue_sid: str, body: UpdateQueueRequest) -> Queue:
        return Queue.model_validate(
            self._t.request(
                "POST", self._path("Queues", queue_sid), data=body.to_form()
            )
        )

    def delete(self, queue_sid: str) -> None:
        self._t.request("DELETE", self._path("Queues", queue_sid))

    # --- Members ---

    def list_members(
        self,
        queue_sid: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> QueueMemberList:
        return QueueMemberList.model_validate(
            self._t.request(
                "GET",
                self._path("Queues", queue_sid, "Members"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    def peek_front(self, queue_sid: str) -> QueueMember:
        return QueueMember.model_validate(
            self._t.request("GET", self._path("Queues", queue_sid, "Members", "Front"))
        )

    def dequeue_front(self, queue_sid: str, body: DequeueRequest) -> QueueMember:
        return QueueMember.model_validate(
            self._t.request(
                "POST",
                self._path("Queues", queue_sid, "Members", "Front"),
                data=body.to_form(),
            )
        )

    def get_member(self, queue_sid: str, call_sid: str) -> QueueMember:
        return QueueMember.model_validate(
            self._t.request("GET", self._path("Queues", queue_sid, "Members", call_sid))
        )

    def dequeue_member(
        self, queue_sid: str, call_sid: str, body: DequeueRequest
    ) -> QueueMember:
        return QueueMember.model_validate(
            self._t.request(
                "POST",
                self._path("Queues", queue_sid, "Members", call_sid),
                data=body.to_form(),
            )
        )


class QueuesAsyncResource(AsyncResource):
    async def create(self, body: CreateQueueRequest) -> Queue:
        return Queue.model_validate(
            await self._t.request("POST", self._path("Queues"), data=body.to_form())
        )

    async def list(
        self,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> QueueList:
        return QueueList.model_validate(
            await self._t.request(
                "GET",
                self._path("Queues"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def get(self, queue_sid: str) -> Queue:
        return Queue.model_validate(
            await self._t.request("GET", self._path("Queues", queue_sid))
        )

    async def update(self, queue_sid: str, body: UpdateQueueRequest) -> Queue:
        return Queue.model_validate(
            await self._t.request(
                "POST", self._path("Queues", queue_sid), data=body.to_form()
            )
        )

    async def delete(self, queue_sid: str) -> None:
        await self._t.request("DELETE", self._path("Queues", queue_sid))

    async def list_members(
        self,
        queue_sid: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> QueueMemberList:
        return QueueMemberList.model_validate(
            await self._t.request(
                "GET",
                self._path("Queues", queue_sid, "Members"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def peek_front(self, queue_sid: str) -> QueueMember:
        return QueueMember.model_validate(
            await self._t.request(
                "GET", self._path("Queues", queue_sid, "Members", "Front")
            )
        )

    async def dequeue_front(self, queue_sid: str, body: DequeueRequest) -> QueueMember:
        return QueueMember.model_validate(
            await self._t.request(
                "POST",
                self._path("Queues", queue_sid, "Members", "Front"),
                data=body.to_form(),
            )
        )

    async def get_member(self, queue_sid: str, call_sid: str) -> QueueMember:
        return QueueMember.model_validate(
            await self._t.request(
                "GET", self._path("Queues", queue_sid, "Members", call_sid)
            )
        )

    async def dequeue_member(
        self, queue_sid: str, call_sid: str, body: DequeueRequest
    ) -> QueueMember:
        return QueueMember.model_validate(
            await self._t.request(
                "POST",
                self._path("Queues", queue_sid, "Members", call_sid),
                data=body.to_form(),
            )
        )
