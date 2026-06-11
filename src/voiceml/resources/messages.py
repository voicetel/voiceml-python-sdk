"""``/Messages`` REST resource — Twilio-compatible outbound SMS.

The wire surface is fire-and-forget today: ``status`` pins to ``"sent"`` on
successful dispatch and ``"failed"`` otherwise. No MMS, no inbound webhook
delivery, no in-flight ``queued``/``sending``/``delivered`` lifecycle.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import cast

from ..models import (
    CreateMessageRequest,
    Message,
    MessageList,
    UpdateMessageRequest,
    UpdateMessageStatus,
)
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


def _build_create_form(
    *,
    to: str,
    body: str,
    from_: str | None,
    messaging_service_sid: str | None,
    status_callback: str | None,
) -> dict[str, object]:
    return CreateMessageRequest(
        To=to,
        Body=body,
        From=from_,
        MessagingServiceSid=messaging_service_sid,
        StatusCallback=status_callback,
    ).to_form()


def _build_update_form(
    *, body: str | None, status: str | None
) -> dict[str, object]:
    req = UpdateMessageRequest(
        Body=body,
        Status=cast("UpdateMessageStatus | None", status),
    )
    # ``to_form()`` already drops ``None``, but Body="" is a meaningful
    # redaction request that must round-trip — and exclude_unset filtering
    # in to_form() relies on us only setting the kwargs the caller passed.
    return req.to_form()


class MessagesResource(Resource):
    """Operations on the account-scoped ``/Messages`` collection."""

    def create(
        self,
        *,
        to: str,
        body: str,
        from_: str | None = None,
        messaging_service_sid: str | None = None,
        status_callback: str | None = None,
    ) -> Message:
        """Dispatch an outbound SMS.

        ``to`` and ``body`` are required; ``from_`` falls back to the
        tenant's configured default sender when omitted.
        """
        return Message.model_validate(
            self._t.request(
                "POST",
                self._path("Messages"),
                data=_build_create_form(
                    to=to,
                    body=body,
                    from_=from_,
                    messaging_service_sid=messaging_service_sid,
                    status_callback=status_callback,
                ),
            )
        )

    def fetch(self, message_sid: str) -> Message:
        """Fetch a previously-sent Message by sid."""
        return Message.model_validate(
            self._t.request("GET", self._path("Messages", message_sid))
        )

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

    def update(
        self,
        message_sid: str,
        *,
        body: str | None = None,
        status: str | None = None,
    ) -> Message:
        """Mutate an existing Message — redact ``body`` or attempt cancel.

        Only ``body=""`` (redaction) is honoured by the server today;
        ``status="canceled"`` returns 21610 because the gateway is
        fire-and-forget.
        """
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

    def iter(
        self,
        *,
        to: str | None = None,
        from_: str | None = None,
        date_sent: str | None = None,
        date_sent_lt: str | None = None,
        date_sent_gt: str | None = None,
        page_size: int | None = None,
    ) -> Sequence[Message]:
        """Walk all pages of ``/Messages`` and return a list.

        Use for small-to-medium result sets; for very large pulls, iterate
        ``list(...).next_page_uri`` manually.
        """
        out: list[Message] = []
        page = 0
        while True:
            chunk = self.list(
                to=to,
                from_=from_,
                date_sent=date_sent,
                date_sent_lt=date_sent_lt,
                date_sent_gt=date_sent_gt,
                page=page,
                page_size=page_size,
            )
            out.extend(chunk.messages)
            if not chunk.next_page_uri or not chunk.messages:
                return out
            page += 1


class MessagesAsyncResource(AsyncResource):
    """Async counterpart to :class:`MessagesResource`."""

    async def create(
        self,
        *,
        to: str,
        body: str,
        from_: str | None = None,
        messaging_service_sid: str | None = None,
        status_callback: str | None = None,
    ) -> Message:
        return Message.model_validate(
            await self._t.request(
                "POST",
                self._path("Messages"),
                data=_build_create_form(
                    to=to,
                    body=body,
                    from_=from_,
                    messaging_service_sid=messaging_service_sid,
                    status_callback=status_callback,
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

    async def update(
        self,
        message_sid: str,
        *,
        body: str | None = None,
        status: str | None = None,
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
