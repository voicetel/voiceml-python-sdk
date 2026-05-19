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
from .resources import (
    ApplicationsAsyncResource,
    ApplicationsResource,
    CallsAsyncResource,
    CallsResource,
    ConferencesAsyncResource,
    ConferencesResource,
    DiagnosticsAsyncResource,
    DiagnosticsResource,
    QueuesAsyncResource,
    QueuesResource,
    RecordingsAsyncResource,
    RecordingsResource,
)


class Client:
    """Synchronous client for the VoiceML REST API.

    VoiceML uses HTTP Basic auth: the ``account_sid`` (Twilio-format ``AC`` + 32 hex)
    is the username and ``api_key`` is the password. Drop-in compatible with the
    Twilio Python SDK constructor signature.

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
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._transport = Transport(
            account_sid=account_sid,
            api_key=api_key,
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
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._transport = AsyncTransport(
            account_sid=account_sid,
            api_key=api_key,
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
