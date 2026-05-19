from __future__ import annotations

from typing import Any

from .._http import AsyncTransport, Transport


class Resource:
    """Mixin holding a sync :class:`Transport` reference + helpers for AccountSid pathing."""

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    @property
    def _acct(self) -> str:
        return self._t.account_sid

    def _path(self, *parts: str) -> str:
        """Build a URL under ``/2010-04-01/Accounts/{AccountSid}/…``.

        Caller passes path segments (e.g. ``"Calls"``, sid, ``"Recordings"``). Empty segments
        are skipped; nothing is URL-encoded — callers should pass sids and slugs that don't
        need escaping (Twilio sids never do).
        """
        tail = "/".join(p for p in parts if p)
        return f"/2010-04-01/Accounts/{self._acct}/{tail}"

    @staticmethod
    def _filter(params: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in params.items() if v is not None}


class AsyncResource:
    """Mixin holding an :class:`AsyncTransport` reference + helpers for AccountSid pathing."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._t = transport

    @property
    def _acct(self) -> str:
        return self._t.account_sid

    def _path(self, *parts: str) -> str:
        tail = "/".join(p for p in parts if p)
        return f"/2010-04-01/Accounts/{self._acct}/{tail}"

    @staticmethod
    def _filter(params: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in params.items() if v is not None}
