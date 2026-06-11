from __future__ import annotations

from typing import Any

import httpx

from ._http import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    AsyncTransport,
    Transport,
)
from .exceptions import ConfigurationError
from .resources import (
    ApplicationsAsyncResource,
    ApplicationsResource,
    CallsAsyncResource,
    CallsResource,
    ConferencesAsyncResource,
    ConferencesResource,
    DiagnosticsAsyncResource,
    DiagnosticsResource,
    IncomingPhoneNumbersAsyncResource,
    IncomingPhoneNumbersResource,
    MessagesAsyncResource,
    MessagesResource,
    NotificationsAsyncResource,
    NotificationsResource,
    QueuesAsyncResource,
    QueuesResource,
    RecordingsAsyncResource,
    RecordingsResource,
)


def _resolve_credentials(
    api_key: str | None, auth_token: str | None
) -> str:
    """Accept either ``api_key=`` (native) or ``auth_token=`` (Twilio-compat alias).

    Both arguments map to the same HTTP Basic password — VoiceML calls it an "API key"
    in docs, but the wire shape and the parameter role match Twilio's ``auth_token``.
    Supplying both is an error so callers don't accidentally pass two different values.
    """
    if api_key is not None and auth_token is not None:
        raise ConfigurationError(
            "Pass either api_key=... or auth_token=..., not both — they map to the same "
            "HTTP Basic password."
        )
    resolved = api_key if api_key is not None else auth_token
    if not resolved:
        raise ConfigurationError("api_key (or auth_token) is required")
    return resolved


class Client:
    """Synchronous client for the VoiceML REST API.

    VoiceML uses HTTP Basic auth: the ``account_sid`` (Twilio-format ``AC`` + 32 hex)
    is the username and ``api_key`` is the password. ``auth_token=`` is accepted as an
    alias for ``api_key=`` so code copied from twilio-python keeps working.

    Usage::

        from voiceml import Client

        with Client(account_sid="AC…", api_key="…") as c:
            call = c.calls.create(CreateCallRequest(To="+1…", From="+1…", Url="https://…"))
            for q in c.queues.list().queues:
                print(q.friendly_name, q.current_size)
    """

    def __init__(
        self,
        *,
        account_sid: str,
        api_key: str | None = None,
        auth_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.Client | None = None,
    ) -> None:
        resolved_key = _resolve_credentials(api_key, auth_token)
        self._transport = Transport(
            account_sid=account_sid,
            api_key=resolved_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        self.calls = CallsResource(self._transport)
        self.conferences = ConferencesResource(self._transport)
        self.queues = QueuesResource(self._transport)
        self.applications = ApplicationsResource(self._transport)
        self.recordings = RecordingsResource(self._transport)
        self.incoming_phone_numbers = IncomingPhoneNumbersResource(self._transport)
        self.messages = MessagesResource(self._transport)
        self.notifications = NotificationsResource(self._transport)
        self.diagnostics = DiagnosticsResource(self._transport)

    @property
    def account_sid(self) -> str:
        return self._transport.account_sid

    @property
    def base_url(self) -> str:
        return self._transport.base_url

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


class AsyncClient:
    """Async counterpart to :class:`Client`. Same surface; methods are awaitable.

    Usage::

        async with AsyncClient(account_sid="AC…", api_key="…") as c:
            calls = await c.calls.list(status="in-progress")
    """

    def __init__(
        self,
        *,
        account_sid: str,
        api_key: str | None = None,
        auth_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        resolved_key = _resolve_credentials(api_key, auth_token)
        self._transport = AsyncTransport(
            account_sid=account_sid,
            api_key=resolved_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        self.calls = CallsAsyncResource(self._transport)
        self.conferences = ConferencesAsyncResource(self._transport)
        self.queues = QueuesAsyncResource(self._transport)
        self.applications = ApplicationsAsyncResource(self._transport)
        self.recordings = RecordingsAsyncResource(self._transport)
        self.incoming_phone_numbers = IncomingPhoneNumbersAsyncResource(self._transport)
        self.messages = MessagesAsyncResource(self._transport)
        self.notifications = NotificationsAsyncResource(self._transport)
        self.diagnostics = DiagnosticsAsyncResource(self._transport)

    @property
    def account_sid(self) -> str:
        return self._transport.account_sid

    @property
    def base_url(self) -> str:
        return self._transport.base_url

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()
