"""HTTP transport: URL building, auth, retry policy and error mapping.

Retry policy
------------
* Idempotent methods (``GET``, ``HEAD``, ``DELETE``, ``PUT``) are retried on
  429/500/502/503/504 and on connect/read transport failures.
* ``POST`` / ``PATCH`` are retried **only** on 429 and on connection-establishment
  failures where the request provably never left the machine (DNS failure,
  refused connection, connect timeout, TLS handshake failure, connection-pool
  timeout). They are never retried on 5xx, read timeouts or connection resets,
  so a ``calls.create`` / ``messages.create`` cannot be duplicated by the SDK.
* ``Retry-After`` is honoured as delta-seconds or an HTTP-date. A value above
  :data:`MAX_RETRY_AFTER` is not slept on: the error is raised immediately with
  the parsed value on ``error.retry_after``.
* Otherwise backoff is exponential (0.5 s base, 8 s max) with full jitter.
"""

from __future__ import annotations

import asyncio
import email.utils
import json as jsonlib
import random
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx

from ._version import __version__
from .exceptions import (
    APIConnectionError,
    ApiError,
    APITimeoutError,
    ConfigurationError,
    from_response,
)
from .models._base import form_value

DEFAULT_BASE_URL = "https://voiceml.voicetel.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_USER_AGENT = (
    f"voiceml-python/{__version__} (+https://github.com/voicetel/voiceml-python-sdk)"
)

#: Longest ``Retry-After`` (seconds) the SDK will sleep on before retrying.
MAX_RETRY_AFTER = 60.0
BACKOFF_BASE = 0.5
BACKOFF_MAX = 8.0
MAX_REDIRECTS = 5

_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})
_IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "DELETE", "PUT", "OPTIONS"})
_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})

# Indirections so tests can control time without touching the network or sleeping.
_sleep = time.sleep
_async_sleep = asyncio.sleep
_now = time.time
_jitter = random.uniform


def _default_http_client(timeout: float) -> httpx.Client:
    return httpx.Client(timeout=timeout)


def _default_async_http_client(timeout: float) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout)


def validate_base_url(url: str, *, name: str = "base_url") -> str:
    """Return ``url`` without a trailing slash; raise ConfigurationError if unusable."""
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ConfigurationError(f"{name} must be an absolute http(s) URL, got {url!r}")
    if parts.query or parts.fragment:
        raise ConfigurationError(f"{name} must not carry a query string or fragment")
    return url.rstrip("/")


def origin_of(url: str) -> tuple[str, str]:
    """``(scheme, netloc)`` with the default port removed, for same-origin checks."""
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    port = parts.port
    if port is None or (scheme, port) in (("https", 443), ("http", 80)):
        return scheme, host
    return scheme, f"{host}:{port}"


@dataclass(frozen=True)
class BinaryResponse:
    """Result of an authenticated binary download (recording audio, exports)."""

    status_code: int
    content: bytes
    headers: httpx.Headers
    url: str
    redirected: bool


