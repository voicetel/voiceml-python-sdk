"""Account-scoped ``/Recordings`` operations.

Per-call recording start/stop/list lives on :class:`voiceml.resources.CallsResource` — this
resource handles the account-wide list, single-recording fetch (both metadata and audio),
and delete.
"""

from __future__ import annotations

from ..models import Recording, RecordingAudio, RecordingList
from ._base import AsyncResource, Resource


def _list_params(
    *,
    date_created: str | None,
    date_created_lt: str | None,
    date_created_gt: str | None,
    call_sid: str | None,
    conference_sid: str | None,
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
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
    }


class RecordingsResource(Resource):
    def list(
        self,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        call_sid: str | None = None,
        conference_sid: str | None = None,
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
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def get(self, recording_sid: str) -> Recording:
        """Fetch the metadata JSON for a recording."""
        return Recording.model_validate(
            self._t.request("GET", self._path("Recordings", recording_sid))
        )

    def get_audio(self, recording_sid: str) -> RecordingAudio:
        """Fetch the WAV audio for a recording.

        Three server delivery shapes are flattened into one result by following any 302
        redirect to S3:
          * ``200 OK`` — local file present.
          * ``302 Found`` — archived to S3; the SDK follows the presigned URL.
          * ``410 Gone`` — local file gone AND no S3 key. Raises :class:`voiceml.GoneError`.
        """
        status, content, headers = self._t.fetch_bytes(
            self._path("Recordings", recording_sid + ".wav")
        )
        return RecordingAudio(
            sid=recording_sid,
            content=content,
            content_type=headers.get("content-type", "application/octet-stream"),
            via_redirect=status == 200 and "x-amz-id-2" in headers,
        )

    def delete(self, recording_sid: str) -> None:
        self._t.request("DELETE", self._path("Recordings", recording_sid))


class RecordingsAsyncResource(AsyncResource):
    async def list(
        self,
        *,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        call_sid: str | None = None,
        conference_sid: str | None = None,
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
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def get(self, recording_sid: str) -> Recording:
        return Recording.model_validate(
            await self._t.request("GET", self._path("Recordings", recording_sid))
        )

    async def get_audio(self, recording_sid: str) -> RecordingAudio:
        status, content, headers = await self._t.fetch_bytes(
            self._path("Recordings", recording_sid + ".wav")
        )
        return RecordingAudio(
            sid=recording_sid,
            content=content,
            content_type=headers.get("content-type", "application/octet-stream"),
            via_redirect=status == 200 and "x-amz-id-2" in headers,
        )

    async def delete(self, recording_sid: str) -> None:
        await self._t.request("DELETE", self._path("Recordings", recording_sid))
