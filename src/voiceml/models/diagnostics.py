"""Notifications, events, and /health — read-only diagnostic surfaces."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ._base import _Base
from .common import HealthFailure


class NotificationsList(_Base):
    """``GET /Calls/{sid}/Notifications`` — always an empty list (compat stub)."""

    notifications: list[Any] = Field(default_factory=list)
    page: int = 0
    page_size: int = 0
    total: int = 0
    uri: str | None = None


class EventsList(_Base):
    """``GET /Calls/{sid}/Events`` — always an empty list (compat stub).

    Canonical event source is the customer's StatusCallback URL.
    """

    events: list[Any] = Field(default_factory=list)
    page: int = 0
    page_size: int = 0
    total: int = 0
    uri: str | None = None


class HealthStatus(_Base):
    """``GET /health`` response — composite probe.

    Hard-check failures flip ``ok`` to False (server returns 503). Soft-check warnings
    surface in ``warnings`` only and don't take the host out of rotation.
    """

    ok: bool
    warnings: list[HealthFailure] = Field(default_factory=list)
    failures: list[HealthFailure] = Field(default_factory=list)