class _Transport:
    """Shared config/state for sync and async transports.

    VoiceML uses HTTP Basic auth with ``AccountSid`` as the username and the per-tenant
    API key as the password. A transport created without credentials can only issue
    requests with ``auth=False`` (the diagnostics endpoints).
    """

    def __init__(
        self,
        *,
        account_sid: str | None,
        api_key: str | None,
        base_url: str,
        max_retries: int,
        user_agent: str,
    ) -> None:
        if (account_sid is None) != (api_key is None):
            raise ConfigurationError(
                "account_sid and api_key must be supplied together "
                "(omit both for a diagnostics-only client)"
            )
        if account_sid is not None and not account_sid:
            raise ConfigurationError("account_sid is required")
        if api_key is not None and not api_key:
            raise ConfigurationError("api_key is required")
        if max_retries < 0:
            raise ConfigurationError("max_retries must be >= 0")
        self._account_sid = account_sid
        self._api_key = api_key
        self._base_url = validate_base_url(base_url)
        self._max_retries = max_retries
        self._user_agent = user_agent

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(base_url={self._base_url!r}, account_sid={self._account_sid!r})"
        )

    @property
    def has_credentials(self) -> bool:
        return self._account_sid is not None

    @property
    def account_sid(self) -> str:
        if self._account_sid is None:
            raise _no_credentials()
        return self._account_sid

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def max_retries(self) -> int:
        return self._max_retries

    def _url(self, path: str, base_url: str | None) -> str:
        if path.startswith(("https://", "http://")):
            return path
        return f"{base_url or self._base_url}{path}"

    def _auth(self, auth: bool) -> tuple[str, str] | None:
        if not auth:
            return None
        if self._account_sid is None or self._api_key is None:
            raise _no_credentials()
        return (self._account_sid, self._api_key)

    def _headers(self, accept: str, *, json_body: bool = False) -> dict[str, str]:
        headers = {"User-Agent": self._user_agent, "Accept": accept}
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def _should_retry_status(self, method: str, status: int, attempt: int) -> bool:
        if attempt >= self._max_retries or status not in _RETRYABLE_STATUSES:
            return False
        return status == 429 or method in _IDEMPOTENT_METHODS

    def _should_retry_exc(self, method: str, exc: httpx.TransportError, attempt: int) -> bool:
        if attempt >= self._max_retries:
            return False
        if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout, httpx.PoolTimeout)):
            # Connection was never established: the request was not sent.
            return True
        if method not in _IDEMPOTENT_METHODS:
            return False
        return isinstance(
            exc, (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError)
        )


def _no_credentials() -> ConfigurationError:
    return ConfigurationError(
        "this client was created without account_sid/api_key; only client.diagnostics is available"
    )


