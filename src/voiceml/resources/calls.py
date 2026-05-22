"""``/Calls`` and call-scoped sub-resources (Recordings, Streams, Siprec, Transcriptions,
Notifications, Events, UserDefinedMessages)."""

from __future__ import annotations

from collections.abc import Sequence

from ..models import (
    Call,
    CallList,
    CallTranscription,
    CreateCallRequest,
    EventsList,
    NotificationsList,
    Recording,
    RecordingList,
    SiprecList,
    SiprecSession,
    StartRecordingRequest,
    StartSiprecRequest,
    StartStreamRequest,
    StartTranscriptionRequest,
    StopSiprecRequest,
    StopStreamRequest,
    StopTranscriptionRequest,
    Stream,
    StreamList,
    TranscriptionList,
    UpdateCallRequest,
    UpdateRecordingRequest,
)
from ._base import AsyncResource, Resource


def _list_params(
    *,
    to: str | None,
    from_: str | None,
    status: str | None,
    parent_call_sid: str | None,
    start_time: str | None,
    start_time_lt: str | None,
    start_time_gt: str | None,
    end_time: str | None,
    end_time_lt: str | None,
    end_time_gt: str | None,
    start_time_gte: str | None,
    start_time_lte: str | None,
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
        "StartTime>=": start_time_gte,
        "StartTime<=": start_time_lte,
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


def _page_params(
    *, page: int | None, page_size: int | None, page_token: str | None
) -> dict[str, object]:
    return {"Page": page, "PageSize": page_size, "PageToken": page_token}


class CallsResource(Resource):
    """Operations on calls and call-scoped sub-resources."""

    def list(
        self,
        *,
        to: str | None = None,
        from_: str | None = None,
        status: str | None = None,
        parent_call_sid: str | None = None,
        start_time: str | None = None,
        start_time_lt: str | None = None,
        start_time_gt: str | None = None,
        end_time: str | None = None,
        end_time_lt: str | None = None,
        end_time_gt: str | None = None,
        start_time_gte: str | None = None,
        start_time_lte: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> CallList:
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
                    start_time_gte=start_time_gte,
                    start_time_lte=start_time_lte,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def create(self, body: CreateCallRequest) -> Call:
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
        return Recording.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Recordings", recording_sid),
                data=body.to_form(),
            )
        )

    def delete_recording(self, call_sid: str, recording_sid: str) -> None:
        self._t.request("DELETE", self._path("Calls", call_sid, "Recordings", recording_sid))

    # --- Streams ---

    def list_streams(self, call_sid: str) -> StreamList:
        return StreamList.model_validate(
            self._t.request("GET", self._path("Calls", call_sid, "Streams"))
        )

    def start_stream(self, call_sid: str, body: StartStreamRequest) -> Stream:
        return Stream.model_validate(
            self._t.request(
                "POST", self._path("Calls", call_sid, "Streams"), data=body.to_form()
            )
        )

    def get_stream(self, call_sid: str, stream_sid: str) -> Stream:
        return Stream.model_validate(
            self._t.request("GET", self._path("Calls", call_sid, "Streams", stream_sid))
        )

    def stop_stream(
        self, call_sid: str, stream_sid: str, body: StopStreamRequest | None = None
    ) -> Stream:
        payload = (body or StopStreamRequest(Status="stopped")).to_form()
        return Stream.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Streams", stream_sid),
                data=payload,
            )
        )

    # --- SIPREC ---

    def list_siprec(self, call_sid: str) -> SiprecList:
        return SiprecList.model_validate(
            self._t.request("GET", self._path("Calls", call_sid, "Siprec"))
        )

    def start_siprec(
        self, call_sid: str, body: StartSiprecRequest | None = None
    ) -> SiprecSession:
        return SiprecSession.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Siprec"),
                data=body.to_form() if body else None,
            )
        )

    def get_siprec(self, call_sid: str, siprec_sid: str) -> SiprecSession:
        return SiprecSession.model_validate(
            self._t.request("GET", self._path("Calls", call_sid, "Siprec", siprec_sid))
        )

    def stop_siprec(
        self, call_sid: str, siprec_sid: str, body: StopSiprecRequest | None = None
    ) -> SiprecSession:
        payload = (body or StopSiprecRequest(Status="stopped")).to_form()
        return SiprecSession.model_validate(
            self._t.request(
                "POST", self._path("Calls", call_sid, "Siprec", siprec_sid), data=payload
            )
        )

    # --- Transcriptions ---

    def list_transcriptions(self, call_sid: str) -> TranscriptionList:
        return TranscriptionList.model_validate(
            self._t.request("GET", self._path("Calls", call_sid, "Transcriptions"))
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

    def get_transcription(self, call_sid: str, transcription_sid: str) -> CallTranscription:
        return CallTranscription.model_validate(
            self._t.request(
                "GET", self._path("Calls", call_sid, "Transcriptions", transcription_sid)
            )
        )

    def stop_transcription(
        self,
        call_sid: str,
        transcription_sid: str,
        body: StopTranscriptionRequest | None = None,
    ) -> CallTranscription:
        payload = (body or StopTranscriptionRequest(Status="stopped")).to_form()
        return CallTranscription.model_validate(
            self._t.request(
                "POST",
                self._path("Calls", call_sid, "Transcriptions", transcription_sid),
                data=payload,
            )
        )

    # --- Notifications / Events (compat stubs) ---

    def list_notifications(
        self,
        call_sid: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> NotificationsList:
        return NotificationsList.model_validate(
            self._t.request(
                "GET",
                self._path("Calls", call_sid, "Notifications"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
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

    def send_user_defined_message(
        self, call_sid: str, payload: dict[str, object] | None = None
    ) -> None:
        """``POST /Calls/{sid}/UserDefinedMessages`` — always raises ``NotImplementedAPIError``.

        Mounted on the server only as a 501 stub. The SDK forwards the call so callers get a
        clean exception rather than discovering at runtime that the endpoint doesn't exist.
        """
        self._t.request(
            "POST",
            self._path("Calls", call_sid, "UserDefinedMessages"),
            data=payload,
        )

    # Helper for auto-pagination

    def iter(
        self,
        *,
        to: str | None = None,
        from_: str | None = None,
        status: str | None = None,
        parent_call_sid: str | None = None,
        start_time: str | None = None,
        start_time_lt: str | None = None,
        start_time_gt: str | None = None,
        end_time: str | None = None,
        end_time_lt: str | None = None,
        end_time_gt: str | None = None,
        start_time_gte: str | None = None,
        start_time_lte: str | None = None,
        page_size: int | None = None,
    ) -> Sequence[Call]:
        """Walk all pages of ``/Calls`` and return a list. Use for small-to-medium result sets;
        for very large pulls, iterate ``list(...).next_page_uri`` manually.
        """
        out: list[Call] = []
        page = 0
        while True:
            chunk = self.list(
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
                start_time_gte=start_time_gte,
                start_time_lte=start_time_lte,
                page=page,
                page_size=page_size,
            )
            out.extend(chunk.calls)
            if not chunk.next_page_uri or not chunk.calls:
                return out
            page += 1


class CallsAsyncResource(AsyncResource):
    """Async counterpart to :class:`CallsResource`."""

    async def list(
        self,
        *,
        to: str | None = None,
        from_: str | None = None,
        status: str | None = None,
        parent_call_sid: str | None = None,
        start_time: str | None = None,
        start_time_lt: str | None = None,
        start_time_gt: str | None = None,
        end_time: str | None = None,
        end_time_lt: str | None = None,
        end_time_gt: str | None = None,
        start_time_gte: str | None = None,
        start_time_lte: str | None = None,
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
                    start_time_gte=start_time_gte,
                    start_time_lte=start_time_lte,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

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
            await self._t.request(
                "GET", self._path("Calls", call_sid, "Recordings", recording_sid)
            )
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
        await self._t.request(
            "DELETE", self._path("Calls", call_sid, "Recordings", recording_sid)
        )

    async def list_streams(self, call_sid: str) -> StreamList:
        return StreamList.model_validate(
            await self._t.request("GET", self._path("Calls", call_sid, "Streams"))
        )

    async def start_stream(self, call_sid: str, body: StartStreamRequest) -> Stream:
        return Stream.model_validate(
            await self._t.request(
                "POST", self._path("Calls", call_sid, "Streams"), data=body.to_form()
            )
        )

    async def get_stream(self, call_sid: str, stream_sid: str) -> Stream:
        return Stream.model_validate(
            await self._t.request("GET", self._path("Calls", call_sid, "Streams", stream_sid))
        )

    async def stop_stream(
        self, call_sid: str, stream_sid: str, body: StopStreamRequest | None = None
    ) -> Stream:
        payload = (body or StopStreamRequest(Status="stopped")).to_form()
        return Stream.model_validate(
            await self._t.request(
                "POST",
                self._path("Calls", call_sid, "Streams", stream_sid),
                data=payload,
            )
        )

    async def list_siprec(self, call_sid: str) -> SiprecList:
        return SiprecList.model_validate(
            await self._t.request("GET", self._path("Calls", call_sid, "Siprec"))
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

    async def get_siprec(self, call_sid: str, siprec_sid: str) -> SiprecSession:
        return SiprecSession.model_validate(
            await self._t.request("GET", self._path("Calls", call_sid, "Siprec", siprec_sid))
        )

    async def stop_siprec(
        self, call_sid: str, siprec_sid: str, body: StopSiprecRequest | None = None
    ) -> SiprecSession:
        payload = (body or StopSiprecRequest(Status="stopped")).to_form()
        return SiprecSession.model_validate(
            await self._t.request(
                "POST", self._path("Calls", call_sid, "Siprec", siprec_sid), data=payload
            )
        )

    async def list_transcriptions(self, call_sid: str) -> TranscriptionList:
        return TranscriptionList.model_validate(
            await self._t.request("GET", self._path("Calls", call_sid, "Transcriptions"))
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

    async def get_transcription(
        self, call_sid: str, transcription_sid: str
    ) -> CallTranscription:
        return CallTranscription.model_validate(
            await self._t.request(
                "GET", self._path("Calls", call_sid, "Transcriptions", transcription_sid)
            )
        )

    async def stop_transcription(
        self,
        call_sid: str,
        transcription_sid: str,
        body: StopTranscriptionRequest | None = None,
    ) -> CallTranscription:
        payload = (body or StopTranscriptionRequest(Status="stopped")).to_form()
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
    ) -> NotificationsList:
        return NotificationsList.model_validate(
            await self._t.request(
                "GET",
                self._path("Calls", call_sid, "Notifications"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
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

    async def send_user_defined_message(
        self, call_sid: str, payload: dict[str, object] | None = None
    ) -> None:
        await self._t.request(
            "POST",
            self._path("Calls", call_sid, "UserDefinedMessages"),
            data=payload,
        )
