"""``/Calls`` and call-scoped sub-resources (Recordings, Streams, Siprec, Transcriptions,
Notifications, Events, UserDefinedMessages, Payments)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import datetime
from typing import Literal

from ..models import (
    Call,
    CallList,
    CallPayment,
    CallTranscription,
    CreateCallRequest,
    EventsList,
    Notification,
    NotificationsList,
    Recording,
    RecordingList,
    SiprecSession,
    StartPaymentRequest,
    StartRecordingRequest,
    StartSiprecRequest,
    StartStreamRequest,
    StartTranscriptionRequest,
    StopSiprecRequest,
    StopStreamRequest,
    StopTranscriptionRequest,
    Stream,
    UpdateCallRequest,
    UpdatePaymentRequest,
    UpdateRecordingRequest,
)
from ..models.payments import (
    PaymentBankAccountType,
    PaymentCapture,
    PaymentInput,
    PaymentMethod,
    PaymentSessionStatus,
    PaymentTokenType,
)
from ._base import AsyncResource, Resource

DateTimeFilter = str | datetime
NotificationLog = Literal[0, 1]


def _list_params(
    *,
    to: str | None,
    from_: str | None,
    status: str | None,
    parent_call_sid: str | None,
    start_time: DateTimeFilter | None,
    start_time_lt: DateTimeFilter | None,
    start_time_gt: DateTimeFilter | None,
    end_time: DateTimeFilter | None,
    end_time_lt: DateTimeFilter | None,
    end_time_gt: DateTimeFilter | None,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
) -> dict[str, object]:
    return {
        "To": to,
        "From": from_,
        "Status": status,
        "ParentCallSid": parent_call_sid,
        "StartTime": start_time,
        "StartTime<": start_time_lt,
        "StartTime>": start_time_gt,
        "EndTime": end_time,
        "EndTime<": end_time_lt,
        "EndTime>": end_time_gt,
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
    }


def _recording_list_params(
    *,
    date_created: str | None,
    date_created_lt: str | None,
    date_created_gt: str | None,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
) -> dict[str, object]:
    return {
        "DateCreated": date_created,
        "DateCreated<": date_created_lt,
        "DateCreated>": date_created_gt,
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
    }


def _notification_list_params(
    *,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
    log: NotificationLog | None,
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


def _page_params(
    *, page: int | None, page_size: int | None, page_token: str | None
) -> dict[str, object]:
    return {"Page": page, "PageSize": page_size, "PageToken": page_token}


def _start_payment_form(
    *,
    idempotency_key: str | None,
    status_callback: str | None,
    bank_account_type: PaymentBankAccountType | None,
    charge_amount: str | None,
    currency: str | None,
    description: str | None,
    input: PaymentInput | None,
    min_postal_code_length: int | None,
    parameter: str | None,
    payment_connector: str | None,
    payment_method: PaymentMethod | None,
    postal_code: bool | None,
    security_code: bool | None,
    timeout: int | None,
    token_type: PaymentTokenType | None,
    valid_card_types: str | None,
    require_matching_inputs: str | None,
    confirmation: bool | None,
) -> dict[str, object]:
    return StartPaymentRequest(
        idempotency_key=idempotency_key,
        status_callback=status_callback,
        bank_account_type=bank_account_type,
        charge_amount=charge_amount,
        currency=currency,
        description=description,
        input=input,
        min_postal_code_length=min_postal_code_length,
        parameter=parameter,
        payment_connector=payment_connector,
        payment_method=payment_method,
        postal_code=postal_code,
        security_code=security_code,
        timeout=timeout,
        token_type=token_type,
        valid_card_types=valid_card_types,
        require_matching_inputs=require_matching_inputs,
        confirmation=confirmation,
    ).to_form()


def _update_payment_form(
    *,
    idempotency_key: str | None,
    status_callback: str | None,
    capture: PaymentCapture | None,
    status: PaymentSessionStatus | None,
) -> dict[str, object]:
    return UpdatePaymentRequest(
        idempotency_key=idempotency_key,
        status_callback=status_callback,
        capture=capture,
        status=status,
    ).to_form()


class CallsResource(Resource):
    """Operations on calls and call-scoped sub-resources."""

    def list(
        self,
        *,
        to: str | None = None,
        from_: str | None = None,
        status: str | None = None,
        parent_call_sid: str | None = None,
        start_time: DateTimeFilter | None = None,
        start_time_lt: DateTimeFilter | None = None,
        start_time_gt: DateTimeFilter | None = None,
        end_time: DateTimeFilter | None = None,
        end_time_lt: DateTimeFilter | None = None,
        end_time_gt: DateTimeFilter | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> CallList:
        """One page of calls. ``datetime`` filters are sent as ISO-8601 UTC."""
        return CallList.model_validate(
            self._t.request(
                "GET",
                self._path("Calls"),
                params=_list_params(
                    to=to,
                    from_=from_,
                    status=status,
                    parent_call_sid=parent_call_sid,
                    start_time=start_time,
                    start_time_lt=start_time_lt,
                    start_time_gt=start_time_gt,
                    end_time=end_time,
                    end_time_lt=end_time_lt,
                    end_time_gt=end_time_gt,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def iter(
        self,
        *,
        to: str | None = None,
        from_: str | None = None,
        status: str | None = None,
        parent_call_sid: str | None = None,
        start_time: DateTimeFilter | None = None,
        start_time_lt: DateTimeFilter | None = None,
        start_time_gt: DateTimeFilter | None = None,
        end_time: DateTimeFilter | None = None,
        end_time_lt: DateTimeFilter | None = None,
        end_time_gt: DateTimeFilter | None = None,
        page_size: int | None = None,
    ) -> Iterator[Call]:
        """Lazily yield calls, following ``next_page_uri`` page by page.

        One request per page, issued as the iterator is consumed; stopping early
        issues no further requests.
        """
        yield from self._paginate(
            self.list(
                to=to,
                from_=from_,
                status=status,
                parent_call_sid=parent_call_sid,
                start_time=start_time,
                start_time_lt=start_time_lt,
                start_time_gt=start_time_gt,
                end_time=end_time,
                end_time_lt=end_time_lt,
                end_time_gt=end_time_gt,
                page_size=page_size,
            )
        )

    def create(self, body: CreateCallRequest) -> Call:
        """Originate a call. Never retried on 5xx or read timeouts (see README)."""
        return Call.model_validate(
            self._t.request("POST", self._path("Calls"), data=body.to_form())
        )

    def get(self, call_sid: str) -> Call:
        return Call.model_validate(self._t.request("GET", self._path("Calls", call_sid)))

    def update(self, call_sid: str, body: UpdateCallRequest) -> Call:
        return Call.model_validate(
            self._t.request("POST", self._path("Calls", call_sid), data=body.to_form())
        )

    def delete(self, call_sid: str) -> None:
        self._t.request("DELETE", self._path("Calls", call_sid))

    # --- Recordings (call-scoped) ---

    def list_recordings(
        self,
        call_sid: str,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> RecordingList:
        return RecordingList.model_validate(
            self._t.request(
                "GET",
                self._path("Calls", call_sid, "Recordings"),
                params=_recording_list_params(
                    date_created=date_created,
                    date_created_lt=date_created_lt,
                    date_created_gt=date_created_gt,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def start_recording(
        self, call_sid: str, body: StartRecordingRequest | None = None
    ) -> Recording:
        return Recording.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Recordings"),
                data=body.to_form() if body else None,
            )
        )

    def get_recording(self, call_sid: str, recording_sid: str) -> Recording:
        return Recording.model_validate(
            self._t.request("GET", self._path("Calls", call_sid, "Recordings", recording_sid))
        )

    def update_recording(
        self, call_sid: str, recording_sid: str, body: UpdateRecordingRequest
    ) -> Recording:
        """Stop / pause / resume a call recording.

        ``recording_sid`` may be ``"Twilio.CURRENT"`` to address the call's active
        recording.
        """
        return Recording.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Recordings", recording_sid),
                data=body.to_form(),
            )
        )

    def delete_recording(self, call_sid: str, recording_sid: str) -> None:
        self._t.request("DELETE", self._path("Calls", call_sid, "Recordings", recording_sid))

    # --- Streams / SIPREC / Transcriptions (start + stop only) ---

    def start_stream(self, call_sid: str, body: StartStreamRequest) -> Stream:
        return Stream.model_validate(
            self._t.request("POST", self._path("Calls", call_sid, "Streams"), data=body.to_form())
        )

    def stop_stream(
        self, call_sid: str, stream_sid: str, body: StopStreamRequest | None = None
    ) -> Stream:
        payload = (body or StopStreamRequest(status="stopped")).to_form()
        return Stream.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Streams", stream_sid),
                data=payload,
            )
        )

    def start_siprec(self, call_sid: str, body: StartSiprecRequest | None = None) -> SiprecSession:
        return SiprecSession.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Siprec"),
                data=body.to_form() if body else None,
            )
        )

    def stop_siprec(
        self, call_sid: str, siprec_sid: str, body: StopSiprecRequest | None = None
    ) -> SiprecSession:
        payload = (body or StopSiprecRequest(status="stopped")).to_form()
        return SiprecSession.model_validate(
            self._t.request(
                "POST", self._path("Calls", call_sid, "Siprec", siprec_sid), data=payload
            )
        )

    def start_transcription(
        self, call_sid: str, body: StartTranscriptionRequest | None = None
    ) -> CallTranscription:
        return CallTranscription.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Transcriptions"),
                data=body.to_form() if body else None,
            )
        )

    def stop_transcription(
        self,
        call_sid: str,
        transcription_sid: str,
        body: StopTranscriptionRequest | None = None,
    ) -> CallTranscription:
        payload = (body or StopTranscriptionRequest(status="stopped")).to_form()
        return CallTranscription.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Transcriptions", transcription_sid),
                data=payload,
            )
        )

    # --- Notifications / Events ---

    def list_notifications(
        self,
        call_sid: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        log: NotificationLog | None = None,
        message_date: str | None = None,
        message_date_lt: str | None = None,
        message_date_gt: str | None = None,
    ) -> NotificationsList:
        return NotificationsList.model_validate(
            self._t.request(
                "GET",
                self._path("Calls", call_sid, "Notifications"),
                params=_notification_list_params(
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

    def get_notification(self, call_sid: str, notification_sid: str) -> Notification:
        return Notification.model_validate(
            self._t.request("GET", self._path("Calls", call_sid, "Notifications", notification_sid))
        )

    def list_events(
        self,
        call_sid: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> EventsList:
        return EventsList.model_validate(
            self._t.request(
                "GET",
                self._path("Calls", call_sid, "Events"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    # --- UserDefinedMessages — server returns 501. Kept for API completeness. ---

    def send_user_defined_message(self, call_sid: str) -> None:
        """``POST /Calls/{sid}/UserDefinedMessages`` — always raises ``NotImplementedAPIError``.

        Mounted on the server only as a 501 stub. The SDK forwards the call so callers get a
        clean exception rather than discovering at runtime that the endpoint doesn't exist.
        """
        self._t.request("POST", self._path("Calls", call_sid, "UserDefinedMessages"))

    # --- Payments — REST companion to the ``<Pay>`` TwiML verb. ---

    def start_payment(
        self,
        call_sid: str,
        *,
        idempotency_key: str | None = None,
        status_callback: str | None = None,
        bank_account_type: PaymentBankAccountType | None = None,
        charge_amount: str | None = None,
        currency: str | None = None,
        description: str | None = None,
        input: PaymentInput | None = None,
        min_postal_code_length: int | None = None,
        parameter: str | None = None,
        payment_connector: str | None = None,
        payment_method: PaymentMethod | None = None,
        postal_code: bool | None = None,
        security_code: bool | None = None,
        timeout: int | None = None,
        token_type: PaymentTokenType | None = None,
        valid_card_types: str | None = None,
        require_matching_inputs: str | None = None,
        confirmation: bool | None = None,
    ) -> CallPayment:
        """Begin a ``<Pay>`` session on the live call.

        Returns 201 with the freshly-minted ``CallPayment``. Returns 403 when
        the tenant is not ``pay_enabled`` or has no ``stripe_secret_key``
        configured.
        """
        return CallPayment.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Payments"),
                data=_start_payment_form(
                    idempotency_key=idempotency_key,
                    status_callback=status_callback,
                    bank_account_type=bank_account_type,
                    charge_amount=charge_amount,
                    currency=currency,
                    description=description,
                    input=input,
                    min_postal_code_length=min_postal_code_length,
                    parameter=parameter,
                    payment_connector=payment_connector,
                    payment_method=payment_method,
                    postal_code=postal_code,
                    security_code=security_code,
                    timeout=timeout,
                    token_type=token_type,
                    valid_card_types=valid_card_types,
                    require_matching_inputs=require_matching_inputs,
                    confirmation=confirmation,
                ),
            )
        )

    def update_payment(
        self,
        call_sid: str,
        payment_sid: str,
        *,
        idempotency_key: str | None = None,
        status_callback: str | None = None,
        capture: PaymentCapture | None = None,
        status: PaymentSessionStatus | None = None,
    ) -> CallPayment:
        """Advance or terminate an existing Pay session.

        ``status="complete"`` captures the collected fields;
        ``status="cancel"`` aborts the session. ``capture=...`` tells the
        runtime which input the user is about to type next.
        """
        return CallPayment.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Payments", payment_sid),
                data=_update_payment_form(
                    idempotency_key=idempotency_key,
                    status_callback=status_callback,
                    capture=capture,
                    status=status,
                ),
            )
        )


class CallsAsyncResource(AsyncResource):
    """Async counterpart to :class:`CallsResource`."""

    async def list(
        self,
        *,
        to: str | None = None,
        from_: str | None = None,
        status: str | None = None,
        parent_call_sid: str | None = None,
        start_time: DateTimeFilter | None = None,
        start_time_lt: DateTimeFilter | None = None,
        start_time_gt: DateTimeFilter | None = None,
        end_time: DateTimeFilter | None = None,
        end_time_lt: DateTimeFilter | None = None,
        end_time_gt: DateTimeFilter | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> CallList:
        return CallList.model_validate(
            await self._t.request(
                "GET",
                self._path("Calls"),
                params=_list_params(
                    to=to,
                    from_=from_,
                    status=status,
                    parent_call_sid=parent_call_sid,
                    start_time=start_time,
                    start_time_lt=start_time_lt,
                    start_time_gt=start_time_gt,
                    end_time=end_time,
                    end_time_lt=end_time_lt,
                    end_time_gt=end_time_gt,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def iter(
        self,
        *,
        to: str | None = None,
        from_: str | None = None,
        status: str | None = None,
        parent_call_sid: str | None = None,
        start_time: DateTimeFilter | None = None,
        start_time_lt: DateTimeFilter | None = None,
        start_time_gt: DateTimeFilter | None = None,
        end_time: DateTimeFilter | None = None,
        end_time_lt: DateTimeFilter | None = None,
        end_time_gt: DateTimeFilter | None = None,
        page_size: int | None = None,
    ) -> AsyncIterator[Call]:
        """Lazily yield calls, following ``next_page_uri`` page by page."""
        first = await self.list(
            to=to,
            from_=from_,
            status=status,
            parent_call_sid=parent_call_sid,
            start_time=start_time,
            start_time_lt=start_time_lt,
            start_time_gt=start_time_gt,
            end_time=end_time,
            end_time_lt=end_time_lt,
            end_time_gt=end_time_gt,
            page_size=page_size,
        )
        async for item in self._paginate(first):
            yield item

    async def create(self, body: CreateCallRequest) -> Call:
        return Call.model_validate(
            await self._t.request("POST", self._path("Calls"), data=body.to_form())
        )

    async def get(self, call_sid: str) -> Call:
        return Call.model_validate(await self._t.request("GET", self._path("Calls", call_sid)))

    async def update(self, call_sid: str, body: UpdateCallRequest) -> Call:
        return Call.model_validate(
            await self._t.request("POST", self._path("Calls", call_sid), data=body.to_form())
        )

    async def delete(self, call_sid: str) -> None:
        await self._t.request("DELETE", self._path("Calls", call_sid))

    async def list_recordings(
        self,
        call_sid: str,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> RecordingList:
        return RecordingList.model_validate(
            await self._t.request(
                "GET",
                self._path("Calls", call_sid, "Recordings"),
                params=_recording_list_params(
                    date_created=date_created,
                    date_created_lt=date_created_lt,
                    date_created_gt=date_created_gt,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def start_recording(
        self, call_sid: str, body: StartRecordingRequest | None = None
    ) -> Recording:
        return Recording.model_validate(
            await self._t.request(
                "POST",
                self._path("Calls", call_sid, "Recordings"),
                data=body.to_form() if body else None,
            )
        )

    async def get_recording(self, call_sid: str, recording_sid: str) -> Recording:
        return Recording.model_validate(
            await self._t.request("GET", self._path("Calls", call_sid, "Recordings", recording_sid))
        )

    async def update_recording(
        self, call_sid: str, recording_sid: str, body: UpdateRecordingRequest
    ) -> Recording:
        return Recording.model_validate(
            await self._t.request(
                "POST",
                self._path("Calls", call_sid, "Recordings", recording_sid),
                data=body.to_form(),
            )
        )

    async def delete_recording(self, call_sid: str, recording_sid: str) -> None:
        await self._t.request("DELETE", self._path("Calls", call_sid, "Recordings", recording_sid))

    async def start_stream(self, call_sid: str, body: StartStreamRequest) -> Stream:
        return Stream.model_validate(
            await self._t.request(
                "POST", self._path("Calls", call_sid, "Streams"), data=body.to_form()
            )
        )

    async def stop_stream(
        self, call_sid: str, stream_sid: str, body: StopStreamRequest | None = None
    ) -> Stream:
        payload = (body or StopStreamRequest(status="stopped")).to_form()
        return Stream.model_validate(
            await self._t.request(
                "POST",
                self._path("Calls", call_sid, "Streams", stream_sid),
                data=payload,
            )
        )

    async def start_siprec(
        self, call_sid: str, body: StartSiprecRequest | None = None
    ) -> SiprecSession:
        return SiprecSession.model_validate(
            await self._t.request(
                "POST",
                self._path("Calls", call_sid, "Siprec"),
                data=body.to_form() if body else None,
            )
        )

    async def stop_siprec(
        self, call_sid: str, siprec_sid: str, body: StopSiprecRequest | None = None
    ) -> SiprecSession:
        payload = (body or StopSiprecRequest(status="stopped")).to_form()
        return SiprecSession.model_validate(
            await self._t.request(
                "POST", self._path("Calls", call_sid, "Siprec", siprec_sid), data=payload
            )
        )

    async def start_transcription(
        self, call_sid: str, body: StartTranscriptionRequest | None = None
    ) -> CallTranscription:
        return CallTranscription.model_validate(
            await self._t.request(
                "POST",
                self._path("Calls", call_sid, "Transcriptions"),
                data=body.to_form() if body else None,
            )
        )

    async def stop_transcription(
        self,
        call_sid: str,
        transcription_sid: str,
        body: StopTranscriptionRequest | None = None,
    ) -> CallTranscription:
        payload = (body or StopTranscriptionRequest(status="stopped")).to_form()
        return CallTranscription.model_validate(
            await self._t.request(
                "POST",
                self._path("Calls", call_sid, "Transcriptions", transcription_sid),
                data=payload,
            )
        )

    async def list_notifications(
        self,
        call_sid: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        log: NotificationLog | None = None,
        message_date: str | None = None,
        message_date_lt: str | None = None,
        message_date_gt: str | None = None,
    ) -> NotificationsList:
        return NotificationsList.model_validate(
            await self._t.request(
                "GET",
                self._path("Calls", call_sid, "Notifications"),
                params=_notification_list_params(
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

    async def get_notification(self, call_sid: str, notification_sid: str) -> Notification:
        return Notification.model_validate(
            await self._t.request(
                "GET", self._path("Calls", call_sid, "Notifications", notification_sid)
            )
        )

    async def list_events(
        self,
        call_sid: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> EventsList:
        return EventsList.model_validate(
            await self._t.request(
                "GET",
                self._path("Calls", call_sid, "Events"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def send_user_defined_message(self, call_sid: str) -> None:
        await self._t.request("POST", self._path("Calls", call_sid, "UserDefinedMessages"))

    async def start_payment(
        self,
        call_sid: str,
        *,
        idempotency_key: str | None = None,
        status_callback: str | None = None,
        bank_account_type: PaymentBankAccountType | None = None,
        charge_amount: str | None = None,
        currency: str | None = None,
        description: str | None = None,
        input: PaymentInput | None = None,
        min_postal_code_length: int | None = None,
        parameter: str | None = None,
        payment_connector: str | None = None,
        payment_method: PaymentMethod | None = None,
        postal_code: bool | None = None,
        security_code: bool | None = None,
        timeout: int | None = None,
        token_type: PaymentTokenType | None = None,
        valid_card_types: str | None = None,
        require_matching_inputs: str | None = None,
        confirmation: bool | None = None,
    ) -> CallPayment:
        return CallPayment.model_validate(
            await self._t.request(
                "POST",
                self._path("Calls", call_sid, "Payments"),
                data=_start_payment_form(
                    idempotency_key=idempotency_key,
                    status_callback=status_callback,
                    bank_account_type=bank_account_type,
                    charge_amount=charge_amount,
                    currency=currency,
                    description=description,
                    input=input,
                    min_postal_code_length=min_postal_code_length,
                    parameter=parameter,
                    payment_connector=payment_connector,
                    payment_method=payment_method,
                    postal_code=postal_code,
                    security_code=security_code,
                    timeout=timeout,
                    token_type=token_type,
                    valid_card_types=valid_card_types,
                    require_matching_inputs=require_matching_inputs,
                    confirmation=confirmation,
                ),
            )
        )

    async def update_payment(
        self,
        call_sid: str,
        payment_sid: str,
        *,
        idempotency_key: str | None = None,
        status_callback: str | None = None,
        capture: PaymentCapture | None = None,
        status: PaymentSessionStatus | None = None,
    ) -> CallPayment:
        return CallPayment.model_validate(
            await self._t.request(
                "POST",
                self._path("Calls", call_sid, "Payments", payment_sid),
                data=_update_payment_form(
                    idempotency_key=idempotency_key,
                    status_callback=status_callback,
                    capture=capture,
                    status=status,
                ),
            )
        )