class Transport(_Transport):
    """Sync HTTP transport. Owns an :class:`httpx.Client` and the retry/auth policy.

    Every request is sent to an absolute URL built from ``base_url`` (or a product
    host), so the ``base_url`` of an injected ``http_client`` is never used. When
    ``http_client`` is supplied, its own timeout, proxy and TLS settings apply.
    """

    def __init__(
        self,
        *,
        account_sid: str | None,
        api_key: str | None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.Client | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        super().__init__(
            account_sid=account_sid,
            api_key=api_key,
            base_url=base_url,
            max_retries=max_retries,
            user_agent=user_agent,
        )
        self._owns_client = http_client is None
        self._http: httpx.Client = http_client or _default_http_client(timeout)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: Any = None,
        base_url: str | None = None,
        auth: bool = True,
        accept: str = "application/json",
    ) -> Any:
        response = self._send(
            method,
            self._url(path, base_url),
            params=params,
            data=data,
            json=json,
            auth=auth,
            accept=accept,
        )
        return parse_response(response)

    def _send(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: Any = None,
        auth: bool = True,
        accept: str = "application/json",
    ) -> httpx.Response:
        credentials = self._auth(auth)
        attempt = 0
        while True:
            try:
                response = self._http.request(
                    method,
                    url,
                    params=clean_params(params),
                    data=clean_params(data),
                    content=encode_json(json),
                    headers=self._headers(accept, json_body=json is not None),
                    auth=credentials,
                    follow_redirects=False,
                )
            except httpx.TransportError as exc:
                if self._should_retry_exc(method, exc, attempt):
                    _sleep(backoff_delay(attempt))
                    attempt += 1
                    continue
                raise wrap_transport_error(exc, attempt + 1) from exc
            if self._should_retry_status(method, response.status_code, attempt):
                delay = retry_delay(attempt, response)
                if delay is None:
                    return response
                response.close()
                _sleep(delay)
                attempt += 1
                continue
            return response

    def fetch_bytes(
        self,
        path: str,
        *,
        base_url: str | None = None,
        accept: str = "*/*",
        auth: bool = True,
    ) -> BinaryResponse:
        """Authenticated binary GET (recording audio, export archives).

        Redirects are followed manually: ``Authorization`` is dropped as soon as the
        scheme or host changes, and an https→http downgrade is refused.
        """
        url = self._url(path, base_url)
        origin = origin_of(url)
        send_auth = auth
        redirected = False
        for _ in range(MAX_REDIRECTS + 1):
            response = self._send("GET", url, auth=send_auth, accept=accept)
            next_url = _redirect_target(url, response)
            if next_url is None:
                break
            response.close()
            redirected = True
            if origin_of(next_url) != origin:
                send_auth = False
            url = next_url
        else:
            raise ApiError(f"too many redirects (>{MAX_REDIRECTS})", status_code=0)
        if not 200 <= response.status_code < 300:
            parse_response(response)
        return BinaryResponse(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            url=url,
            redirected=redirected,
        )

    def close(self) -> None:
        if self._owns_client:
            self._http.close()

    def __enter__(self) -> Transport:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class AsyncTransport(_Transport):
    """Async counterpart to :class:`Transport`. Same surface, awaitable methods."""

    def __init__(
        self,
        *,
        account_sid: str | None,
        api_key: str | None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        super().__init__(
            account_sid=account_sid,
            api_key=api_key,
            base_url=base_url,
            max_retries=max_retries,
            user_agent=user_agent,
        )
        self._owns_client = http_client is None
        self._http: httpx.AsyncClient = http_client or _default_async_http_client(timeout)

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: Any = None,
        base_url: str | None = None,
        auth: bool = True,
        accept: str = "application/json",
    ) -> Any:
        response = await self._send(
            method,
            self._url(path, base_url),
            params=params,
            data=data,
            json=json,
            auth=auth,
            accept=accept,
        )
        return parse_response(response)

    async def _send(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: Any = None,
        auth: bool = True,
        accept: str = "application/json",
    ) -> httpx.Response:
        credentials = self._auth(auth)
        attempt = 0
        while True:
            try:
                response = await self._http.request(
                    method,
                    url,
                    params=clean_params(params),
                    data=clean_params(data),
                    content=encode_json(json),
                    headers=self._headers(accept, json_body=json is not None),
                    auth=credentials,
                    follow_redirects=False,
                )
            except httpx.TransportError as exc:
                if self._should_retry_exc(method, exc, attempt):
                    await _async_sleep(backoff_delay(attempt))
                    attempt += 1
                    continue
                raise wrap_transport_error(exc, attempt + 1) from exc
            if self._should_retry_status(method, response.status_code, attempt):
                delay = retry_delay(attempt, response)
                if delay is None:
                    return response
                await response.aclose()
                await _async_sleep(delay)
                attempt += 1
                continue
            return response

    async def fetch_bytes(
        self,
        path: str,
        *,
        base_url: str | None = None,
        accept: str = "*/*",
        auth: bool = True,
    ) -> BinaryResponse:
        url = self._url(path, base_url)
        origin = origin_of(url)
        send_auth = auth
        redirected = False
        for _ in range(MAX_REDIRECTS + 1):
            response = await self._send("GET", url, auth=send_auth, accept=accept)
            next_url = _redirect_target(url, response)
            if next_url is None:
                break
            await response.aclose()
            redirected = True
            if origin_of(next_url) != origin:
                send_auth = False
            url = next_url
        else:
            raise ApiError(f"too many redirects (>{MAX_REDIRECTS})", status_code=0)
        if not 200 <= response.status_code < 300:
            parse_response(response)
        return BinaryResponse(
            status_code=response.status_code,
            content=response.content,
            headers=response.headers,
            url=url,
            redirected=redirected,
        )

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()


class _ScopedTransport:
    """A transport view pinned to a specific product base URL.

    Wraps a real (sync or async) transport and forwards every call, injecting a
    ``base_url`` override so an entire resource group lands on its product
    subdomain (``conversations.voicetel.com`` / ``messaging.voicetel.com``)
    without each resource needing to know its own host. The forwarded
    ``request`` returns whatever the inner transport returns — a value for the
    sync transport, an awaitable for the async one — so a single wrapper serves
    both.
    """

    def __init__(self, inner: Transport | AsyncTransport, base_url: str) -> None:
        self._inner = inner
        self._base_url = validate_base_url(base_url)

    def __repr__(self) -> str:
        return f"_ScopedTransport(base_url={self._base_url!r})"

    @property
    def account_sid(self) -> str:
        return self._inner.account_sid

    @property
    def base_url(self) -> str:
        return self._base_url

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: Any = None,
        auth: bool = True,
    ) -> Any:
        return self._inner.request(
            method,
            path,
            params=params,
            data=data,
            json=json,
            base_url=self._base_url,
            auth=auth,
        )

    def fetch_bytes(self, path: str, *, accept: str = "*/*", auth: bool = True) -> Any:
        return self._inner.fetch_bytes(path, base_url=self._base_url, accept=accept, auth=auth)


