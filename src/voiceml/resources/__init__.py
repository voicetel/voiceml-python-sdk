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
from .messages import MessagesAsyncResource, MessagesResource
from .notifications import NotificationsAsyncResource, NotificationsResource
from .queues import QueuesAsyncResource, QueuesResource
from .recordings import RecordingsAsyncResource, RecordingsResource
from .routes_v2 import RoutesV2AsyncResource, RoutesV2Resource
from .sip import SipAsyncResource, SipResource

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
    "MessagesAsyncResource",
    "MessagesResource",
    "NotificationsAsyncResource",
    "NotificationsResource",
    "QueuesAsyncResource",
    "QueuesResource",
    "RecordingsAsyncResource",
    "RecordingsResource",
    "RoutesV2AsyncResource",
    "RoutesV2Resource",
    "SipAsyncResource",
    "SipResource",
]
