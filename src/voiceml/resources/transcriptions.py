"""Account-scoped ``/Transcriptions`` (recording transcriptions, ``TR…``).

Per-recording transcriptions are on ``client.recordings`` (``list_transcriptions``,
``get_transcription``, ``delete_transcription``); live call transcriptions are started
and stopped through ``client.calls``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from ..models import RecordingTranscription, RecordingTranscriptionList
from ._base import AsyncResource, Resource


def transcription_list_params(
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


class TranscriptionsResource(Resource):
    """``client.transcriptions``."""

    def list(
        self,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> RecordingTranscriptionList:
        return RecordingTranscriptionList.model_validate(
            self._t.request(
                "GET",
                self._path("Transcriptions"),
                params=transcription_list_params(
                    date_created=date_created,
                    date_created_lt=date_created_lt,
                    date_created_gt=date_created_gt,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def iter(
        self,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        page_size: int | None = None,
    ) -> Iterator[RecordingTranscription]:
        """Lazily yield transcriptions, following ``next_page_uri`` page by page."""
        yield from self._paginate(
            self.list(
                date_created=date_created,
                date_created_lt=date_created_lt,
                date_created_gt=date_created_gt,
                page_size=page_size,
            )
        )

    def get(self, sid: str) -> RecordingTranscription:
        return RecordingTranscription.model_validate(
            self._t.request("GET", self._path("Transcriptions", sid))
        )

    def delete(self, sid: str) -> None:
        self._t.request("DELETE", self._path("Transcriptions", sid))


class TranscriptionsAsyncResource(AsyncResource):
    """Async counterpart to :class:`TranscriptionsResource`."""

    async def list(
        self,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> RecordingTranscriptionList:
        return RecordingTranscriptionList.model_validate(
            await self._t.request(
                "GET",
                self._path("Transcriptions"),
                params=transcription_list_params(
                    date_created=date_created,
                    date_created_lt=date_created_lt,
                    date_created_gt=date_created_gt,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def iter(
        self,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        page_size: int | None = None,
    ) -> AsyncIterator[RecordingTranscription]:
        """Lazily yield transcriptions, following ``next_page_uri`` page by page."""
        first = await self.list(
            date_created=date_created,
            date_created_lt=date_created_lt,
            date_created_gt=date_created_gt,
            page_size=page_size,
        )
        async for item in self._paginate(first):
            yield item

    async def get(self, sid: str) -> RecordingTranscription:
        return RecordingTranscription.model_validate(
            await self._t.request("GET", self._path("Transcriptions", sid))
        )

    async def delete(self, sid: str) -> None:
        await self._t.request("DELETE", self._path("Transcriptions", sid))
