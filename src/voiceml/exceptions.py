from __future__ import annotations

from typing import Any


class VoiceMLError(Exception):
    """Base class for every error raised by this SDK."""


class ConfigurationError(VoiceMLError):
    """Raised when the client is constructed with conflicting or missing config.

    Also raised when an authenticated operation is called on a client created
    without credentials (see :class:`voiceml.Client` — credential-less clients
    can only call ``client.diagnostics``).
    """


class PaginationError(VoiceMLError):
    """Raised when a list response links to a next page the SDK refuses to follow.

    ``/v1`` list envelopes carry an absolute ``meta.next_page_url``. The SDK only
    follows it when its scheme and host equal the configured product host, so
    credentials are never sent to a different origin.
    """


class ApiError(VoiceMLError):
    """Raised when a request fails: a non-2xx response, an undecodable body, or a
    network failure (see :class:`APIConnectionError`).

    Subclasses cover specific status families; catch :class:`ApiError` to handle them all.
    The Twilio-compatible error body (``{code, message, more_info, status}``) is parsed into
    :attr:`code` / :attr:`message` / :attr:`more_info` when present, with the raw payload
    exposed on :attr:`body`. ``more_info`` is the documentation URL included for each
    error code. :attr:`retry_after` carries the parsed ``Retry-After`` header (seconds)
    when the server sent one.
    """

    message: str
    status_code: int
    code: int | None
    more_info: str | None
    body: Any
    retry_after: float | None

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: int | None = None,
        more_info: str | None = None,
        body: Any = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.more_info = more_info
        self.body = body
        self.retry_after = retry_after

    def __repr__(self) -> str:
        return f"{type(self).__name__}(status_code={self.status_code}, code={self.code!r})"


class APIConnectionError(ApiError):
    """The request never produced an HTTP response (DNS failure, refused connection,
    TLS failure, connection reset, …). ``status_code`` is ``0``; the underlying
    ``httpx`` exception is preserved as ``__cause__``.
    """


class APITimeoutError(APIConnectionError):
    """The request timed out (connect, read, write or pool timeout)."""


class BadRequestError(ApiError):
    """HTTP 400 — the request was malformed or failed server-side validation."""


class AuthenticationError(ApiError):
    """HTTP 401 — Basic auth missing, account unknown, key wrong, or source IP not allowed.

    The server intentionally returns an identical 401 for all four failure modes — see the
    spec's `Unauthorized` response description.
    """


class PermissionDeniedError(ApiError):
    """HTTP 403 — authenticated, but not allowed to perform this action."""


class NotFoundError(ApiError):
    """HTTP 404 — the resource does not exist (or belongs to a different tenant)."""


class MethodNotAllowedError(ApiError):
    """HTTP 405 — the endpoint does not support this HTTP method."""


class ConflictError(ApiError):
    """HTTP 409 — request conflicts with current resource state.

    Typical cases: deleting a queue that still has waiting members, or an
    optimistic-lock failure on ``accounts.update`` (code 20409).
    """


class RateLimitError(ApiError):
    """HTTP 429 — per-account rate limit exceeded.

    :attr:`retry_after` holds the server's ``Retry-After`` hint in seconds when present.
    """


class GoneError(ApiError):
    """HTTP 410 — recording audio is no longer available (no local file, no S3 key)."""


class NotImplementedAPIError(ApiError):
    """HTTP 501 — endpoint is mounted as a stub (e.g. UserDefinedMessages)."""


class ServerError(ApiError):
    """HTTP 5xx — the server hit an error processing the request (includes 503 from
    ``/health`` when a hard check fails)."""


def from_response(
    status_code: int,
    code: int | None,
    body: Any,
    message: str,
    *,
    more_info: str | None = None,
    retry_after: float | None = None,
) -> ApiError:
    """Map an HTTP status to the most specific :class:`ApiError` subclass."""
    cls: type[ApiError]
    if status_code == 400:
        cls = BadRequestError
    elif status_code == 401:
        cls = AuthenticationError
    elif status_code == 403:
        cls = PermissionDeniedError
    elif status_code == 404:
        cls = NotFoundError
    elif status_code == 405:
        cls = MethodNotAllowedError
    elif status_code == 409:
        cls = ConflictError
    elif status_code == 410:
        cls = GoneError
    elif status_code == 429:
        cls = RateLimitError
    elif status_code == 501:
        cls = NotImplementedAPIError
    elif 500 <= status_code < 600:
        cls = ServerError
    else:
        cls = ApiError
    return cls(
        message,
        status_code=status_code,
        code=code,
        more_info=more_info,
        body=body,
        retry_after=retry_after,
    )
