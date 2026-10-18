"""Account-scoped ``/Recordings`` operations.

Per-call recording start/stop/list lives on :class:`voiceml.resources.CallsResource` — this
resource handles the account-wide list, single-recording fetch (both metadata and audio),
and delete.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from ..models import (
    Recording,
    RecordingAudio,
    RecordingList,
    RecordingTranscription,
    RecordingTranscriptionList,
)
from ._base import AsyncResource, Resource, account_path
from .transcriptions import transcription_list_params

AUDIO_ACCEPT = "audio/*, */*"


def _list_params(
    *,
    date_created: str | None,
    date_created_lt: str | None,
    date_created_gt: str | None,
    call_sid: str | None,
    conference_sid: str | None,
    include_soft_deleted: bool | None,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
) -> dict[str, object]:
    return {
        "DateCreated": date_created,
        "DateCreated<": date_created_lt,
        "DateCreated>": date_created_gt,
        "CallSid": call_sid,
        "ConferenceSid": conference_sid,
        "IncludeSoftDeleted": include_soft_deleted,
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
    }


def _get_params(*, include_soft_deleted: bool | None) -> dict[str, object]:
    return {"IncludeSoftDeleted": include_soft_deleted}


class RecordingsResource(Resource):
    def list(
        self,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        call_sid: str | None = None,
        conference_sid: str | None = None,
        include_soft_deleted: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> RecordingList:
        return RecordingList.model_validate(
            self._t.request(
                "GET",
                self._path("Recordings"),
                params=_list_params(
                    date_created=date_created,
                    date_created_lt=date_created_lt,
                    date_created_gt=date_created_gt,
                    call_sid=call_sid,
                    conference_sid=conference_sid,
                    include_soft_deleted=include_soft_deleted,
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
        call_sid: str | None = None,
        conference_sid: str | None = None,
        include_soft_deleted: bool | None = None,
        page_size: int | None = None,
    ) -> Iterator[Recording]:
        """Lazily yield recordings, following ``next_page_uri`` page by page.

        One request per page, issued as the iterator is consumed; stopping early
        issues no further requests.
        """
        yield from self._paginate(
            self.list(
                date_created=date_created,
                date_created_lt=date_created_lt,
                date_created_gt=date_created_gt,
                call_sid=call_sid,
                conference_sid=conference_sid,
                include_soft_deleted=include_soft_deleted,
                page_size=page_size,
            )
        )

    def get(self, recording_sid: str, *, include_soft_deleted: bool | None = None) -> Recording:
        """Fetch the metadata JSON for a recording."""
        return Recording.model_validate(
            self._t.request(
                "GET",
                self._path("Recordings", recording_sid),
                params=_get_params(include_soft_deleted=include_soft_deleted),
            )
        )

    def get_audio(self, recording_sid: str) -> RecordingAudio:
        """Fetch the WAV audio for a recording.

        Three server delivery shapes are flattened into one result by following any 302
        redirect to S3:
          * ``200 OK`` — local file present.
          * ``302 Found`` — archived to S3; the SDK follows the presigned URL.
          * ``410 Gone`` — local file gone AND no S3 key. Raises :class:`voiceml.GoneError`.
        """
        result = self._t.fetch_bytes(
            account_path(self._acct, "Recordings", recording_sid, suffix=".wav"),
            accept=AUDIO_ACCEPT,
        )
        return RecordingAudio(
            sid=recording_sid,
            content=result.content,
            content_type=result.headers.get("content-type", "application/octet-stream"),
            via_redirect=result.redirected,
        )

    def delete(self, recording_sid: str) -> None:
        self._t.request("DELETE", self._path("Recordings", recording_sid))

    # --- Transcriptions of a recording ---

    def list_transcriptions(
        self,
        recording_sid: str,
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
                self._path("Recordings", recording_sid, "Transcriptions"),
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

    def get_transcription(
        self, recording_sid: str, transcription_sid: str
    ) -> RecordingTranscription:
        return RecordingTranscription.model_validate(
            self._t.request(
                "GET",
                self._path("Recordings", recording_sid, "Transcriptions", transcription_sid),
            )
        )

    def delete_transcription(self, recording_sid: str, transcription_sid: str) -> None:
        self._t.request(
            "DELETE",
            self._path("Recordings", recording_sid, "Transcriptions", transcription_sid),
        )


class RecordingsAsyncResource(AsyncResource):
    async def list(
        self,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        call_sid: str | None = None,
        conference_sid: str | None = None,
        include_soft_deleted: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> RecordingList:
        return RecordingList.model_validate(
            await self._t.request(
                "GET",
                self._path("Recordings"),
                params=_list_params(
                    date_created=date_created,
                    date_created_lt=date_created_lt,
                    date_created_gt=date_created_gt,
                    call_sid=call_sid,
                    conference_sid=conference_sid,
                    include_soft_deleted=include_soft_deleted,
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
        call_sid: str | None = None,
        conference_sid: str | None = None,
        include_soft_deleted: bool | None = None,
        page_size: int | None = None,
    ) -> AsyncIterator[Recording]:
        """Lazily yield recordings, following ``next_page_uri`` page by page.

        One request per page, issued as the iterator is consumed; stopping early
        issues no further requests.
        """
        first = await self.list(
            date_created=date_created,
            date_created_lt=date_created_lt,
            date_created_gt=date_created_gt,
            call_sid=call_sid,
            conference_sid=conference_sid,
            include_soft_deleted=include_soft_deleted,
            page_size=page_size,
        )
        async for item in self._paginate(first):
            yield item

    async def get(
        self, recording_sid: str, *, include_soft_deleted: bool | None = None
    ) -> Recording:
        return Recording.model_validate(
            await self._t.request(
                "GET",
                self._path("Recordings", recording_sid),
                params=_get_params(include_soft_deleted=include_soft_deleted),
            )
        )

    async def get_audio(self, recording_sid: str) -> RecordingAudio:
        result = await self._t.fetch_bytes(
            account_path(self._acct, "Recordings", recording_sid, suffix=".wav"),
            accept=AUDIO_ACCEPT,
        )
        return RecordingAudio(
            sid=recording_sid,
            content=result.content,
            content_type=result.headers.get("content-type", "application/octet-stream"),
            via_redirect=result.redirected,
        )

    async def delete(self, recording_sid: str) -> None:
        await self._t.request("DELETE", self._path("Recordings", recording_sid))

    # --- Transcriptions of a recording ---

    async def list_transcriptions(
        self,
        recording_sid: str,
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
                self._path("Recordings", recording_sid, "Transcriptions"),
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

    async def get_transcription(
        self, recording_sid: str, transcription_sid: str
    ) -> RecordingTranscription:
        return RecordingTranscription.model_validate(
            await self._t.request(
                "GET",
                self._path("Recordings", recording_sid, "Transcriptions", transcription_sid),
            )
        )

    async def delete_transcription(self, recording_sid: str, transcription_sid: str) -> None:
        await self._t.request(
            "DELETE",
            self._path("Recordings", recording_sid, "Transcriptions", transcription_sid),
        )
