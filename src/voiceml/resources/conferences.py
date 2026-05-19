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


class ConferencesResource(Resource):
    """Operations on live conferences and their participants/recordings."""

    def list(self) -> ConferenceList:
        return ConferenceList.model_validate(
            self._t.request("GET", self._path("Conferences"))
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

    def list_participants(self, conference_sid: str) -> ParticipantList:
        return ParticipantList.model_validate(
            self._t.request(
                "GET", self._path("Conferences", conference_sid, "Participants")
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

    def list_recordings(self, conference_sid: str) -> RecordingList:
        return RecordingList.model_validate(
            self._t.request(
                "GET", self._path("Conferences", conference_sid, "Recordings")
            )
        )


class ConferencesAsyncResource(AsyncResource):
    async def list(self) -> ConferenceList:
        return ConferenceList.model_validate(
            await self._t.request("GET", self._path("Conferences"))
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

    async def list_participants(self, conference_sid: str) -> ParticipantList:
        return ParticipantList.model_validate(
            await self._t.request(
                "GET", self._path("Conferences", conference_sid, "Participants")
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

    async def list_recordings(self, conference_sid: str) -> RecordingList:
        return RecordingList.model_validate(
            await self._t.request(
                "GET", self._path("Conferences", conference_sid, "Recordings")
            )
        )
