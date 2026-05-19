from __future__ import annotations

from typing import Any


class VoiceMLError(Exception):
    """Base class for every error raised by this SDK."""


class ConfigurationError(VoiceMLError):
    """Raised when the client is constructed with conflicting or missing config."""


class ApiError(VoiceMLError):
    """Raised when the API returns a non-2xx response.

    Subclasses cover specific status families; catch :class:`ApiError` to handle them all.
    The Twilio-shape error body (``{code, message, more_info, status}``) is parsed into
    :attr:`code` / :attr:`message` when present, with the raw payload exposed on :attr:`body`.
    """

    status_code: int
    code: int | str | None
    body: Any

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: int | str | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.body = body

    def __repr__(self) -> str:
        return f"{type(self).__name__}(status_code={self.status_code}, code={self.code!r})"


class BadRequestError(ApiError):
    """HTTP 400 — the request was malformed or failed server-side validation."""


class AuthenticationError(ApiError):
    """HTTP 401 — Basic auth missing, account unknown, key wrong, or source IP not allowed.

    The server intentionally returns an identical 401 for all four failure modes — see the
    Twilio-compat spec's `Unauthorized` response description.
    """


class PermissionDeniedError(ApiError):
    """HTTP 403 — authenticated, but not allowed to perform this action."""


class NotFoundError(ApiError):
    """HTTP 404 — the resource does not exist (or belongs to a different tenant)."""


class ConflictError(ApiError):
    """HTTP 409 — request conflicts with current resource state.

    Typical case: deleting a queue that still has waiting members.
    """


class RateLimitError(ApiError):
    """HTTP 429 — per-account rate limit exceeded. ``Retry-After`` header may hint when to retry."""


class GoneError(ApiError):
    """HTTP 410 — recording audio is no longer available (no local file, no S3 key)."""


class NotImplementedAPIError(ApiError):
    """HTTP 501 — endpoint is mounted as a stub (e.g. UserDefinedMessages)."""


class ServerError(ApiError):
    """HTTP 5xx — the server hit an error processing the request."""


def from_response(status_code: int, code: int | str | None, body: Any, message: str) -> ApiError:
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
    return cls(message, status_code=status_code, code=code, body=body)
