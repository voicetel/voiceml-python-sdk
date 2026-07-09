"""Per-product host resolution for the VoiceML API.

Twilio splits its products across dedicated subdomains (``api.twilio.com``,
``conversations.twilio.com``, ``messaging.twilio.com``, …). VoiceML mirrors
that shape on ``voicetel.com``: the Conversations product answers on
``conversations.voicetel.com`` and the Messaging Service product on
``messaging.voicetel.com``, while everything else stays on the default
``voiceml.voicetel.com`` host. Conversation Service and Messaging Service share
the identical ``/v1/Services`` path shape, so the *host* is what disambiguates
them on the wire.

Given the configured ``base_url`` this module derives the two product hosts by
swapping the leftmost ``voiceml`` label — but only for recognised
``*.voicetel.com`` hosts. For any other base URL (a self-hosted callBroadcast
instance, a test stub, a regional override) the product hosts fall back to the
configured host unchanged, so a single-host deployment keeps working. A caller
who needs Messaging Service against a custom host points ``messaging_base_url``
(or ``conversations_base_url``) at their own subdomain explicitly.
"""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit


def _derive_product_host(base_url: str, product: str) -> str:
    """Swap the ``voiceml`` label of a ``*.voicetel.com`` host for ``product``.

    Returns ``base_url`` unchanged when the host is not a ``voiceml.*.voicetel.com``
    style host (e.g. a self-hosted instance), so single-host deployments keep
    working without special-casing.
    """
    parts = urlsplit(base_url)
    host = parts.hostname
    if not host or not host.endswith(".voicetel.com"):
        return base_url
    labels = host.split(".")
    if "voiceml" not in labels:
        return base_url
    labels[labels.index("voiceml")] = product
    new_host = ".".join(labels)
    netloc = new_host if parts.port is None else f"{new_host}:{parts.port}"
    return urlunsplit((parts.scheme, netloc, parts.path, "", ""))


def resolve_product_base_urls(
    base_url: str,
    messaging_base_url: str | None = None,
    conversations_base_url: str | None = None,
) -> tuple[str, str, str]:
    """Return ``(default, messaging, conversations)`` base URLs.

    Explicit overrides win; otherwise each product host is derived from
    ``base_url`` (see module docstring). All three are returned without a
    trailing slash.
    """
    default = base_url.rstrip("/")
    messaging = (
        messaging_base_url or _derive_product_host(default, "messaging")
    ).rstrip("/")
    conversations = (
        conversations_base_url or _derive_product_host(default, "conversations")
    ).rstrip("/")
    return default, messaging, conversations
