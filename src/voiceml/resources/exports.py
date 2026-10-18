"""``/Exports`` — daily event-log archives (a VoiceML extension).

``download(date)`` follows the server's redirect to a presigned URL without
forwarding credentials to the storage host, like recording audio.
"""

from __future__ import annotations

from ..models import ExportArchive, ExportList
from ._base import AsyncResource, Resource, account_path


class ExportsResource(Resource):
    """``client.exports``."""

    def list(self) -> ExportList:
        """List the account's available archives, newest first."""
        return ExportList.model_validate(self._t.request("GET", self._path("Exports")))

    def download(self, date: str) -> ExportArchive:
        """Download the archive for ``date`` (``YYYY-MM-DD``)."""
        result = self._t.fetch_bytes(account_path(self._acct, "Exports", date, suffix=""))
        return ExportArchive(
            date=date,
            content=result.content,
            content_type=result.headers.get("content-type", "application/octet-stream"),
        )


class ExportsAsyncResource(AsyncResource):
    """Async counterpart to :class:`ExportsResource`."""

    async def list(self) -> ExportList:
        return ExportList.model_validate(await self._t.request("GET", self._path("Exports")))

    async def download(self, date: str) -> ExportArchive:
        result = await self._t.fetch_bytes(account_path(self._acct, "Exports", date, suffix=""))
        return ExportArchive(
            date=date,
            content=result.content,
            content_type=result.headers.get("content-type", "application/octet-stream"),
        )
