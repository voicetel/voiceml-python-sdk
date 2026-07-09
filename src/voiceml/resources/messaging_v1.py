"""``/v1/Services`` Messaging Service surface — Twilio ``messaging.twilio.com/v1``.

Wired under ``client.messaging_v1.services.*``. The whole group is routed at the
messaging host (``messaging.voicetel.com``) by the client, which is what
disambiguates a Messaging Service (``MG…``) from a Conversation Service
(``IS…``) — they share the ``/v1/Services`` path shape. See :mod:`voiceml._hosts`.

``create`` / ``list`` / ``fetch`` / ``delete`` reuse the shared path; ``update``
(``POST /v1/Services/{sid}``) is unique to Messaging Service.
"""

from __future__ import annotations

from ..models import (
    CreateMessagingServiceRequest,
    MessagingService,
    MessagingServiceList,
    UpdateMessagingServiceRequest,
)


def _page_params(*, page_size: int | None) -> dict[str, object]:
    return {"PageSize": page_size}


class MessagingV1ServicesResource:
    """Operations on ``/v1/Services`` at the messaging host (sync)."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    def create(
        self,
        *,
        friendly_name: str,
        inbound_request_url: str | None = None,
        inbound_method: str | None = None,
        fallback_url: str | None = None,
        fallback_method: str | None = None,
        status_callback: str | None = None,
        sticky_sender: bool | None = None,
        mms_converter: bool | None = None,
        smart_encoding: bool | None = None,
        scan_message_content: str | None = None,
        fallback_to_long_code: bool | None = None,
        area_code_geomatch: bool | None = None,
        synchronous_validation: bool | None = None,
        validity_period: int | None = None,
        usecase: str | None = None,
        use_inbound_webhook_on_number: bool | None = None,
    ) -> MessagingService:
        body = CreateMessagingServiceRequest(
            FriendlyName=friendly_name,
            InboundRequestUrl=inbound_request_url,
            InboundMethod=inbound_method,
            FallbackUrl=fallback_url,
            FallbackMethod=fallback_method,
            StatusCallback=status_callback,
            StickySender=sticky_sender,
            MmsConverter=mms_converter,
            SmartEncoding=smart_encoding,
            ScanMessageContent=scan_message_content,
            FallbackToLongCode=fallback_to_long_code,
            AreaCodeGeomatch=area_code_geomatch,
            SynchronousValidation=synchronous_validation,
            ValidityPeriod=validity_period,
            Usecase=usecase,
            UseInboundWebhookOnNumber=use_inbound_webhook_on_number,
        ).to_form()
        return MessagingService.model_validate(
            self._t.request("POST", "/v1/Services", data=body)
        )

    def list(self, *, page_size: int | None = None) -> MessagingServiceList:
        return MessagingServiceList.model_validate(
            self._t.request(
                "GET", "/v1/Services", params=_page_params(page_size=page_size)
            )
        )

    def fetch(self, sid: str) -> MessagingService:
        return MessagingService.model_validate(
            self._t.request("GET", f"/v1/Services/{sid}")
        )

    def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        inbound_request_url: str | None = None,
        inbound_method: str | None = None,
        fallback_url: str | None = None,
        fallback_method: str | None = None,
        status_callback: str | None = None,
        sticky_sender: bool | None = None,
        mms_converter: bool | None = None,
        smart_encoding: bool | None = None,
        scan_message_content: str | None = None,
        fallback_to_long_code: bool | None = None,
        area_code_geomatch: bool | None = None,
        synchronous_validation: bool | None = None,
        validity_period: int | None = None,
        usecase: str | None = None,
        use_inbound_webhook_on_number: bool | None = None,
    ) -> MessagingService:
        body = UpdateMessagingServiceRequest(
            FriendlyName=friendly_name,
            InboundRequestUrl=inbound_request_url,
            InboundMethod=inbound_method,
            FallbackUrl=fallback_url,
            FallbackMethod=fallback_method,
            StatusCallback=status_callback,
            StickySender=sticky_sender,
            MmsConverter=mms_converter,
            SmartEncoding=smart_encoding,
            ScanMessageContent=scan_message_content,
            FallbackToLongCode=fallback_to_long_code,
            AreaCodeGeomatch=area_code_geomatch,
            SynchronousValidation=synchronous_validation,
            ValidityPeriod=validity_period,
            Usecase=usecase,
            UseInboundWebhookOnNumber=use_inbound_webhook_on_number,
        ).to_form()
        return MessagingService.model_validate(
            self._t.request("POST", f"/v1/Services/{sid}", data=body)
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", f"/v1/Services/{sid}")


class MessagingV1Resource:
    """Holder for ``client.messaging_v1.*`` sub-resources (sync)."""

    def __init__(self, transport: object) -> None:
        self.services = MessagingV1ServicesResource(transport)


# ===========================================================================
# Async counterparts — same surface; methods are awaitable.
# ===========================================================================


class MessagingV1ServicesAsyncResource:
    """Operations on ``/v1/Services`` at the messaging host (async)."""

    def __init__(self, transport: object) -> None:
        self._t = transport

    async def create(
        self,
        *,
        friendly_name: str,
        inbound_request_url: str | None = None,
        inbound_method: str | None = None,
        fallback_url: str | None = None,
        fallback_method: str | None = None,
        status_callback: str | None = None,
        sticky_sender: bool | None = None,
        mms_converter: bool | None = None,
        smart_encoding: bool | None = None,
        scan_message_content: str | None = None,
        fallback_to_long_code: bool | None = None,
        area_code_geomatch: bool | None = None,
        synchronous_validation: bool | None = None,
        validity_period: int | None = None,
        usecase: str | None = None,
        use_inbound_webhook_on_number: bool | None = None,
    ) -> MessagingService:
        body = CreateMessagingServiceRequest(
            FriendlyName=friendly_name,
            InboundRequestUrl=inbound_request_url,
            InboundMethod=inbound_method,
            FallbackUrl=fallback_url,
            FallbackMethod=fallback_method,
            StatusCallback=status_callback,
            StickySender=sticky_sender,
            MmsConverter=mms_converter,
            SmartEncoding=smart_encoding,
            ScanMessageContent=scan_message_content,
            FallbackToLongCode=fallback_to_long_code,
            AreaCodeGeomatch=area_code_geomatch,
            SynchronousValidation=synchronous_validation,
            ValidityPeriod=validity_period,
            Usecase=usecase,
            UseInboundWebhookOnNumber=use_inbound_webhook_on_number,
        ).to_form()
        return MessagingService.model_validate(
            await self._t.request("POST", "/v1/Services", data=body)
        )

    async def list(self, *, page_size: int | None = None) -> MessagingServiceList:
        return MessagingServiceList.model_validate(
            await self._t.request(
                "GET", "/v1/Services", params=_page_params(page_size=page_size)
            )
        )

    async def fetch(self, sid: str) -> MessagingService:
        return MessagingService.model_validate(
            await self._t.request("GET", f"/v1/Services/{sid}")
        )

    async def update(
        self,
        sid: str,
        *,
        friendly_name: str | None = None,
        inbound_request_url: str | None = None,
        inbound_method: str | None = None,
        fallback_url: str | None = None,
        fallback_method: str | None = None,
        status_callback: str | None = None,
        sticky_sender: bool | None = None,
        mms_converter: bool | None = None,
        smart_encoding: bool | None = None,
        scan_message_content: str | None = None,
        fallback_to_long_code: bool | None = None,
        area_code_geomatch: bool | None = None,
        synchronous_validation: bool | None = None,
        validity_period: int | None = None,
        usecase: str | None = None,
        use_inbound_webhook_on_number: bool | None = None,
    ) -> MessagingService:
        body = UpdateMessagingServiceRequest(
            FriendlyName=friendly_name,
            InboundRequestUrl=inbound_request_url,
            InboundMethod=inbound_method,
            FallbackUrl=fallback_url,
            FallbackMethod=fallback_method,
            StatusCallback=status_callback,
            StickySender=sticky_sender,
            MmsConverter=mms_converter,
            SmartEncoding=smart_encoding,
            ScanMessageContent=scan_message_content,
            FallbackToLongCode=fallback_to_long_code,
            AreaCodeGeomatch=area_code_geomatch,
            SynchronousValidation=synchronous_validation,
            ValidityPeriod=validity_period,
            Usecase=usecase,
            UseInboundWebhookOnNumber=use_inbound_webhook_on_number,
        ).to_form()
        return MessagingService.model_validate(
            await self._t.request("POST", f"/v1/Services/{sid}", data=body)
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", f"/v1/Services/{sid}")


class MessagingV1AsyncResource:
    """Holder for ``client.messaging_v1.*`` sub-resources (async)."""

    def __init__(self, transport: object) -> None:
        self.services = MessagingV1ServicesAsyncResource(transport)
