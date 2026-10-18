from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any, TypeVar

import httpx

from ._hosts import resolve_product_base_urls
from ._http import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    AsyncTransport,
    Transport,
    _ScopedTransport,
)
from .exceptions import ConfigurationError
from .models.common import ListResponse
from .resources import (
    AccountsAsyncResource,
    AccountsResource,
    ApplicationsAsyncResource,
    ApplicationsResource,
    AssistantsV1AsyncResource,
    AssistantsV1Resource,
    BalanceAsyncResource,
    BalanceResource,
    CallsAsyncResource,
    CallsResource,
    ConferencesAsyncResource,
    ConferencesResource,
    ConversationsV1AsyncResource,
    ConversationsV1Resource,
    DiagnosticsAsyncResource,
    DiagnosticsResource,
    ExportsAsyncResource,
    ExportsResource,
    IncomingPhoneNumbersAsyncResource,
    IncomingPhoneNumbersResource,
    MessagesAsyncResource,
    MessagesResource,
    MessagingV1AsyncResource,
    MessagingV1Resource,
    MonitorV1AsyncResource,
    MonitorV1Resource,
    NotificationsAsyncResource,
    NotificationsResource,
    OutgoingCallerIdsAsyncResource,
    OutgoingCallerIdsResource,
    PricingAsyncResource,
    PricingResource,
    QueuesAsyncResource,
    QueuesResource,
    RecordingsAsyncResource,
    RecordingsResource,
    RoutesV2AsyncResource,
    RoutesV2Resource,
    SipAsyncResource,
    SipResource,
    TranscriptionsAsyncResource,
    TranscriptionsResource,
    UsageRecordsAsyncResource,
    UsageRecordsResource,
    VoiceV1AsyncResource,
    VoiceV1Resource,
)
from .resources._base import next_page_url

ItemT = TypeVar("ItemT")
PageT = TypeVar("PageT", bound=ListResponse[Any])


def _resolve_credentials(
    account_sid: str | None, api_key: str | None, auth_token: str | None
) -> tuple[str | None, str | None]:
    """Accept either ``api_key=`` (native) or ``auth_token=`` (alias).

    Both arguments map to the same HTTP Basic password (the VoiceML API key).
    Supplying both is an error so callers don't accidentally pass two different values.
    Omitting the account SID *and* the key yields a diagnostics-only client.
    """
    if api_key is not None and auth_token is not None:
        raise ConfigurationError(
            "Pass either api_key=... or auth_token=..., not both — they map to the same "
            "HTTP Basic password."
        )
    key = api_key if api_key is not None else auth_token
    if account_sid is None and key is None:
        return None, None
    if account_sid is None or not account_sid:
        raise ConfigurationError("account_sid is required")
    if not key:
        raise ConfigurationError("api_key (or auth_token) is required")
    return account_sid, key


class _ClientBase:
    _default_url: str
    _messaging_url: str
    _conversations_url: str

    def _setup_hosts(
        self,
        base_url: str,
        messaging_base_url: str | None,
        conversations_base_url: str | None,
    ) -> None:
        self._default_url, self._messaging_url, self._conversations_url = resolve_product_base_urls(
            base_url, messaging_base_url, conversations_base_url
        )

    def _product_url(self, page: ListResponse[Any]) -> str:
        if page.product == "messaging":
            return self._messaging_url
        if page.product == "conversations":
            return self._conversations_url
        return self._default_url

    @property
    def base_url(self) -> str:
        return self._default_url

    @property
    def messaging_base_url(self) -> str:
        return self._messaging_url

    @property
    def conversations_base_url(self) -> str:
        return self._conversations_url


