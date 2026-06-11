"""``/Conferences`` and ``/Conferences/{sid}/Participants``, ``/Conferences/{sid}/Recordings``."""

from __future__ import annotations

from collections.abc import Sequence

from ..models import (
    Conference,
    ConferenceList,
    CreateParticipantRequest,
    EndConferenceRequest,
    Participant,
    ParticipantList,
    Recording,
    RecordingList,
    UpdateParticipantRequest,
    UpdateRecordingRequest,
)
from ._base import AsyncResource, Resource


def _conference_list_params(
    *,
    friendly_name: str | None,
    status: str | None,
    date_created: str | None,
    date_created_lt: str | None,
    date_created_gt: str | None,
    date_updated: str | None,
    date_updated_lt: str | None,
    date_updated_gt: str | None,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
) -> dict[str, object]:
    return {
        "FriendlyName": friendly_name,
        "Status": status,
        "DateCreated": date_created,
        "DateCreated<": date_created_lt,
        "DateCreated>": date_created_gt,
        "DateUpdated": date_updated,
        "DateUpdated<": date_updated_lt,
        "DateUpdated>": date_updated_gt,
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
    }


def _participant_list_params(
    *,
    muted: bool | None,
    hold: bool | None,
    coaching: bool | None,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
) -> dict[str, object]:
    return {
        "Muted": muted,
        "Hold": hold,
        "Coaching": coaching,
        "Page": page,
        "PageSize": page_size,
        "PageToken": page_token,
    }


def _page_params(
    *, page: int | None, page_size: int | None, page_token: str | None
) -> dict[str, object]:
    return {"Page": page, "PageSize": page_size, "PageToken": page_token}


