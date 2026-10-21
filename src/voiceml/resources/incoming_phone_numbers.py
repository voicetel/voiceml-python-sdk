"""``/IncomingPhoneNumbers`` — tenant-self-serve DID assignment + voice/SMS routing.

The ``sid`` URL path param is the canonical ``PN``-prefixed identifier (e.g.
``PN0123456789abcdef0123456789abcdef``). The server accepts the legacy E.164 form
(``+14155550100``) during the transition window, but tenants are encouraged to use the
PN-sid. This SDK accepts either as the ``sid`` argument — the value is percent-encoded
(``+`` → ``%2B``) and the server resolves it to the underlying row.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from ..models import (
    CreateIncomingPhoneNumberRequest,
    CreateTypedIncomingPhoneNumberRequest,
    IncomingPhoneNumber,
    IncomingPhoneNumberList,
    UpdateIncomingPhoneNumberRequest,
)
from ..models.incoming_phone_numbers import HttpMethod, IncomingPhoneNumberOrigin
from ._base import AsyncResource, Resource


def _list_params(
    *,
    phone_number: str | None,
    friendly_name: str | None,
    beta: bool | None,
    origin: IncomingPhoneNumberOrigin | None,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
) -> dict[str, object]:
    return {
        "PhoneNumber": phone_number,
        "FriendlyName": friendly_name,
        "Beta": beta,
        "Origin": origin,
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
    }


def _create_form(
    *,
    phone_number: str,
    voice_url: str | None,
    voice_method: HttpMethod | None,
    voice_fallback_url: str | None,
    voice_fallback_method: HttpMethod | None,
    sms_url: str | None,
    sms_method: HttpMethod | None,
    sms_fallback_url: str | None,
    sms_fallback_method: HttpMethod | None,
    sms_application_sid: str | None,
    voice_application_sid: str | None,
    status_callback: str | None,
    status_callback_method: HttpMethod | None,
) -> dict[str, object]:
    return CreateIncomingPhoneNumberRequest(
        phone_number=phone_number,
        voice_url=voice_url,
        voice_method=voice_method,
        voice_fallback_url=voice_fallback_url,
        voice_fallback_method=voice_fallback_method,
        sms_url=sms_url,
        sms_method=sms_method,
        sms_fallback_url=sms_fallback_url,
        sms_fallback_method=sms_fallback_method,
        sms_application_sid=sms_application_sid,
        voice_application_sid=voice_application_sid,
        status_callback=status_callback,
        status_callback_method=status_callback_method,
    ).to_form()


def _typed_create_form(
    *, phone_number: str, voice_url: str | None, voice_method: HttpMethod | None
) -> dict[str, object]:
    return CreateTypedIncomingPhoneNumberRequest(
        phone_number=phone_number, voice_url=voice_url, voice_method=voice_method
    ).to_form()


def _update_form(
    *,
    voice_url: str | None,
    voice_method: HttpMethod | None,
    voice_fallback_url: str | None,
    voice_fallback_method: HttpMethod | None,
    sms_url: str | None,
    sms_method: HttpMethod | None,
    sms_fallback_url: str | None,
    sms_fallback_method: HttpMethod | None,
    sms_application_sid: str | None,
    voice_application_sid: str | None,
    status_callback: str | None,
    status_callback_method: HttpMethod | None,
) -> dict[str, object]:
    return UpdateIncomingPhoneNumberRequest(
        voice_url=voice_url,
        voice_method=voice_method,
        voice_fallback_url=voice_fallback_url,
        voice_fallback_method=voice_fallback_method,
        sms_url=sms_url,
        sms_method=sms_method,
        sms_fallback_url=sms_fallback_url,
        sms_fallback_method=sms_fallback_method,
        sms_application_sid=sms_application_sid,
        voice_application_sid=voice_application_sid,
        status_callback=status_callback,
        status_callback_method=status_callback_method,
    ).to_form()


class IncomingPhoneNumbersResource(Resource):
    """Sync ``IncomingPhoneNumbers`` operations."""

    def _list(self, kind: str | None, params: dict[str, object]) -> IncomingPhoneNumberList:
        parts = ("IncomingPhoneNumbers",) if kind is None else ("IncomingPhoneNumbers", kind)
        return IncomingPhoneNumberList.model_validate(
            self._t.request("GET", self._path(*parts), params=params)
        )

    def _create_typed(self, kind: str, form: dict[str, object]) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            self._t.request("POST", self._path("IncomingPhoneNumbers", kind), data=form)
        )

    def list(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: IncomingPhoneNumberOrigin | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return self._list(
            None,
            _list_params(
                phone_number=phone_number,
                friendly_name=friendly_name,
                beta=beta,
                origin=origin,
                page=page,
                page_size=page_size,
                page_token=page_token,
            ),
        )

    def iter(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: IncomingPhoneNumberOrigin | None = None,
        page_size: int | None = None,
    ) -> Iterator[IncomingPhoneNumber]:
        """Lazily yield every number, following ``next_page_uri`` page by page."""
        yield from self._paginate(
            self.list(
                phone_number=phone_number,
                friendly_name=friendly_name,
                beta=beta,
                origin=origin,
                page_size=page_size,
            )
        )

    def create(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: HttpMethod | None = None,
        sms_url: str | None = None,
        sms_method: HttpMethod | None = None,
        sms_fallback_url: str | None = None,
        sms_fallback_method: HttpMethod | None = None,
        sms_application_sid: str | None = None,
        voice_application_sid: str | None = None,
        status_callback: str | None = None,
        status_callback_method: HttpMethod | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers"),
                data=_create_form(
                    phone_number=phone_number,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    sms_url=sms_url,
                    sms_method=sms_method,
                    sms_fallback_url=sms_fallback_url,
                    sms_fallback_method=sms_fallback_method,
                    sms_application_sid=sms_application_sid,
                    voice_application_sid=voice_application_sid,
                    status_callback=status_callback,
                    status_callback_method=status_callback_method,
                ),
            )
        )

    def get(self, sid: str) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            self._t.request("GET", self._path("IncomingPhoneNumbers", sid))
        )

    def update(
        self,
        sid: str,
        *,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: HttpMethod | None = None,
        sms_url: str | None = None,
        sms_method: HttpMethod | None = None,
        sms_fallback_url: str | None = None,
        sms_fallback_method: HttpMethod | None = None,
        sms_application_sid: str | None = None,
        voice_application_sid: str | None = None,
        status_callback: str | None = None,
        status_callback_method: HttpMethod | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers", sid),
                data=_update_form(
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    sms_url=sms_url,
                    sms_method=sms_method,
                    sms_fallback_url=sms_fallback_url,
                    sms_fallback_method=sms_fallback_method,
                    sms_application_sid=sms_application_sid,
                    voice_application_sid=voice_application_sid,
                    status_callback=status_callback,
                    status_callback_method=status_callback_method,
                ),
            )
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", self._path("IncomingPhoneNumbers", sid))

    def list_local(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: IncomingPhoneNumberOrigin | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return self._list(
            "Local",
            _list_params(
                phone_number=phone_number,
                friendly_name=friendly_name,
                beta=beta,
                origin=origin,
                page=page,
                page_size=page_size,
                page_token=page_token,
            ),
        )

    def create_local(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
    ) -> IncomingPhoneNumber:
        return self._create_typed(
            "Local",
            _typed_create_form(
                phone_number=phone_number, voice_url=voice_url, voice_method=voice_method
            ),
        )

    def list_mobile(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: IncomingPhoneNumberOrigin | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return self._list(
            "Mobile",
            _list_params(
                phone_number=phone_number,
                friendly_name=friendly_name,
                beta=beta,
                origin=origin,
                page=page,
                page_size=page_size,
                page_token=page_token,
            ),
        )

    def create_mobile(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
    ) -> IncomingPhoneNumber:
        return self._create_typed(
            "Mobile",
            _typed_create_form(
                phone_number=phone_number, voice_url=voice_url, voice_method=voice_method
            ),
        )

    def list_toll_free(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: IncomingPhoneNumberOrigin | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return self._list(
            "TollFree",
            _list_params(
                phone_number=phone_number,
                friendly_name=friendly_name,
                beta=beta,
                origin=origin,
                page=page,
                page_size=page_size,
                page_token=page_token,
            ),
        )

    def create_toll_free(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
    ) -> IncomingPhoneNumber:
        return self._create_typed(
            "TollFree",
            _typed_create_form(
                phone_number=phone_number, voice_url=voice_url, voice_method=voice_method
            ),
        )


class IncomingPhoneNumbersAsyncResource(AsyncResource):
    """Async counterpart to :class:`IncomingPhoneNumbersResource`."""

    async def _list(self, kind: str | None, params: dict[str, object]) -> IncomingPhoneNumberList:
        parts = ("IncomingPhoneNumbers",) if kind is None else ("IncomingPhoneNumbers", kind)
        return IncomingPhoneNumberList.model_validate(
            await self._t.request("GET", self._path(*parts), params=params)
        )

    async def _create_typed(self, kind: str, form: dict[str, object]) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            await self._t.request("POST", self._path("IncomingPhoneNumbers", kind), data=form)
        )

    async def list(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: IncomingPhoneNumberOrigin | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return await self._list(
            None,
            _list_params(
                phone_number=phone_number,
                friendly_name=friendly_name,
                beta=beta,
                origin=origin,
                page=page,
                page_size=page_size,
                page_token=page_token,
            ),
        )

    async def iter(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: IncomingPhoneNumberOrigin | None = None,
        page_size: int | None = None,
    ) -> AsyncIterator[IncomingPhoneNumber]:
        """Lazily yield every number, following ``next_page_uri`` page by page."""
        first = await self.list(
            phone_number=phone_number,
            friendly_name=friendly_name,
            beta=beta,
            origin=origin,
            page_size=page_size,
        )
        async for item in self._paginate(first):
            yield item

    async def create(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: HttpMethod | None = None,
        sms_url: str | None = None,
        sms_method: HttpMethod | None = None,
        sms_fallback_url: str | None = None,
        sms_fallback_method: HttpMethod | None = None,
        sms_application_sid: str | None = None,
        voice_application_sid: str | None = None,
        status_callback: str | None = None,
        status_callback_method: HttpMethod | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            await self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers"),
                data=_create_form(
                    phone_number=phone_number,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    sms_url=sms_url,
                    sms_method=sms_method,
                    sms_fallback_url=sms_fallback_url,
                    sms_fallback_method=sms_fallback_method,
                    sms_application_sid=sms_application_sid,
                    voice_application_sid=voice_application_sid,
                    status_callback=status_callback,
                    status_callback_method=status_callback_method,
                ),
            )
        )

    async def get(self, sid: str) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            await self._t.request("GET", self._path("IncomingPhoneNumbers", sid))
        )

    async def update(
        self,
        sid: str,
        *,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: HttpMethod | None = None,
        sms_url: str | None = None,
        sms_method: HttpMethod | None = None,
        sms_fallback_url: str | None = None,
        sms_fallback_method: HttpMethod | None = None,
        sms_application_sid: str | None = None,
        voice_application_sid: str | None = None,
        status_callback: str | None = None,
        status_callback_method: HttpMethod | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            await self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers", sid),
                data=_update_form(
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    sms_url=sms_url,
                    sms_method=sms_method,
                    sms_fallback_url=sms_fallback_url,
                    sms_fallback_method=sms_fallback_method,
                    sms_application_sid=sms_application_sid,
                    voice_application_sid=voice_application_sid,
                    status_callback=status_callback,
                    status_callback_method=status_callback_method,
                ),
            )
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", self._path("IncomingPhoneNumbers", sid))

    async def list_local(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: IncomingPhoneNumberOrigin | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return await self._list(
            "Local",
            _list_params(
                phone_number=phone_number,
                friendly_name=friendly_name,
                beta=beta,
                origin=origin,
                page=page,
                page_size=page_size,
                page_token=page_token,
            ),
        )

    async def create_local(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
    ) -> IncomingPhoneNumber:
        return await self._create_typed(
            "Local",
            _typed_create_form(
                phone_number=phone_number, voice_url=voice_url, voice_method=voice_method
            ),
        )

    async def list_mobile(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: IncomingPhoneNumberOrigin | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return await self._list(
            "Mobile",
            _list_params(
                phone_number=phone_number,
                friendly_name=friendly_name,
                beta=beta,
                origin=origin,
                page=page,
                page_size=page_size,
                page_token=page_token,
            ),
        )

    async def create_mobile(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
    ) -> IncomingPhoneNumber:
        return await self._create_typed(
            "Mobile",
            _typed_create_form(
                phone_number=phone_number, voice_url=voice_url, voice_method=voice_method
            ),
        )

    async def list_toll_free(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: IncomingPhoneNumberOrigin | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return await self._list(
            "TollFree",
            _list_params(
                phone_number=phone_number,
                friendly_name=friendly_name,
                beta=beta,
                origin=origin,
                page=page,
                page_size=page_size,
                page_token=page_token,
            ),
        )

    async def create_toll_free(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
    ) -> IncomingPhoneNumber:
        return await self._create_typed(
            "TollFree",
            _typed_create_form(
                phone_number=phone_number, voice_url=voice_url, voice_method=voice_method
            ),
        )
