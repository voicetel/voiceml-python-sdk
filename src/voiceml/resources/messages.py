"""``/Messages`` REST resource — Twilio-compatible outbound SMS / MMS, plus the
per-message ``/Media`` sub-resource."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Sequence
from datetime import datetime

from ..models import (
    CreateMessageFeedbackRequest,
    CreateMessageRequest,
    Media,
    MediaList,
    Message,
    MessageFeedback,
    MessageList,
    UpdateMessageRequest,
    UpdateMessageStatus,
)
from ..models.messages import HttpMethod, MessageFeedbackOutcome, ScheduleType
from ._base import AsyncResource, Resource


def _list_params(
    *,
    to: str | None,
    from_: str | None,
    date_sent: str | None,
    date_sent_lt: str | None,
    date_sent_gt: str | None,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
) -> dict[str, object]:
    return {
        "To": to,
        "From": from_,
        "DateSent": date_sent,
        "DateSent<": date_sent_lt,
        "DateSent>": date_sent_gt,
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
    }


def _media_list_params(
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


def _build_create_form(
    *,
    to: str,
    body: str | None,
    from_: str | None,
    media_url: Sequence[str] | None,
    messaging_service_sid: str | None,
    validity_period: int | None,
    status_callback: str | None,
    status_callback_method: HttpMethod | None,
    send_at: datetime | None,
    schedule_type: ScheduleType | None,
) -> dict[str, object]:
    return CreateMessageRequest(
        to=to,
        body=body,
        from_=from_,
        media_url=list(media_url) if media_url is not None else None,
        messaging_service_sid=messaging_service_sid,
        validity_period=validity_period,
        status_callback=status_callback,
        status_callback_method=status_callback_method,
        send_at=send_at,
        schedule_type=schedule_type,
    ).to_form()


def _build_update_form(
    *, body: str | None, status: UpdateMessageStatus | None
) -> dict[str, object]:
    # ``to_form()`` drops ``None`` but keeps ``body=""``, which is a meaningful
    # redaction request that must round-trip.
    return UpdateMessageRequest(body=body, status=status).to_form()


class MessagesResource(Resource):
    """Operations on the account-scoped ``/Messages`` collection."""

    def create(
        self,
        *,
        to: str,
        body: str | None = None,
        from_: str | None = None,
        media_url: Sequence[str] | None = None,
        messaging_service_sid: str | None = None,
        validity_period: int | None = None,
        status_callback: str | None = None,
        status_callback_method: HttpMethod | None = None,
        send_at: datetime | None = None,
        schedule_type: ScheduleType | None = None,
    ) -> Message:
        """Send an SMS (``body``) or MMS (``media_url``, optionally with ``body``).

        At least one of ``body`` / ``media_url`` is required (checked before any
        request is made). ``from_`` falls back to the tenant's configured default
        sender when omitted. Never retried on 5xx or read timeouts.

        ``send_at`` schedules the message for a future UTC time; the server requires
        ``schedule_type`` (``"fixed"``) and ``messaging_service_sid`` alongside it.
        """
        return Message.model_validate(
            self._t.request(
                "POST",
                self._path("Messages"),
                data=_build_create_form(
                    to=to,
                    body=body,
                    from_=from_,
                    media_url=media_url,
                    messaging_service_sid=messaging_service_sid,
                    validity_period=validity_period,
                    status_callback=status_callback,
                    status_callback_method=status_callback_method,
                    send_at=send_at,
                    schedule_type=schedule_type,
                ),
            )
        )

    def fetch(self, message_sid: str) -> Message:
        """Fetch a previously-sent Message by sid."""
        return Message.model_validate(self._t.request("GET", self._path("Messages", message_sid)))

    def list(
        self,
        *,
        to: str | None = None,
        from_: str | None = None,
        date_sent: str | None = None,
        date_sent_lt: str | None = None,
        date_sent_gt: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> MessageList:
        """Return a single page of Messages, optionally filtered."""
        return MessageList.model_validate(
            self._t.request(
                "GET",
                self._path("Messages"),
                params=_list_params(
                    to=to,
                    from_=from_,
                    date_sent=date_sent,
                    date_sent_lt=date_sent_lt,
                    date_sent_gt=date_sent_gt,
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
        date_sent: str | None = None,
        date_sent_lt: str | None = None,
        date_sent_gt: str | None = None,
        page_size: int | None = None,
    ) -> Iterator[Message]:
        """Lazily yield messages, following ``next_page_uri`` page by page.

        One request per page, issued as the iterator is consumed; stopping early
        issues no further requests.
        """
        yield from self._paginate(
            self.list(
                to=to,
                from_=from_,
                date_sent=date_sent,
                date_sent_lt=date_sent_lt,
                date_sent_gt=date_sent_gt,
                page_size=page_size,
            )
        )

    def update(
        self,
        message_sid: str,
        *,
        body: str | None = None,
        status: UpdateMessageStatus | None = None,
    ) -> Message:
        """Mutate an existing Message — redact with ``body=""`` or cancel a scheduled
        send with ``status="canceled"``."""
        return Message.model_validate(
            self._t.request(
                "POST",
                self._path("Messages", message_sid),
                data=_build_update_form(body=body, status=status),
            )
        )

    def delete(self, message_sid: str) -> None:
        """Remove a Message resource from the account's store."""
        self._t.request("DELETE", self._path("Messages", message_sid))

    def create_feedback(
        self, message_sid: str, *, outcome: MessageFeedbackOutcome | None = None
    ) -> MessageFeedback:
        """Submit delivery feedback for a Message.

        ``outcome="confirmed"`` marks the message as delivered; anything else
        (including omitting it) is recorded as ``unconfirmed``. The response
        echoes the Feedback resource.
        """
        body = CreateMessageFeedbackRequest(outcome=outcome).to_form()
        return MessageFeedback.model_validate(
            self._t.request("POST", self._path("Messages", message_sid, "Feedback"), data=body)
        )

    # --- Media ---

    def list_media(
        self,
        message_sid: str,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> MediaList:
        """List the media attached to a message."""
        return MediaList.model_validate(
            self._t.request(
                "GET",
                self._path("Messages", message_sid, "Media"),
                params=_media_list_params(
                    date_created=date_created,
                    date_created_lt=date_created_lt,
                    date_created_gt=date_created_gt,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def get_media(self, message_sid: str, media_sid: str) -> Media:
        """Fetch one media item's metadata."""
        return Media.model_validate(
            self._t.request("GET", self._path("Messages", message_sid, "Media", media_sid))
        )

    def delete_media(self, message_sid: str, media_sid: str) -> None:
        """Delete one media item from a message."""
        self._t.request("DELETE", self._path("Messages", message_sid, "Media", media_sid))


class MessagesAsyncResource(AsyncResource):
    """Async counterpart to :class:`MessagesResource`."""

    async def create(
        self,
        *,
        to: str,
        body: str | None = None,
        from_: str | None = None,
        media_url: Sequence[str] | None = None,
        messaging_service_sid: str | None = None,
        validity_period: int | None = None,
        status_callback: str | None = None,
        status_callback_method: HttpMethod | None = None,
        send_at: datetime | None = None,
        schedule_type: ScheduleType | None = None,
    ) -> Message:
        return Message.model_validate(
            await self._t.request(
                "POST",
                self._path("Messages"),
                data=_build_create_form(
                    to=to,
                    body=body,
                    from_=from_,
                    media_url=media_url,
                    messaging_service_sid=messaging_service_sid,
                    validity_period=validity_period,
                    status_callback=status_callback,
                    status_callback_method=status_callback_method,
                    send_at=send_at,
                    schedule_type=schedule_type,
                ),
            )
        )

    async def fetch(self, message_sid: str) -> Message:
        return Message.model_validate(
            await self._t.request("GET", self._path("Messages", message_sid))
        )

    async def list(
        self,
        *,
        to: str | None = None,
        from_: str | None = None,
        date_sent: str | None = None,
        date_sent_lt: str | None = None,
        date_sent_gt: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> MessageList:
        return MessageList.model_validate(
            await self._t.request(
                "GET",
                self._path("Messages"),
                params=_list_params(
                    to=to,
                    from_=from_,
                    date_sent=date_sent,
                    date_sent_lt=date_sent_lt,
                    date_sent_gt=date_sent_gt,
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
        date_sent: str | None = None,
        date_sent_lt: str | None = None,
        date_sent_gt: str | None = None,
        page_size: int | None = None,
    ) -> AsyncIterator[Message]:
        """Lazily yield messages, following ``next_page_uri`` page by page."""
        first = await self.list(
            to=to,
            from_=from_,
            date_sent=date_sent,
            date_sent_lt=date_sent_lt,
            date_sent_gt=date_sent_gt,
            page_size=page_size,
        )
        async for item in self._paginate(first):
            yield item

    async def update(
        self,
        message_sid: str,
        *,
        body: str | None = None,
        status: UpdateMessageStatus | None = None,
    ) -> Message:
        return Message.model_validate(
            await self._t.request(
                "POST",
                self._path("Messages", message_sid),
                data=_build_update_form(body=body, status=status),
            )
        )

    async def delete(self, message_sid: str) -> None:
        await self._t.request("DELETE", self._path("Messages", message_sid))

    async def create_feedback(
        self, message_sid: str, *, outcome: MessageFeedbackOutcome | None = None
    ) -> MessageFeedback:
        """Submit delivery feedback for a Message (see the sync counterpart)."""
        body = CreateMessageFeedbackRequest(outcome=outcome).to_form()
        return MessageFeedback.model_validate(
            await self._t.request(
                "POST", self._path("Messages", message_sid, "Feedback"), data=body
            )
        )

    async def list_media(
        self,
        message_sid: str,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> MediaList:
        return MediaList.model_validate(
            await self._t.request(
                "GET",
                self._path("Messages", message_sid, "Media"),
                params=_media_list_params(
                    date_created=date_created,
                    date_created_lt=date_created_lt,
                    date_created_gt=date_created_gt,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def get_media(self, message_sid: str, media_sid: str) -> Media:
        return Media.model_validate(
            await self._t.request("GET", self._path("Messages", message_sid, "Media", media_sid))
        )

    async def delete_media(self, message_sid: str, media_sid: str) -> None:
        await self._t.request("DELETE", self._path("Messages", message_sid, "Media", media_sid))
