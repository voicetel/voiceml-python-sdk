"""``/OutgoingCallerIds`` — verified caller IDs."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from ..models import (
    CreateOutgoingCallerIdRequest,
    OutgoingCallerId,
    OutgoingCallerIdList,
    UpdateOutgoingCallerIdRequest,
    ValidationRequest,
)
from ._base import AsyncResource, Resource


def _list_params(
    *,
    phone_number: str | None,
    friendly_name: str | None,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
) -> dict[str, object]:
    return {
        "PhoneNumber": phone_number,
        "FriendlyName": friendly_name,
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
    }


class OutgoingCallerIdsResource(Resource):
    """``client.outgoing_caller_ids``."""

    def list(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> OutgoingCallerIdList:
        return OutgoingCallerIdList.model_validate(
            self._t.request(
                "GET",
                self._path("OutgoingCallerIds"),
                params=_list_params(
                    phone_number=phone_number,
                    friendly_name=friendly_name,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def iter(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        page_size: int | None = None,
    ) -> Iterator[OutgoingCallerId]:
        """Lazily yield caller IDs, following ``next_page_uri`` page by page."""
        yield from self._paginate(
            self.list(phone_number=phone_number, friendly_name=friendly_name, page_size=page_size)
        )

    def create(self, *, phone_number: str, friendly_name: str | None = None) -> ValidationRequest:
        """Start verifying ``phone_number``; returns the validation code to enter."""
        form = CreateOutgoingCallerIdRequest(
            phone_number=phone_number, friendly_name=friendly_name
        ).to_form()
        return ValidationRequest.model_validate(
            self._t.request("POST", self._path("OutgoingCallerIds"), data=form)
        )

    def get(self, sid: str) -> OutgoingCallerId:
        return OutgoingCallerId.model_validate(
            self._t.request("GET", self._path("OutgoingCallerIds", sid))
        )

    def update(self, sid: str, *, friendly_name: str | None = None) -> OutgoingCallerId:
        form = UpdateOutgoingCallerIdRequest(friendly_name=friendly_name).to_form()
        return OutgoingCallerId.model_validate(
            self._t.request("POST", self._path("OutgoingCallerIds", sid), data=form)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", self._path("OutgoingCallerIds", sid))


class OutgoingCallerIdsAsyncResource(AsyncResource):
    """Async counterpart to :class:`OutgoingCallerIdsResource`."""

    async def list(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> OutgoingCallerIdList:
        return OutgoingCallerIdList.model_validate(
            await self._t.request(
                "GET",
                self._path("OutgoingCallerIds"),
                params=_list_params(
                    phone_number=phone_number,
                    friendly_name=friendly_name,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def iter(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        page_size: int | None = None,
    ) -> AsyncIterator[OutgoingCallerId]:
        """Lazily yield caller IDs, following ``next_page_uri`` page by page."""
        first = await self.list(
            phone_number=phone_number, friendly_name=friendly_name, page_size=page_size
        )
        async for item in self._paginate(first):
            yield item

    async def create(
        self, *, phone_number: str, friendly_name: str | None = None
    ) -> ValidationRequest:
        form = CreateOutgoingCallerIdRequest(
            phone_number=phone_number, friendly_name=friendly_name
        ).to_form()
        return ValidationRequest.model_validate(
            await self._t.request("POST", self._path("OutgoingCallerIds"), data=form)
        )

    async def get(self, sid: str) -> OutgoingCallerId:
        return OutgoingCallerId.model_validate(
            await self._t.request("GET", self._path("OutgoingCallerIds", sid))
        )

    async def update(self, sid: str, *, friendly_name: str | None = None) -> OutgoingCallerId:
        form = UpdateOutgoingCallerIdRequest(friendly_name=friendly_name).to_form()
        return OutgoingCallerId.model_validate(
            await self._t.request("POST", self._path("OutgoingCallerIds", sid), data=form)
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", self._path("OutgoingCallerIds", sid))