class ConferencesResource(Resource):
    """Operations on live conferences and their participants/recordings."""

    def list(
        self,
        *,
        friendly_name: str | None = None,
        status: str | None = None,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        date_updated: str | None = None,
        date_updated_lt: str | None = None,
        date_updated_gt: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ConferenceList:
        return ConferenceList.model_validate(
            self._t.request(
                "GET",
                self._path("Conferences"),
                params=_conference_list_params(
                    friendly_name=friendly_name,
                    status=status,
                    date_created=date_created,
                    date_created_lt=date_created_lt,
                    date_created_gt=date_created_gt,
                    date_updated=date_updated,
                    date_updated_lt=date_updated_lt,
                    date_updated_gt=date_updated_gt,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def iter(
        self,
        *,
        friendly_name: str | None = None,
        status: str | None = None,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        date_updated: str | None = None,
        date_updated_lt: str | None = None,
        date_updated_gt: str | None = None,
        page_size: int | None = None,
    ) -> Sequence[Conference]:
        out: list[Conference] = []
        page = 0
        while True:
            chunk = self.list(
                friendly_name=friendly_name,
                status=status,
                date_created=date_created,
                date_created_lt=date_created_lt,
                date_created_gt=date_created_gt,
                date_updated=date_updated,
                date_updated_lt=date_updated_lt,
                date_updated_gt=date_updated_gt,
                page=page,
                page_size=page_size,
            )
            out.extend(chunk.conferences)
            if not chunk.next_page_uri or not chunk.conferences:
                return out
            page += 1

    def get(self, conference_sid: str) -> Conference:
        return Conference.model_validate(
            self._t.request("GET", self._path("Conferences", conference_sid))
        )

    def end(
        self, conference_sid: str, body: EndConferenceRequest | None = None
    ) -> Conference:
        payload = (body or EndConferenceRequest(Status="completed")).to_form()
        return Conference.model_validate(
            self._t.request(
                "POST", self._path("Conferences", conference_sid), data=payload
            )
        )

    # --- Participants ---

    def create_participant(
        self, conference_sid: str, body: CreateParticipantRequest
    ) -> Participant:
        return Participant.model_validate(
            self._t.request(
                "POST",
                self._path("Conferences", conference_sid, "Participants"),
                data=body.to_form(),
            )
        )

    def list_participants(
        self,
        conference_sid: str,
        *,
        muted: bool | None = None,
        hold: bool | None = None,
        coaching: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ParticipantList:
        return ParticipantList.model_validate(
            self._t.request(
                "GET",
                self._path("Conferences", conference_sid, "Participants"),
                params=_participant_list_params(
                    muted=muted,
                    hold=hold,
                    coaching=coaching,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    def get_participant(self, conference_sid: str, call_sid: str) -> Participant:
        return Participant.model_validate(
            self._t.request(
                "GET", self._path("Conferences", conference_sid, "Participants", call_sid)
            )
        )

    def update_participant(
        self, conference_sid: str, call_sid: str, body: UpdateParticipantRequest
    ) -> Participant:
        return Participant.model_validate(
            self._t.request(
                "POST",
                self._path("Conferences", conference_sid, "Participants", call_sid),
                data=body.to_form(),
            )
        )

    def kick_participant(self, conference_sid: str, call_sid: str) -> None:
        self._t.request(
            "DELETE", self._path("Conferences", conference_sid, "Participants", call_sid)
        )

    # --- Recordings ---

    def list_recordings(
        self,
        conference_sid: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> RecordingList:
        return RecordingList.model_validate(
            self._t.request(
                "GET",
                self._path("Conferences", conference_sid, "Recordings"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    def get_recording(self, conference_sid: str, recording_sid: str) -> Recording:
        return Recording.model_validate(
            self._t.request(
                "GET",
                self._path("Conferences", conference_sid, "Recordings", recording_sid),
            )
        )

    def update_recording(
        self, conference_sid: str, recording_sid: str, body: UpdateRecordingRequest
    ) -> Recording:
        return Recording.model_validate(
            self._t.request(
                "POST",
                self._path("Conferences", conference_sid, "Recordings", recording_sid),
                data=body.to_form(),
            )
        )

    def delete_recording(self, conference_sid: str, recording_sid: str) -> None:
        self._t.request(
            "DELETE",
            self._path("Conferences", conference_sid, "Recordings", recording_sid),
        )


class ConferencesAsyncResource(AsyncResource):
    async def list(
        self,
        *,
        friendly_name: str | None = None,
        status: str | None = None,
        date_created: str | None = None,
        date_created_lt: str | None = None,
        date_created_gt: str | None = None,
        date_updated: str | None = None,
        date_updated_lt: str | None = None,
        date_updated_gt: str | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ConferenceList:
        return ConferenceList.model_validate(
            await self._t.request(
                "GET",
                self._path("Conferences"),
                params=_conference_list_params(
                    friendly_name=friendly_name,
                    status=status,
                    date_created=date_created,
                    date_created_lt=date_created_lt,
                    date_created_gt=date_created_gt,
                    date_updated=date_updated,
                    date_updated_lt=date_updated_lt,
                    date_updated_gt=date_updated_gt,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def get(self, conference_sid: str) -> Conference:
        return Conference.model_validate(
            await self._t.request("GET", self._path("Conferences", conference_sid))
        )

    async def end(
        self, conference_sid: str, body: EndConferenceRequest | None = None
    ) -> Conference:
        payload = (body or EndConferenceRequest(Status="completed")).to_form()
        return Conference.model_validate(
            await self._t.request(
                "POST", self._path("Conferences", conference_sid), data=payload
            )
        )

    async def create_participant(
        self, conference_sid: str, body: CreateParticipantRequest
    ) -> Participant:
        return Participant.model_validate(
            await self._t.request(
                "POST",
                self._path("Conferences", conference_sid, "Participants"),
                data=body.to_form(),
            )
        )

    async def list_participants(
        self,
        conference_sid: str,
        *,
        muted: bool | None = None,
        hold: bool | None = None,
        coaching: bool | None = None,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> ParticipantList:
        return ParticipantList.model_validate(
            await self._t.request(
                "GET",
                self._path("Conferences", conference_sid, "Participants"),
                params=_participant_list_params(
                    muted=muted,
                    hold=hold,
                    coaching=coaching,
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

    async def get_participant(self, conference_sid: str, call_sid: str) -> Participant:
        return Participant.model_validate(
            await self._t.request(
                "GET", self._path("Conferences", conference_sid, "Participants", call_sid)
            )
        )

    async def update_participant(
        self, conference_sid: str, call_sid: str, body: UpdateParticipantRequest
    ) -> Participant:
        return Participant.model_validate(
            await self._t.request(
                "POST",
                self._path("Conferences", conference_sid, "Participants", call_sid),
                data=body.to_form(),
            )
        )

    async def kick_participant(self, conference_sid: str, call_sid: str) -> None:
        await self._t.request(
            "DELETE", self._path("Conferences", conference_sid, "Participants", call_sid)
        )

    async def list_recordings(
        self,
        conference_sid: str,
        *,
        page: int | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> RecordingList:
        return RecordingList.model_validate(
            await self._t.request(
                "GET",
                self._path("Conferences", conference_sid, "Recordings"),
                params=_page_params(page=page, page_size=page_size, page_token=page_token),
            )
        )

    async def get_recording(self, conference_sid: str, recording_sid: str) -> Recording:
        return Recording.model_validate(
            await self._t.request(
                "GET",
                self._path("Conferences", conference_sid, "Recordings", recording_sid),
            )
        )

    async def update_recording(
        self, conference_sid: str, recording_sid: str, body: UpdateRecordingRequest
    ) -> Recording:
        return Recording.model_validate(
            await self._t.request(
                "POST",
                self._path("Conferences", conference_sid, "Recordings", recording_sid),
                data=body.to_form(),
            )
        )

    async def delete_recording(self, conference_sid: str, recording_sid: str) -> None:
        await self._t.request(
            "DELETE",
            self._path("Conferences", conference_sid, "Recordings", recording_sid),
        )
