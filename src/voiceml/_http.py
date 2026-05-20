from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from ._version import __version__
from .exceptions import ApiError, ConfigurationError, from_response

DEFAULT_BASE_URL = "https://voiceml.voicetel.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_USER_AGENT = f"voiceml-python/{__version__} (+https://github.com/voicetel/voiceml-python-sdk)"

_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})


class _Transport:
    """Shared config/state for sync and async transports.

    VoiceML uses HTTP Basic auth with ``AccountSid`` as the username and the per-tenant
    API key as the password. The pair is held here so callers can build a ``Client`` once
    and re-use it across resource groups.
    """

    def __init__(
        self,
        *,
        account_sid: str,
        api_key: str,
        base_url: str,
        max_retries: int,
        user_agent: str,
    ) -> None:
        if not account_sid:
            raise ConfigurationError("account_sid is required")
        if not api_key:
            raise ConfigurationError("api_key is required")
        if max_retries < 0:
            raise ConfigurationError("max_retries must be >= 0")
        self._account_sid = account_sid
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._user_agent = user_agent

    @property
    def account_sid(self) -> str:
        return self._account_sid

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def base_url(self) -> str:
        return self._base_url

    def _auth(self) -> tuple[str, str]:
        return (self._account_sid, self._api_key)

    def _headers(self) -> dict[str, str]:
        return {"User-Agent": self._user_agent, "Accept": "application/json"}


class Transport(_Transport):
    """Sync HTTP transport. Owns an :class:`httpx.Client` and the retry/auth policy."""

    def __init__(
        self,
        *,
        account_sid: str,
        api_key: str,
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
        self._http: httpx.Client = http_client or httpx.Client(
            base_url=self._base_url, timeout=timeout
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = self._http.request(
                    method,
                    path,
                    params=_clean_params(params),
                    data=_clean_form(data),
                    json=json,
                    headers=self._headers(),
                    auth=self._auth(),
                )
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise ApiError(
                        f"transport error after {attempt + 1} attempts: {exc}",
                        status_code=0,
                    ) from exc
                _sleep_backoff(attempt)
                continue
            if response.status_code in _RETRYABLE_STATUSES and attempt < self._max_retries:
                _sleep_backoff(attempt, response)
                continue
            return _parse(response)
        assert last_exc is not None  # pragma: no cover
        raise last_exc  # pragma: no cover

    def fetch_bytes(self, path: str) -> tuple[int, bytes, httpx.Headers]:
        """Fetch a binary payload (audio/wav recordings). Follows the single 302→presigned
        redirect that ``GET /Recordings/{sid}.wav`` issues when the audio has been archived
        to S3 — the caller usually only cares about the final bytes.
        """
        response = self._http.request(
            "GET",
            path,
            headers=self._headers(),
            auth=self._auth(),
            follow_redirects=True,
        )
        if not 200 <= response.status_code < 300:
            _parse(response)
        return response.status_code, response.content, response.headers

    def close(self) -> None:
        if self._owns_client:
            self._http.close()

    def __enter__(self) -> Transport:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


class AsyncTransport(_Transport):
    """Async counterpart to :class:`Transport`. Same surface, awaitable :meth:`request`."""

    def __init__(
        self,
        *,
        account_sid: str,
        api_key: str,
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
        self._http: httpx.AsyncClient = http_client or httpx.AsyncClient(
            base_url=self._base_url, timeout=timeout
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await self._http.request(
                    method,
                    path,
                    params=_clean_params(params),
                    data=_clean_form(data),
                    json=json,
                    headers=self._headers(),
                    auth=self._auth(),
                )
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    raise ApiError(
                        f"transport error after {attempt + 1} attempts: {exc}",
                        status_code=0,
                    ) from exc
                await asyncio.sleep(_backoff_delay(attempt))
                continue
            if response.status_code in _RETRYABLE_STATUSES and attempt < self._max_retries:
                await asyncio.sleep(_backoff_delay(attempt, response))
                continue
            return _parse(response)
        assert last_exc is not None  # pragma: no cover
        raise last_exc  # pragma: no cover

    async def fetch_bytes(self, path: str) -> tuple[int, bytes, httpx.Headers]:
        response = await self._http.request(
            "GET",
            path,
            headers=self._headers(),
            auth=self._auth(),
            follow_redirects=True,
        )
        if not 200 <= response.status_code < 300:
            _parse(response)
        return response.status_code, response.content, response.headers

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    async def __aenter__(self) -> AsyncTransport:
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.aclose()


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Drop ``None`` values. Keep empty strings — Twilio uses them as "explicit clear" tokens."""
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}


def _clean_form(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None:
        return None
    out: dict[str, Any] = {}
    for k, v in data.items():
        if v is None:
            continue
        if isinstance(v, bool):
            out[k] = "true" if v else "false"
        else:
            out[k] = v
    return out


def _parse(response: httpx.Response) -> Any:
    if 200 <= response.status_code < 300:
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError as exc:
            raise ApiError(
                f"non-JSON success response: {response.text[:200]}",
                status_code=response.status_code,
                body=response.text,
            ) from exc
    body: Any
    try:
        body = response.json()
    except ValueError:
        body = response.text
    code: int | str | None = None
    more_info: str | None = None
    message = f"HTTP {response.status_code}"
    if isinstance(body, dict):
        raw_code = body.get("code")
        if isinstance(raw_code, (int, str)):
            code = raw_code
        message = body.get("message") or message
        raw_more_info = body.get("more_info")
        if isinstance(raw_more_info, str) and raw_more_info:
            more_info = raw_more_info
    raise from_response(response.status_code, code, body, message, more_info=more_info)


def _backoff_delay(attempt: int, response: httpx.Response | None = None) -> float:
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return max(0.0, float(retry_after))
            except ValueError:
                pass
    return float(min(8.0, 0.5 * (2**attempt)))


def _sleep_backoff(attempt: int, response: httpx.Response | None = None) -> None:
    time.sleep(_backoff_delay(attempt, response))
