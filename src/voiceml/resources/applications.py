"""``/Applications`` resource."""

from __future__ import annotations

from ..models import (
    Application,
    ApplicationList,
    CreateApplicationRequest,
    UpdateApplicationRequest,
)
from ._base import AsyncResource, Resource


class ApplicationsResource(Resource):
    def create(self, body: CreateApplicationRequest) -> Application:
        return Application.model_validate(
            self._t.request("POST", self._path("Applications"), data=body.to_form())
        )

    def list(self) -> ApplicationList:
        return ApplicationList.model_validate(
            self._t.request("GET", self._path("Applications"))
        )

    def get(self, application_sid: str) -> Application:
        return Application.model_validate(
            self._t.request("GET", self._path("Applications", application_sid))
        )

    def update(
        self, application_sid: str, body: UpdateApplicationRequest
    ) -> Application:
        return Application.model_validate(
            self._t.request(
                "POST", self._path("Applications", application_sid), data=body.to_form()
            )
        )

    def delete(self, application_sid: str) -> None:
        self._t.request("DELETE", self._path("Applications", application_sid))


class ApplicationsAsyncResource(AsyncResource):
    async def create(self, body: CreateApplicationRequest) -> Application:
        return Application.model_validate(
            await self._t.request(
                "POST", self._path("Applications"), data=body.to_form()
            )
        )

    async def list(self) -> ApplicationList:
        return ApplicationList.model_validate(
            await self._t.request("GET", self._path("Applications"))
        )

    async def get(self, application_sid: str) -> Application:
        return Application.model_validate(
            await self._t.request("GET", self._path("Applications", application_sid))
        )

    async def update(
        self, application_sid: str, body: UpdateApplicationRequest
    ) -> Application:
        return Application.model_validate(
            await self._t.request(
                "POST",
                self._path("Applications", application_sid),
                data=body.to_form(),
            )
        )

    async def delete(self, application_sid: str) -> None:
        await self._t.request("DELETE", self._path("Applications", application_sid))
