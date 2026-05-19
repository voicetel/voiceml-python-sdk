"""Base class shared by every model in this package.

Two policies:

- **Permissive on the way in.** ``extra="allow"`` lets the server add new fields without
  breaking validation. Clients pinned to today's models will simply ignore additions.
- **Tight on the way out.** :meth:`to_form` serializes only the fields the caller
  explicitly set into a form-encoded body — the wire shape VoiceML expects on every POST.
  Twilio sends ``application/x-www-form-urlencoded`` by default, and so does this SDK.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    """Common Pydantic config for every model in this package."""

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        str_strip_whitespace=False,
    )

    def to_form(self) -> dict[str, Any]:
        """Render as a form-encodable dict.

        Only fields the caller explicitly set are emitted. Booleans become ``"true"``/
        ``"false"`` (Twilio convention). List values are kept as lists so httpx encodes
        them as repeated form params (e.g. ``StatusCallbackEvent=ringing&...=completed``).
        """
        raw = self.model_dump(exclude_unset=True, by_alias=True, mode="json")
        out: dict[str, Any] = {}
        for k, v in raw.items():
            if v is None:
                continue
            if isinstance(v, bool):
                out[k] = "true" if v else "false"
            elif isinstance(v, (list, tuple)) and not isinstance(v, (str, bytes)):
                out[k] = list(v)
            else:
                out[k] = v
        return out


def encode_list(values: Sequence[str] | None) -> list[str] | None:
    """Helper for resources that accept a list query/form param built ad-hoc."""
    if values is None:
        return None
    return list(values)
