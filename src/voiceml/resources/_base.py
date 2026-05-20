from __future__ import annotations

from typing import Any

from .._http import AsyncTransport, Transport


def _join_with_json_suffix(acct: str, parts: tuple[str, ...]) -> str:
    """Build ``/2010-04-01/Accounts/{acct}/<parts…>.json``.

    The Twilio-shape REST surface terminates every resource path with ``.json``. The server
    accepts both forms for back-compat, but the SDK always emits the strict-Twilio form so
    URL comparisons in user code (logging, signature validators, route assertions) line up.

    If the last segment already carries an extension (``.wav``, ``.json``, ``.yaml``, etc.)
    it's left alone — callers building binary or doc paths pass the extension themselves.
    """
    tail = "/".join(p for p in parts if p)
    # Don't double-suffix paths the caller already extended (`.wav`, `.json`, `.yaml`…).
    last = parts[-1] if parts else ""
    if "." in last.rsplit("/", 1)[-1]:
        return f"/2010-04-01/Accounts/{acct}/{tail}"
    return f"/2010-04-01/Accounts/{acct}/{tail}.json"


class Resource:
    """Mixin holding a sync :class:`Transport` reference + helpers for AccountSid pathing."""

    def __init__(self, transport: Transport) -> None:
        self._t = transport

    @property
    def _acct(self) -> str:
        return self._t.account_sid

    def _path(self, *parts: str) -> str:
        """Build a URL under ``/2010-04-01/Accounts/{AccountSid}/….json``.

        Caller passes path segments (e.g. ``"Calls"``, sid, ``"Recordings"``). Empty segments
        are skipped; the trailing ``.json`` suffix Twilio expects is added automatically.
        Nothing is URL-encoded — callers should pass sids and slugs that don't need escaping
        (Twilio sids never do).
        """
        return _join_with_json_suffix(self._acct, parts)

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
        return _join_with_json_suffix(self._acct, parts)

    @staticmethod
    def _filter(params: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in params.items() if v is not None}