def _redirect_target(current: str, response: httpx.Response) -> str | None:
    if response.status_code not in _REDIRECT_STATUSES:
        return None
    location = response.headers.get("location")
    if not location:
        return None
    target = str(urljoin(current, location))
    scheme = urlsplit(target).scheme.lower()
    if scheme not in ("http", "https"):
        raise ApiError(f"refusing redirect to unsupported scheme {scheme!r}", status_code=0)
    if urlsplit(current).scheme.lower() == "https" and scheme == "http":
        raise ApiError("refusing redirect from https to http", status_code=0)
    return target


def clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Drop ``None`` values and render the rest with :func:`form_value`.

    Empty strings are kept — the API uses them as "explicit clear" tokens. Lists
    stay lists so httpx encodes them as repeated keys (``Key=a&Key=b``).
    """
    if params is None:
        return None
    return {key: form_value(value) for key, value in params.items() if value is not None}


def encode_json(body: Any) -> bytes | None:
    """Compact, deterministic JSON request body (independent of the httpx version)."""
    if body is None:
        return None
    return jsonlib.dumps(body, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode(
        "utf-8"
    )


def parse_response(response: httpx.Response) -> Any:
    """Decode a JSON response or raise the matching :class:`ApiError` subclass."""
    if 200 <= response.status_code < 300:
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(
                f"could not decode {response.status_code} response body as JSON "
                f"(content-type {response.headers.get('content-type', 'unknown')!r}): {exc}",
                status_code=response.status_code,
                body=response.text,
            ) from exc
    body: Any
    try:
        body = response.json()
    except ValueError:
        body = response.text
    code: int | None = None
    more_info: str | None = None
    message = f"HTTP {response.status_code}"
    if isinstance(body, dict):
        raw_code = body.get("code")
        if isinstance(raw_code, bool):
            raw_code = None
        if isinstance(raw_code, int):
            code = raw_code
        elif isinstance(raw_code, str) and raw_code.isdigit():
            code = int(raw_code)
        raw_message = body.get("message")
        if isinstance(raw_message, str) and raw_message:
            message = raw_message
        raw_more_info = body.get("more_info")
        if isinstance(raw_more_info, str) and raw_more_info:
            more_info = raw_more_info
    elif isinstance(body, str) and body.strip():
        message = f"HTTP {response.status_code}: {body.strip()[:200]}"
    raise from_response(
        response.status_code,
        code,
        body,
        message,
        more_info=more_info,
        retry_after=parse_retry_after(response.headers.get("retry-after")),
    )


def wrap_transport_error(exc: httpx.TransportError, attempts: int) -> ApiError:
    cls = APITimeoutError if isinstance(exc, httpx.TimeoutException) else APIConnectionError
    suffix = "" if attempts == 1 else f" after {attempts} attempts"
    return cls(f"{type(exc).__name__}{suffix}: {exc}", status_code=0)


def parse_retry_after(value: str | None) -> float | None:
    """Parse ``Retry-After`` as delta-seconds or an HTTP-date; ``None`` if absent/invalid."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        seconds = float(value)
    except ValueError:
        try:
            when = email.utils.parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None
        return max(0.0, when.timestamp() - _now())
    if seconds != seconds or seconds in (float("inf"), float("-inf")):
        return None
    return max(0.0, seconds)


def backoff_delay(attempt: int) -> float:
    """Full-jitter exponential backoff: uniform(0, min(8, 0.5 * 2**attempt))."""
    return _jitter(0.0, min(BACKOFF_MAX, BACKOFF_BASE * (2**attempt)))


def retry_delay(attempt: int, response: httpx.Response) -> float | None:
    """Delay before retrying ``response``; ``None`` means "do not retry, raise now"."""
    retry_after = parse_retry_after(response.headers.get("retry-after"))
    if retry_after is None:
        return backoff_delay(attempt)
    if retry_after > MAX_RETRY_AFTER:
        return None
    return retry_after
