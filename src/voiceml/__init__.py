"""Official Python SDK for the VoiceML REST API.

VoiceML is VoiceTel's voice, messaging and answering-machine-detection service with a
Twilio-compatible REST API (``https://voiceml.voicetel.com``), so code written against
Twilio-compatible clients is migration-compatible. Authenticate with your AccountSid
and a VoiceML API key.

Quickstart::

    from voiceml import Client
    from voiceml.models import CreateCallRequest

    with Client(account_sid="AC…", api_key="…") as c:
        call = c.calls.create(
            CreateCallRequest(
                To="+14155550100",
                From="+14155550101",
                Url="https://example.com/twiml",
                MachineDetection="DetectMessageEnd",
            )
        )
        print(call.sid, call.status)

Docs: https://voicetel.com/docs/api/v0.9/voiceml/
"""

from __future__ import annotations

from . import models, webhooks
from ._version import __version__
from .client import AsyncClient, Client
from .exceptions import (
    APIConnectionError,
    ApiError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConfigurationError,
    ConflictError,
    GoneError,
    MethodNotAllowedError,
    NotFoundError,
    NotImplementedAPIError,
    PaginationError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    VoiceMLError,
)
from .webhooks import RequestValidator, validate_request

__all__ = [
    "APIConnectionError",
    "APITimeoutError",
    "ApiError",
    "AsyncClient",
    "AuthenticationError",
    "BadRequestError",
    "Client",
    "ConfigurationError",
    "ConflictError",
    "GoneError",
    "MethodNotAllowedError",
    "NotFoundError",
    "NotImplementedAPIError",
    "PaginationError",
    "PermissionDeniedError",
    "RateLimitError",
    "RequestValidator",
    "ServerError",
    "VoiceMLError",
    "__version__",
    "models",
    "validate_request",
    "webhooks",
]
