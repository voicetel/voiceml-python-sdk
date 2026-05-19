"""Official Python SDK for the VoiceML REST API.

VoiceML is VoiceTel's outbound voice + AMD service with a Twilio-shaped REST surface
(``https://voiceml.voicetel.com``). The wire shape, auth model, error codes, and
pagination envelope all match Twilio's documented behaviour — so existing Twilio
client patterns map across.

Quickstart::

    from voiceml import Client
    from voiceml.models import CreateCallRequest

    with Client(account_sid="AC…", api_key="…") as c:
        call = c.calls.create(
            CreateCallRequest(
                To="+18005551234",
                From="+18005550000",
                Url="https://example.com/twiml",
                MachineDetection="DetectMessageEnd",
            )
        )
        print(call.sid, call.status)
"""

from __future__ import annotations

from . import models
from ._version import __version__
from .client import AsyncClient, Client
from .exceptions import (
    ApiError,
    AuthenticationError,
    BadRequestError,
    ConfigurationError,
    ConflictError,
    GoneError,
    NotFoundError,
    NotImplementedAPIError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    VoiceMLError,
)

__all__ = [
    "ApiError",
    "AsyncClient",
    "AuthenticationError",
    "BadRequestError",
    "Client",
    "ConfigurationError",
    "ConflictError",
    "GoneError",
    "NotFoundError",
    "NotImplementedAPIError",
    "PermissionDeniedError",
    "RateLimitError",
    "ServerError",
    "VoiceMLError",
    "__version__",
    "models",
]