class Client(_ClientBase):
    """Synchronous client for the VoiceML REST API.

    VoiceML uses HTTP Basic auth: the ``account_sid`` (``AC`` + 32 hex) is the username
    and the VoiceML ``api_key`` is the password. ``auth_token=`` is accepted as an alias
    for ``api_key=`` so code written against twilio-python's constructor keeps its
    shape — but the value must be a VoiceML API key; Twilio-issued credentials do not
    work against VoiceML.

    Omit both ``account_sid`` and ``api_key`` to create a diagnostics-only client
    (``Client().diagnostics.health()``); any other call then raises
    :class:`voiceml.ConfigurationError`.

    Every request goes to an absolute URL derived from ``base_url`` (or the
    product hosts), so the ``base_url`` of an injected ``http_client`` is never used.
    When ``http_client`` is supplied, its own timeout/proxy/TLS settings apply and
    ``timeout`` is ignored.

    Usage::

        from voiceml import Client
        from voiceml.models import CreateCallRequest

        with Client(account_sid="AC…", api_key="…") as c:
            call = c.calls.create(
                CreateCallRequest(To="+14155550100", From="+14155550101", Url="https://…")
            )
            for q in c.queues.iter():
                print(q.friendly_name, q.current_size)
    """

    def __init__(
        self,
        *,
        account_sid: str | None = None,
        api_key: str | None = None,
        auth_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        messaging_base_url: str | None = None,
        conversations_base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.Client | None = None,
    ) -> None:
        sid, key = _resolve_credentials(account_sid, api_key, auth_token)
        self._setup_hosts(base_url, messaging_base_url, conversations_base_url)
        self._transport = Transport(
            account_sid=sid,
            api_key=key,
            base_url=self._default_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        # Conversations and Messaging Service ride their own product subdomains
        # (they share the /v1/Services path shape — host is what disambiguates).
        messaging_transport = _ScopedTransport(self._transport, self._messaging_url)
        conversations_transport = _ScopedTransport(self._transport, self._conversations_url)
        self.calls = CallsResource(self._transport)
        self.conferences = ConferencesResource(self._transport)
        self.queues = QueuesResource(self._transport)
        self.applications = ApplicationsResource(self._transport)
        self.recordings = RecordingsResource(self._transport)
        self.incoming_phone_numbers = IncomingPhoneNumbersResource(self._transport)
        self.messages = MessagesResource(self._transport)
        self.messaging_v1 = MessagingV1Resource(messaging_transport)
        self.notifications = NotificationsResource(self._transport)
        self.pricing = PricingResource(self._transport)
        self.sip = SipResource(self._transport)
        self.routes_v2 = RoutesV2Resource(self._transport)
        self.voice_v1 = VoiceV1Resource(self._transport)
        self.conversations_v1 = ConversationsV1Resource(conversations_transport)
        self.assistants_v1 = AssistantsV1Resource(self._transport)
        self.monitor_v1 = MonitorV1Resource(self._transport)
        self.accounts = AccountsResource(self._transport)
        self.balance = BalanceResource(self._transport)
        self.outgoing_caller_ids = OutgoingCallerIdsResource(self._transport)
        self.usage_records = UsageRecordsResource(self._transport)
        self.exports = ExportsResource(self._transport)
        self.transcriptions = TranscriptionsResource(self._transport)
        self.diagnostics = DiagnosticsResource(self._transport)

    def __repr__(self) -> str:
        sid = self._transport._account_sid
        return f"Client(base_url={self._default_url!r}, account_sid={sid!r})"

    @property
    def account_sid(self) -> str:
        return self._transport.account_sid

    def next_page(self, page: PageT) -> PageT | None:
        """Fetch the page after ``page``, or ``None`` when ``page`` is the last one.

        Follows ``next_page_uri`` (``/2010-04-01`` lists) or ``meta.next_page_url``
        (``/v1`` lists) verbatim against the host that served the page.
        """
        url = next_page_url(page, self._product_url(page))
        if url is None:
            return None
        return type(page).model_validate(self._transport.request("GET", url))

    def paginate(self, page: ListResponse[ItemT]) -> Iterator[ItemT]:
        """Lazily yield every item from ``page`` and the pages after it.

        Requests are issued one page at a time as the iterator is consumed; stopping
        early issues no further requests.
        """
        current: ListResponse[ItemT] | None = page
        while current is not None:
            yield from current.items
            current = self.next_page(current)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncClient(_ClientBase):
    """Async counterpart to :class:`Client`. Same surface; methods are awaitable and the
    ``iter()`` / :meth:`paginate` helpers are async iterators.

    Usage::

        async with AsyncClient(account_sid="AC…", api_key="…") as c:
            calls = await c.calls.list(status="in-progress")
            async for call in c.calls.iter(status="completed"):
                print(call.sid)
    """

    def __init__(
        self,
        *,
        account_sid: str | None = None,
        api_key: str | None = None,
        auth_token: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        messaging_base_url: str | None = None,
        conversations_base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        sid, key = _resolve_credentials(account_sid, api_key, auth_token)
        self._setup_hosts(base_url, messaging_base_url, conversations_base_url)
        self._transport = AsyncTransport(
            account_sid=sid,
            api_key=key,
            base_url=self._default_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=http_client,
        )
        messaging_transport = _ScopedTransport(self._transport, self._messaging_url)
        conversations_transport = _ScopedTransport(self._transport, self._conversations_url)
        self.calls = CallsAsyncResource(self._transport)
        self.conferences = ConferencesAsyncResource(self._transport)
        self.queues = QueuesAsyncResource(self._transport)
        self.applications = ApplicationsAsyncResource(self._transport)
        self.recordings = RecordingsAsyncResource(self._transport)
        self.incoming_phone_numbers = IncomingPhoneNumbersAsyncResource(self._transport)
        self.messages = MessagesAsyncResource(self._transport)
        self.messaging_v1 = MessagingV1AsyncResource(messaging_transport)
        self.notifications = NotificationsAsyncResource(self._transport)
        self.pricing = PricingAsyncResource(self._transport)
        self.sip = SipAsyncResource(self._transport)
        self.routes_v2 = RoutesV2AsyncResource(self._transport)
        self.voice_v1 = VoiceV1AsyncResource(self._transport)
        self.conversations_v1 = ConversationsV1AsyncResource(conversations_transport)
        self.assistants_v1 = AssistantsV1AsyncResource(self._transport)
        self.monitor_v1 = MonitorV1AsyncResource(self._transport)
        self.accounts = AccountsAsyncResource(self._transport)
        self.balance = BalanceAsyncResource(self._transport)
        self.outgoing_caller_ids = OutgoingCallerIdsAsyncResource(self._transport)
        self.usage_records = UsageRecordsAsyncResource(self._transport)
        self.exports = ExportsAsyncResource(self._transport)
        self.transcriptions = TranscriptionsAsyncResource(self._transport)
        self.diagnostics = DiagnosticsAsyncResource(self._transport)

    def __repr__(self) -> str:
        sid = self._transport._account_sid
        return f"AsyncClient(base_url={self._default_url!r}, account_sid={sid!r})"

    @property
    def account_sid(self) -> str:
        return self._transport.account_sid

    async def next_page(self, page: PageT) -> PageT | None:
        """Fetch the page after ``page``, or ``None`` when ``page`` is the last one."""
        url = next_page_url(page, self._product_url(page))
        if url is None:
            return None
        return type(page).model_validate(await self._transport.request("GET", url))

    async def paginate(self, page: ListResponse[ItemT]) -> AsyncIterator[ItemT]:
        """Lazily yield every item from ``page`` and the pages after it."""
        current: ListResponse[ItemT] | None = page
        while current is not None:
            for item in current.items:
                yield item
            current = await self.next_page(current)

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()
