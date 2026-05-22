"""``/Conferences`` and ``/Conferences/{sid}/Participants``, ``/Conferences/{sid}/Recordings``."""

from __future__ import annotations

from ..models import (
    Conference,
    ConferenceList,
    EndConferenceRequest,
    Participant,
    ParticipantList,
    RecordingList,
    UpdateParticipantRequest,
)
from ._base import AsyncResource, Resource


def _conference_list_params(
    *,
    friendly_name: str | None,
    status: str | None,
    page: int | None,
    page_size: int | None,
    page_token: str | None,
) -> dict[str, object]:
    return {
        "FriendlyName": friendly_name,
        "Status": status,
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
                    page=page,
                    page_size=page_size,
                    page_token=page_token,
                ),
            )
        )

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


class ConferencesAsyncResource(AsyncResource):
    async def list(
        self,
        *,
        friendly_name: str | None = None,
        status: str | None = None,
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
