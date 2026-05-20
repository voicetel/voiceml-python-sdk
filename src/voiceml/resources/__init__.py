"""All resource groups, exported for the top-level client."""

from __future__ import annotations

from .applications import ApplicationsAsyncResource, ApplicationsResource
from .calls import CallsAsyncResource, CallsResource
from .conferences import ConferencesAsyncResource, ConferencesResource
from .diagnostics import DiagnosticsAsyncResource, DiagnosticsResource
from .incoming_phone_numbers import (
    IncomingPhoneNumbersAsyncResource,
    IncomingPhoneNumbersResource,
)
from .queues import QueuesAsyncResource, QueuesResource
from .recordings import RecordingsAsyncResource, RecordingsResource

__all__ = [
    "ApplicationsAsyncResource",
    "ApplicationsResource",
    "CallsAsyncResource",
    "CallsResource",
    "ConferencesAsyncResource",
    "ConferencesResource",
    "DiagnosticsAsyncResource",
    "DiagnosticsResource",
    "IncomingPhoneNumbersAsyncResource",
    "IncomingPhoneNumbersResource",
    "QueuesAsyncResource",
    "QueuesResource",
    "RecordingsAsyncResource",
    "RecordingsResource",
]
