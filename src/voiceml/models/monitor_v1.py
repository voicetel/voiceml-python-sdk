"""Monitor v1 — the Alert resource (``/v1/Alerts``).

A Monitor Alert is a failure event — a call-scoped error or a messaging
delivery failure — rendered in the Alert shape. The list view omits the
request/response detail; :meth:`fetch` includes it when the row carries
any. Paths sit at ``/v1/`` (no account namespace); the account is
resolved from HTTP Basic auth.

The server currently answers a single page (``meta.next_page_url`` is
always ``null``), and ``PageSize`` caps the rows returned (default 50,
capped at 1000).
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base
from .common import V1Page
from .common import VoiceV1Meta as VoiceV1Meta

MonitorV1LogLevel = Literal["error", "warning"]


class MonitorV1Alert(_Base):
    """One failure event in the Monitor Alert shape.

    ``request_headers`` / ``request_variables`` / ``response_body`` /
    ``response_headers`` only appear on :meth:`fetch`, and only when the
    underlying event stored them.
    """

    sid: str
    account_sid: str
    alert_text: str
    error_code: str
    log_level: MonitorV1LogLevel | str
    more_info: str
    request_method: str
    request_url: str
    url: str
    date_created: str
    date_generated: str
    date_updated: str
    api_version: str | None = None
    resource_sid: str | None = None
    service_sid: str | None = None
    request_headers: str | None = None
    request_variables: str | None = None
    response_body: str | None = None
    response_headers: str | None = None


class MonitorV1AlertList(V1Page[MonitorV1Alert]):
    alerts: list[MonitorV1Alert] = Field(default_factory=list)
