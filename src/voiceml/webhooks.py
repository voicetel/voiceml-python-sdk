"""Validate the ``X-Twilio-Signature`` header VoiceML puts on outbound webhooks.

VoiceML signs every webhook it sends (voice URLs, status callbacks, …) with the
account's **API key**, using the same scheme as Twilio-compatible validators:

1. Start from the full URL the request was sent to, with any ``#fragment`` removed.
2. For ``POST`` form bodies, append ``key + value`` for every form key in ascending
   (byte-order) key order; a key that repeats contributes each value in the order
   received. ``GET`` requests are signed over the URL alone.
3. HMAC-SHA1 the result with the API key and Base64-encode it (standard, padded).

:func:`validate_request` compares in constant time and, as Twilio-compatible validators do,
also accepts the URL with the default port added or removed (``:443`` for https,
``:80`` for http), since proxies and load balancers often rewrite it.

Example (Flask)::

    from voiceml.webhooks import validate_request

    ok = validate_request(
        api_key=os.environ["VOICEML_API_KEY"],
        url=request.url,
        params=list(request.form.items(multi=True)),
        signature=request.headers.get("X-Twilio-Signature", ""),
    )
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from collections.abc import Iterable, Mapping, Sequence
from urllib.parse import urlsplit

__all__ = [
    "SIGNATURE_HEADER",
    "RequestValidator",
    "WebhookParams",
    "compute_signature",
    "validate_request",
]

#: Header carrying the signature on every VoiceML webhook.
SIGNATURE_HEADER = "X-Twilio-Signature"

#: Form parameters: a mapping (values may be lists for repeated keys) or an iterable
#: of ``(key, value)`` pairs in the order received.
WebhookParams = Mapping[str, str | Sequence[str]] | Iterable[tuple[str, str]]

_DEFAULT_PORTS = {"https": 443, "http": 80}


def _pairs(params: WebhookParams | None) -> list[tuple[str, str]]:
    if params is None:
        return []
    if isinstance(params, Mapping):
        getlist = getattr(params, "getlist", None)
        out: list[tuple[str, str]] = []
        for key in params:
            if callable(getlist):
                values = list(getlist(key))
            else:
                raw = params[key]
                values = [raw] if isinstance(raw, str) else list(raw)
            out.extend((str(key), str(v)) for v in values)
        return out
    return [(str(k), str(v)) for k, v in params]


def _signing_payload(url: str, params: WebhookParams | None) -> str:
    base = url.split("#", 1)[0]
    pairs = _pairs(params)
    # Stable sort: equal keys keep their received value order.
    pairs.sort(key=lambda kv: kv[0].encode("utf-8"))
    return base + "".join(k + v for k, v in pairs)


def compute_signature(api_key: str, url: str, params: WebhookParams | None = None) -> str:
    """Return the Base64 HMAC-SHA1 signature VoiceML would send for this request.

    Pass ``params`` for ``POST`` form bodies; leave it ``None`` for ``GET``.
    """
    digest = hmac.new(
        api_key.encode("utf-8"),
        _signing_payload(url, params).encode("utf-8"),
        hashlib.sha1,
    ).digest()
    return base64.b64encode(digest).decode("ascii")


def _url_variants(url: str) -> list[str]:
    """``url`` plus the same URL with the scheme's default port added or removed."""
    base = url.split("#", 1)[0]
    parts = urlsplit(base)
    default = _DEFAULT_PORTS.get(parts.scheme.lower())
    if default is None or not parts.netloc:
        return [base]
    userinfo, at, hostport = parts.netloc.rpartition("@")
    prefix = userinfo + at
    try:
        port = parts.port
    except ValueError:
        return [base]
    if port is None:
        alternate = f"{prefix}{hostport}:{default}"
    elif port == default:
        alternate = prefix + hostport[: hostport.rfind(":")]
    else:
        return [base]
    return [base, base.replace("//" + parts.netloc, "//" + alternate, 1)]


def validate_request(
    api_key: str,
    url: str,
    params: WebhookParams | None,
    signature: str,
) -> bool:
    """Return ``True`` if ``signature`` is a valid VoiceML signature for the request.

    ``url`` is the full URL the webhook was delivered to (scheme, host, path and query);
    ``params`` the POST form parameters (``None`` for GET); ``signature`` the value of
    the ``X-Twilio-Signature`` header. Comparison is constant-time.
    """
    if not api_key or not signature:
        return False
    expected = signature.encode("utf-8")
    valid = False
    for candidate in _url_variants(url):
        computed = compute_signature(api_key, candidate, params).encode("utf-8")
        # Evaluate every candidate so timing does not depend on which one matched.
        valid = hmac.compare_digest(computed, expected) or valid
    return valid


class RequestValidator:
    """Object form of :func:`validate_request`, bound to one API key.

    ``RequestValidator(api_key).validate(url, params, signature)`` is a
    migration-compatible interface for code written against twilio-python.
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def __repr__(self) -> str:
        return "RequestValidator(api_key=***)"

    def compute_signature(self, url: str, params: WebhookParams | None = None) -> str:
        return compute_signature(self._api_key, url, params)

    def validate(self, url: str, params: WebhookParams | None, signature: str) -> bool:
        return validate_request(self._api_key, url, params, signature)
