"""``/v1/Services`` Messaging Service surface — Twilio-compatible Messaging v1.

Wired under ``client.messaging_v1.services.*``. The whole group is routed at the
messaging host (``messaging.voicetel.com``) by the client, which is what
disambiguates a Messaging Service (``MG…``) from a Conversation Service
(``IS…``) — they share the ``/v1/Services`` path shape. See :mod:`voiceml._hosts`.

``create`` / ``list`` / ``fetch`` / ``delete`` reuse the shared path; ``update``
(``POST /v1/Services/{sid}``) is unique to Messaging Service.
"""

from __future__ import annotations

from typing import Literal

from .._http import _ScopedTransport
from ..models import (
    CreateMessagingServicePhoneNumberRequest,
    CreateMessagingServiceRequest,
    MessagingService,
    MessagingServiceList,
    MessagingServicePhoneNumber,
    MessagingServicePhoneNumberList,
    UpdateMessagingServiceRequest,
)
from ..models.calls import HttpMethod
from ._base import path


def _page_params(*, page_size: int | None) -> dict[str, object]:
    return {"PageSize": page_size}


class MessagingV1PhoneNumbersResource:
    """``client.messaging_v1.services.phone_numbers(service_sid)`` — the service's sender
    pool (messaging host only)."""

    def __init__(self, transport: _ScopedTransport, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def __repr__(self) -> str:
        return f"<MessagingV1PhoneNumbersResource service_sid={self._svc!r}>"

    def list(
        self, *, page: int | None = None, page_size: int | None = None
    ) -> MessagingServicePhoneNumberList:
        return MessagingServicePhoneNumberList.model_validate(
            self._t.request(
                "GET",
                path("v1", "Services", self._svc, "PhoneNumbers"),
                params={"Page": page, "PageSize": page_size},
            )
        )

    def create(self, *, phone_number_sid: str) -> MessagingServicePhoneNumber:
        """Add an IncomingPhoneNumber (``PN…`` sid) to the sender pool."""
        form = CreateMessagingServicePhoneNumberRequest(phone_number_sid=phone_number_sid)
        return MessagingServicePhoneNumber.model_validate(
            self._t.request(
                "POST", path("v1", "Services", self._svc, "PhoneNumbers"), data=form.to_form()
            )
        )

    def fetch(self, sid: str) -> MessagingServicePhoneNumber:
        return MessagingServicePhoneNumber.model_validate(
            self._t.request("GET", path("v1", "Services", self._svc, "PhoneNumbers", sid))
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", path("v1", "Services", self._svc, "PhoneNumbers", sid))


class MessagingV1ServicesResource:
    """Operations on ``/v1/Services`` at the messaging host (sync)."""

    def __init__(self, transport: _ScopedTransport) -> None:
        self._t = transport

    def create(
        self,
        *,
        friendly_name: str,
        inbound_request_url: str | None = None,
        inbound_method: HttpMethod | None = None,
        fallback_url: str | None = None,
        fallback_method: HttpMethod | None = None,
        status_callback: str | None = None,
        sticky_sender: bool | None = None,
        mms_converter: bool | None = None,
        smart_encoding: bool | None = None,
        scan_message_content: Literal["inherit", "enable", "disable"] | None = None,
        fallback_to_long_code: bool | None = None,
        area_code_geomatch: bool | None = None,
        synchronous_validation: bool | None = None,
        validity_period: int | None = None,
        usecase: str | None = None,
        use_inbound_webhook_on_number: bool | None = None,
    ) -> MessagingService:
        body = CreateMessagingServiceRequest(
            friendly_name=friendly_name,
            inbound_request_url=inbound_request_url,
            inbound_method=inbound_method,
            fallback_url=fallback_url,
            fallback_method=fallback_method,
            status_callback=status_callback,
            sticky_sender=sticky_sender,
            mms_converter=mms_converter,
            smart_encoding=smart_encoding,
            scan_message_content=scan_message_content,
            fallback_to_long_code=fallback_to_long_code,
            area_code_geomatch=area_code_geomatch,
            synchronous_validation=synchronous_validation,
            validity_period=validity_period,
            usecase=usecase,
            use_inbound_webhook_on_number=use_inbound_webhook_on_number,
        ).to_form()
        return MessagingService.model_validate(
            self._t.request("POST", path("v1", "Services"), data=body)
        )

    def list(self, *, page_size: int | None = None) -> MessagingServiceList:
        return MessagingServiceList.model_validate(
            self._t.request("GET", path("v1", "Services"), params=_page_params(page_size=page_size))
        )

    def fetch(self, sid: str) -> MessagingService:
        return MessagingService.model_validate(self._t.request("GET", path("v1", "Services", sid)))

    def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        inbound_request_url: str | None = None,
        inbound_method: HttpMethod | None = None,
        fallback_url: str | None = None,
        fallback_method: HttpMethod | None = None,
        status_callback: str | None = None,
        sticky_sender: bool | None = None,
        mms_converter: bool | None = None,
        smart_encoding: bool | None = None,
        scan_message_content: Literal["inherit", "enable", "disable"] | None = None,
        fallback_to_long_code: bool | None = None,
        area_code_geomatch: bool | None = None,
        synchronous_validation: bool | None = None,
        validity_period: int | None = None,
        usecase: str | None = None,
        use_inbound_webhook_on_number: bool | None = None,
    ) -> MessagingService:
        body = UpdateMessagingServiceRequest(
            friendly_name=friendly_name,
            inbound_request_url=inbound_request_url,
            inbound_method=inbound_method,
            fallback_url=fallback_url,
            fallback_method=fallback_method,
            status_callback=status_callback,
            sticky_sender=sticky_sender,
            mms_converter=mms_converter,
            smart_encoding=smart_encoding,
            scan_message_content=scan_message_content,
            fallback_to_long_code=fallback_to_long_code,
            area_code_geomatch=area_code_geomatch,
            synchronous_validation=synchronous_validation,
            validity_period=validity_period,
            usecase=usecase,
            use_inbound_webhook_on_number=use_inbound_webhook_on_number,
        ).to_form()
        return MessagingService.model_validate(
            self._t.request("POST", path("v1", "Services", sid), data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", path("v1", "Services", sid))

    def phone_numbers(self, service_sid: str) -> MessagingV1PhoneNumbersResource:
        """The sender-pool phone numbers of Messaging Service ``service_sid``."""
        return MessagingV1PhoneNumbersResource(self._t, service_sid)


class MessagingV1Resource:
    """Holder for ``client.messaging_v1.*`` sub-resources (sync)."""

    def __init__(self, transport: _ScopedTransport) -> None:
        self.services = MessagingV1ServicesResource(transport)


# ===========================================================================
# Async counterparts — same surface; methods are awaitable.
# ===========================================================================


class MessagingV1PhoneNumbersAsyncResource:
    """``client.messaging_v1.services.phone_numbers(service_sid)`` — the service's sender
    pool (messaging host only)."""

    def __init__(self, transport: _ScopedTransport, service_sid: str) -> None:
        self._t = transport
        self._svc = service_sid

    def __repr__(self) -> str:
        return f"<MessagingV1PhoneNumbersAsyncResource service_sid={self._svc!r}>"

    async def list(
        self, *, page: int | None = None, page_size: int | None = None
    ) -> MessagingServicePhoneNumberList:
        return MessagingServicePhoneNumberList.model_validate(
            await self._t.request(
                "GET",
                path("v1", "Services", self._svc, "PhoneNumbers"),
                params={"Page": page, "PageSize": page_size},
            )
        )

    async def create(self, *, phone_number_sid: str) -> MessagingServicePhoneNumber:
        """Add an IncomingPhoneNumber (``PN…`` sid) to the sender pool."""
        form = CreateMessagingServicePhoneNumberRequest(phone_number_sid=phone_number_sid)
        return MessagingServicePhoneNumber.model_validate(
            await self._t.request(
                "POST", path("v1", "Services", self._svc, "PhoneNumbers"), data=form.to_form()
            )
        )

    async def fetch(self, sid: str) -> MessagingServicePhoneNumber:
        return MessagingServicePhoneNumber.model_validate(
            await self._t.request("GET", path("v1", "Services", self._svc, "PhoneNumbers", sid))
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", path("v1", "Services", self._svc, "PhoneNumbers", sid))


class MessagingV1ServicesAsyncResource:
    """Operations on ``/v1/Services`` at the messaging host (async)."""

    def __init__(self, transport: _ScopedTransport) -> None:
        self._t = transport

    async def create(
        self,
        *,
        friendly_name: str,
        inbound_request_url: str | None = None,
        inbound_method: HttpMethod | None = None,
        fallback_url: str | None = None,
        fallback_method: HttpMethod | None = None,
        status_callback: str | None = None,
        sticky_sender: bool | None = None,
        mms_converter: bool | None = None,
        smart_encoding: bool | None = None,
        scan_message_content: Literal["inherit", "enable", "disable"] | None = None,
        fallback_to_long_code: bool | None = None,
        area_code_geomatch: bool | None = None,
        synchronous_validation: bool | None = None,
        validity_period: int | None = None,
        usecase: str | None = None,
        use_inbound_webhook_on_number: bool | None = None,
    ) -> MessagingService:
        body = CreateMessagingServiceRequest(
            friendly_name=friendly_name,
            inbound_request_url=inbound_request_url,
            inbound_method=inbound_method,
            fallback_url=fallback_url,
            fallback_method=fallback_method,
            status_callback=status_callback,
            sticky_sender=sticky_sender,
            mms_converter=mms_converter,
            smart_encoding=smart_encoding,
            scan_message_content=scan_message_content,
            fallback_to_long_code=fallback_to_long_code,
            area_code_geomatch=area_code_geomatch,
            synchronous_validation=synchronous_validation,
            validity_period=validity_period,
            usecase=usecase,
            use_inbound_webhook_on_number=use_inbound_webhook_on_number,
        ).to_form()
        return MessagingService.model_validate(
            await self._t.request("POST", path("v1", "Services"), data=body)
        )

    async def list(self, *, page_size: int | None = None) -> MessagingServiceList:
        return MessagingServiceList.model_validate(
            await self._t.request(
                "GET", path("v1", "Services"), params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> MessagingService:
        return MessagingService.model_validate(
            await self._t.request("GET", path("v1", "Services", sid))
        )

    async def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        inbound_request_url: str | None = None,
        inbound_method: HttpMethod | None = None,
        fallback_url: str | None = None,
        fallback_method: HttpMethod | None = None,
        status_callback: str | None = None,
        sticky_sender: bool | None = None,
        mms_converter: bool | None = None,
        smart_encoding: bool | None = None,
        scan_message_content: Literal["inherit", "enable", "disable"] | None = None,
        fallback_to_long_code: bool | None = None,
        area_code_geomatch: bool | None = None,
        synchronous_validation: bool | None = None,
        validity_period: int | None = None,
        usecase: str | None = None,
        use_inbound_webhook_on_number: bool | None = None,
    ) -> MessagingService:
        body = UpdateMessagingServiceRequest(
            friendly_name=friendly_name,
            inbound_request_url=inbound_request_url,
            inbound_method=inbound_method,
            fallback_url=fallback_url,
            fallback_method=fallback_method,
            status_callback=status_callback,
            sticky_sender=sticky_sender,
            mms_converter=mms_converter,
            smart_encoding=smart_encoding,
            scan_message_content=scan_message_content,
            fallback_to_long_code=fallback_to_long_code,
            area_code_geomatch=area_code_geomatch,
            synchronous_validation=synchronous_validation,
            validity_period=validity_period,
            usecase=usecase,
            use_inbound_webhook_on_number=use_inbound_webhook_on_number,
        ).to_form()
        return MessagingService.model_validate(
            await self._t.request("POST", path("v1", "Services", sid), data=body)
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", path("v1", "Services", sid))

    def phone_numbers(self, service_sid: str) -> MessagingV1PhoneNumbersAsyncResource:
        """The sender-pool phone numbers of Messaging Service ``service_sid``."""
        return MessagingV1PhoneNumbersAsyncResource(self._t, service_sid)


class MessagingV1AsyncResource:
    """Holder for ``client.messaging_v1.*`` sub-resources (async)."""

    def __init__(self, transport: _ScopedTransport) -> None:
        self.services = MessagingV1ServicesAsyncResource(transport)
