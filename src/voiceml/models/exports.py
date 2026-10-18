"""Daily event-log archives (``/Exports``) — a VoiceML extension."""

from __future__ import annotations

from pydantic import Field

from ._base import _Base


class Export(_Base):
    """One available daily archive."""

    date: str | None = None
    size: int | None = None
    uri: str | None = None


class ExportList(_Base):
    """``GET /Exports.json`` — the account's archives, newest first (not paginated)."""

    account_sid: str | None = None
    uri: str | None = None
    exports: list[Export] = Field(default_factory=list)


class ExportArchive(_Base):
    """Result of ``exports.download(date)``: the archive bytes after following the
    server's redirect to a presigned URL (credentials are not forwarded)."""

    date: str
    content: bytes
    content_type: str

    def __repr__(self) -> str:
        return (
            f"ExportArchive(date={self.date!r}, content_type={self.content_type!r}, "
            f"bytes={len(self.content)})"
        )
