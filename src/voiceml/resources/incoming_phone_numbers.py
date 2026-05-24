"""``/IncomingPhoneNumbers`` — tenant-self-serve DID assignment + voice routing.

The ``sid`` URL path param is the canonical ``PN``-prefixed identifier (e.g.
``PN0123456789abcdef0123456789abcdef``). The server accepts the legacy E.164 form
(``+18005551234``) during the transition window, but tenants are encouraged to use the
PN-sid. This SDK accepts either as the ``sid`` argument — the value is URL-encoded and
passed through; the server resolves it to the underlying row.
"""

from __future__ import annotations

from urllib.parse import quote

from ..models import (
    CreateIncomingPhoneNumberRequest,
    IncomingPhoneNumber,
    IncomingPhoneNumberList,
    UpdateIncomingPhoneNumberRequest,
)
from ._base import AsyncResource, Resource


def _typed_list_params(
    *,
    phone_number: str | None,
    friendly_name: str | None,
    beta: bool | None,
    origin: str | None,
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


def _list_params(
    *,
    phone_number: str | None,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
) -> dict[str, object]:
    return {
        "PhoneNumber": phone_number,
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
    }


def _encode_sid(sid: str) -> str:
    """URL-encode an IncomingPhoneNumber identifier.

    PN-sids ([A-Za-z0-9]) pass through unchanged; legacy E.164 sids have the leading
    ``+`` encoded to ``%2B`` so they survive routing without being mistaken for a
    space. Using ``quote(safe="")`` is conservative — encodes everything reserved.
    """
    return quote(sid, safe="")


def _build_create_form(
    *,
    phone_number: str,
    voice_url: str | None,
    voice_method: str | None,
    voice_fallback_url: str | None,
    voice_fallback_method: str | None,
    friendly_name: str | None,
) -> dict[str, object]:
    body = CreateIncomingPhoneNumberRequest(
        PhoneNumber=phone_number,
        VoiceUrl=voice_url,
        VoiceMethod=voice_method,  # type: ignore[arg-type]
        VoiceFallbackUrl=voice_fallback_url,
        VoiceFallbackMethod=voice_fallback_method,  # type: ignore[arg-type]
        FriendlyName=friendly_name,
    )
    return body.to_form()


def _build_update_form(
    *,
    voice_url: str | None,
    voice_method: str | None,
    voice_fallback_url: str | None,
    voice_fallback_method: str | None,
    friendly_name: str | None,
) -> dict[str, object]:
    body = UpdateIncomingPhoneNumberRequest(
        VoiceUrl=voice_url,
        VoiceMethod=voice_method,  # type: ignore[arg-type]
        VoiceFallbackUrl=voice_fallback_url,
        VoiceFallbackMethod=voice_fallback_method,  # type: ignore[arg-type]
        FriendlyName=friendly_name,
    )
    return body.to_form()


class IncomingPhoneNumbersResource(Resource):
    """Sync ``IncomingPhoneNumbers`` operations."""

    def list(
        self,
        *,
        phone_number: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return IncomingPhoneNumberList.model_validate(
            self._t.request(
                "GET",
                self._path("IncomingPhoneNumbers"),
                params=_list_params(
                    phone_number=phone_number,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def create(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        friendly_name: str | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers"),
                data=_build_create_form(
                    phone_number=phone_number,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    friendly_name=friendly_name,
                ),
            )
        )

    def get(self, sid: str) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            self._t.request(
                "GET", self._path("IncomingPhoneNumbers", _encode_sid(sid))
            )
        )

    def update(
        self,
        sid: str,
        *,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        friendly_name: str | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers", _encode_sid(sid)),
                data=_build_update_form(
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    friendly_name=friendly_name,
                ),
            )
        )

    def delete(self, sid: str) -> None:
        self._t.request(
            "DELETE", self._path("IncomingPhoneNumbers", _encode_sid(sid))
        )

    def list_local(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return IncomingPhoneNumberList.model_validate(
            self._t.request(
                "GET",
                self._path("IncomingPhoneNumbers", "Local"),
                params=_typed_list_params(
                    phone_number=phone_number,
                    friendly_name=friendly_name,
                    beta=beta,
                    origin=origin,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def create_local(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        friendly_name: str | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers", "Local"),
                data=_build_create_form(
                    phone_number=phone_number,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    friendly_name=friendly_name,
                ),
            )
        )

    def list_mobile(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return IncomingPhoneNumberList.model_validate(
            self._t.request(
                "GET",
                self._path("IncomingPhoneNumbers", "Mobile"),
                params=_typed_list_params(
                    phone_number=phone_number,
                    friendly_name=friendly_name,
                    beta=beta,
                    origin=origin,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def create_mobile(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        friendly_name: str | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers", "Mobile"),
                data=_build_create_form(
                    phone_number=phone_number,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    friendly_name=friendly_name,
                ),
            )
        )

    def list_toll_free(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return IncomingPhoneNumberList.model_validate(
            self._t.request(
                "GET",
                self._path("IncomingPhoneNumbers", "TollFree"),
                params=_typed_list_params(
                    phone_number=phone_number,
                    friendly_name=friendly_name,
                    beta=beta,
                    origin=origin,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def create_toll_free(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        friendly_name: str | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers", "TollFree"),
                data=_build_create_form(
                    phone_number=phone_number,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    friendly_name=friendly_name,
                ),
            )
        )


class IncomingPhoneNumbersAsyncResource(AsyncResource):
    """Async counterpart to :class:`IncomingPhoneNumbersResource`."""

    async def list(
        self,
        *,
        phone_number: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return IncomingPhoneNumberList.model_validate(
            await self._t.request(
                "GET",
                self._path("IncomingPhoneNumbers"),
                params=_list_params(
                    phone_number=phone_number,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def create(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        friendly_name: str | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            await self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers"),
                data=_build_create_form(
                    phone_number=phone_number,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    friendly_name=friendly_name,
                ),
            )
        )

    async def get(self, sid: str) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            await self._t.request(
                "GET", self._path("IncomingPhoneNumbers", _encode_sid(sid))
            )
        )

    async def update(
        self,
        sid: str,
        *,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        friendly_name: str | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            await self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers", _encode_sid(sid)),
                data=_build_update_form(
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    friendly_name=friendly_name,
                ),
            )
        )

    async def delete(self, sid: str) -> None:
        await self._t.request(
            "DELETE", self._path("IncomingPhoneNumbers", _encode_sid(sid))
        )

    async def list_local(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return IncomingPhoneNumberList.model_validate(
            await self._t.request(
                "GET",
                self._path("IncomingPhoneNumbers", "Local"),
                params=_typed_list_params(
                    phone_number=phone_number,
                    friendly_name=friendly_name,
                    beta=beta,
                    origin=origin,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def create_local(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        friendly_name: str | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            await self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers", "Local"),
                data=_build_create_form(
                    phone_number=phone_number,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    friendly_name=friendly_name,
                ),
            )
        )

    async def list_mobile(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return IncomingPhoneNumberList.model_validate(
            await self._t.request(
                "GET",
                self._path("IncomingPhoneNumbers", "Mobile"),
                params=_typed_list_params(
                    phone_number=phone_number,
                    friendly_name=friendly_name,
                    beta=beta,
                    origin=origin,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def create_mobile(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        friendly_name: str | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            await self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers", "Mobile"),
                data=_build_create_form(
                    phone_number=phone_number,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    friendly_name=friendly_name,
                ),
            )
        )

    async def list_toll_free(
        self,
        *,
        phone_number: str | None = None,
        friendly_name: str | None = None,
        beta: bool | None = None,
        origin: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> IncomingPhoneNumberList:
        return IncomingPhoneNumberList.model_validate(
            await self._t.request(
                "GET",
                self._path("IncomingPhoneNumbers", "TollFree"),
                params=_typed_list_params(
                    phone_number=phone_number,
                    friendly_name=friendly_name,
                    beta=beta,
                    origin=origin,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def create_toll_free(
        self,
        *,
        phone_number: str,
        voice_url: str | None = None,
        voice_method: str | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: str | None = None,
        friendly_name: str | None = None,
    ) -> IncomingPhoneNumber:
        return IncomingPhoneNumber.model_validate(
            await self._t.request(
                "POST",
                self._path("IncomingPhoneNumbers", "TollFree"),
                data=_build_create_form(
                    phone_number=phone_number,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    friendly_name=friendly_name,
                ),
            )
        )
