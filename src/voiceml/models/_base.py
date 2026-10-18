"""Base classes shared by every model in this package.

Two policies:

- **Tolerant on the way in.** Response models (:class:`_Base`) use ``extra="allow"``
  so the server can add fields without breaking validation, and response enums are
  typed as open strings so a new server-side value never fails a call.
- **Strict on the way out.** Request models (:class:`_Request`) use
  ``extra="forbid"``: a misspelled field raises ``ValidationError`` instead of being
  sent as a wire parameter. :meth:`_Request.to_form` serializes only the fields the
  caller explicitly set — the ``application/x-www-form-urlencoded`` body VoiceML
  expects on every ``/2010-04-01`` POST.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import date, datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    """Common Pydantic config for every response model in this package."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=False,
    )


def form_value(value: Any) -> Any:
    """Render one value for a form body or query string.

    * booleans → ``true`` / ``false``
    * ``datetime`` → ISO-8601 UTC (``2026-07-01T12:00:00Z``); naive values are taken as UTC
    * ``date`` → ``YYYY-MM-DD``
    * dicts → compact JSON (``Attributes``-style JSON-typed fields)
    * lists → kept as lists so httpx emits repeated keys (never ``Key[0]=…``)
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return json.dumps(value, separators=(",", ":"))
    if isinstance(value, (list, tuple)):
        return [form_value(v) for v in value]
    return value


class _Request(BaseModel):
    """Common Pydantic config for every request model in this package."""

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=False,
    )

    def to_form(self) -> dict[str, Any]:
        """Render as a form-encodable dict keyed by wire (PascalCase) names.

        Only fields the caller explicitly set are emitted, and ``None`` is dropped;
        ``""`` is kept because the API treats it as "clear this value". Values are
        rendered with :func:`form_value`.
        """
        raw = self.model_dump(exclude_unset=True, by_alias=True, mode="python")
        return {k: form_value(v) for k, v in raw.items() if v is not None}

    def to_json(self) -> dict[str, Any]:
        """Render as a JSON body keyed by wire names (unset / ``None`` fields dropped)."""
        raw = self.model_dump(exclude_unset=True, by_alias=True, mode="json")
        return {k: v for k, v in raw.items() if v is not None}


def encode_list(values: Sequence[str] | None) -> list[str] | None:
    """Helper for resources that accept a list query/form param built ad-hoc."""
    if values is None:
        return None
    return list(values)
