# 📞 VoiceML Python SDK

The official Python client for the [VoiceML REST API](https://voicetel.com/docs/api/v0.9/voiceml/) — VoiceTel's Twilio-compatible voice, messaging and answering-machine-detection API — with typed, async-ready Python.

![Version](https://img.shields.io/badge/version-0.9.3-blue)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)
![License](https://img.shields.io/badge/license-MIT%20%2B%20Commons%20Clause-green)
[![CI](https://github.com/voicetel/voiceml-python-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/voicetel/voiceml-python-sdk/actions/workflows/ci.yml)
![Typed](https://img.shields.io/badge/typed-pydantic--v2-blue)

## 📚 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quickstart](#-quickstart)
- [Authentication](#-authentication)
- [Resource Reference](#-resource-reference)
- [Error Handling](#-error-handling)
- [Retries and Rate Limits](#-retries-and-rate-limits)
- [Async Support](#-async-support)
- [Pagination](#-pagination)
- [Webhook Signatures](#-webhook-signatures)
- [Diagnostics](#-diagnostics)
- [Migrating from twilio-python](#-migrating-from-twilio-python)
- [Development](#-development)
- [API Documentation](#-api-documentation)
- [Contributors](#-contributors)
- [Sponsors](#-sponsors)
- [License](#-license)

## ✨ Features

### 🛡️ Typed end to end
- **All 333 of the 333 operations** in the published OpenAPI document are covered. A spec-driven contract test calls every SDK method and checks method, path, host, auth and parameters against the spec.
- **Pydantic v2 models** for requests and responses. Request models reject unknown fields and out-of-range enum values before anything is sent; response models tolerate `null`s, new enum values and new fields, so a server-side addition never breaks your code.
- **Autocomplete everywhere** — `Call.sid`, `Recording.duration`, `Queue.current_size`, `Message.from_` (the wire field `from`) and `Message.to` are all typed.

### ⚡ Sync + async, same surface
- `Client` for blocking calls, `AsyncClient` for `await` — the same resources, method names and return types. `iter()` / `paginate()` are lazy iterators (async iterators on `AsyncClient`).
- Built on `httpx`: connection pooling, and you can inject your own `httpx.Client` / `httpx.AsyncClient` (proxies, TLS settings, mock transports).

### 🔁 Safe transport
- **Retries that never duplicate a call or SMS** — see [Retries and Rate Limits](#-retries-and-rate-limits).
- **`Retry-After`** honoured as seconds or an HTTP date, capped at 60 seconds.
- **Typed errors** for every failure, including timeouts and network errors.
- Credentials never appear in `repr()` / `str()` output, and are never sent to a redirect target on another host.

## 🚀 Installation

```bash
pip install voiceml
```

Requires Python 3.10 or later. CI tests 3.10, 3.11, 3.12 and 3.13, plus the minimum supported `httpx` (0.27) and `pydantic` (2.8).

> This README documents the `main` branch. Changes not yet on PyPI are listed under **Unreleased** in [CHANGELOG.md](CHANGELOG.md).

## 🏁 Quickstart

```python
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

    for queue in c.queues.iter():
        print(queue.friendly_name, queue.current_size)
```

## 🔑 Authentication

VoiceML uses **HTTP Basic** auth: your `AccountSid` is the username and your **VoiceML API key** is the password — the same positions Twilio SDKs use for the AccountSid and auth token. Twilio-issued credentials do **not** work with VoiceML; use the API key issued for your VoiceML account.

```python
from voiceml import Client

with Client(account_sid="AC…", api_key="…") as c:
    account = c.accounts.fetch()
    print(account.friendly_name, account.status)
```

`auth_token=` is accepted as an alias for `api_key=`. Don't have credentials yet? See **[voicetel.com/docs/api/v0.9/voiceml/](https://voicetel.com/docs/api/v0.9/voiceml/)** for issuance and rotation.

## 🗺️ Resource Reference

| Resource | Sync + Async | Covers |
|---|---|---|
| `client.calls` | create, get, list, iter, update, delete | per-call recordings (incl. `Twilio.CURRENT`), start/stop streams, SIPREC and live transcriptions, notifications, events, payments, user-defined messages |
| `client.conferences` | get, list, iter, end | participants (create / mute / hold / kick), recordings (start, list, update, delete) |
| `client.queues` | create, get, list, iter, update, delete | members: list, get, peek / dequeue front or a specific member |
| `client.applications` | create, get, list, update, delete | voice + SMS callback bundles |
| `client.recordings` | get, list, iter, delete, `get_audio` | recording transcriptions (list, get, delete); audio follows the archive redirect without forwarding credentials |
| `client.transcriptions` | get, list, iter, delete | account-wide recording transcriptions |
| `client.messages` | create (SMS / MMS), fetch, list, iter, update, delete, `create_feedback` | media: `list_media`, `get_media`, `delete_media` |
| `client.incoming_phone_numbers` | create, get, list, iter, update, delete | voice + SMS routing; `list_/create_` `local`, `mobile`, `toll_free` |
| `client.outgoing_caller_ids` | create (verification), get, list, iter, update, delete | |
| `client.accounts` | fetch, update, `rotate_key` | the authenticated account (`ConflictError` on concurrent update); `rotate_key` returns the new API key once |
| `client.balance` | fetch | |
| `client.usage_records` | list, iter, `list_all_time`, `list_daily`, `list_last_month`, `list_monthly`, `list_this_month`, `list_today`, `list_yearly`, `list_yesterday` | |
| `client.notifications` | get, list | account-wide alert log |
| `client.monitor_v1` | alerts: list, iter, fetch | failure events (call errors and message delivery failures) |
| `client.exports` | list, download | daily event-log archives |
| `client.sip` | domains, credential_lists (+ credentials), ip_access_control_lists (+ ip_addresses), registrations | domain ↔ ACL / credential-list mappings (historical, `auth.calls`, `auth.registrations`) |
| `client.voice_v1` | byoc_trunks, connection_policies (+ targets), settings, source_ip_mappings, ip_records | |
| `client.routes_v2` | phone_numbers, sip_domains | inbound processing region |
| `client.pricing` | `v1.{voice,messaging,phone_numbers}`, `v2.{voice,trunking}` | read-only rate lookups |
| `client.conversations_v1` | conversations, messages, participants, webhooks, roles, users, credentials, configuration, services (+ service-scoped resources) | served from `conversations.voicetel.com` |
| `client.messaging_v1.services` | create, list, fetch, update, delete, `phone_numbers(sid)` | Messaging Service (`MG…`) and its sender pool, served from `messaging.voicetel.com` |
| `client.assistants_v1` | assistants (+ tools, knowledge, feedback, messages), tools, knowledge, sessions, policies | JSON bodies |
| `client.diagnostics` | `health`, `openapi_json`, `openapi_yaml`, `openapi_yml` | no credentials needed — see [Diagnostics](#-diagnostics) |

Methods that take a request body accept either a typed model from `voiceml.models` or keyword arguments:

```python
from voiceml import Client
from voiceml.models import CreateCallRequest

with Client(account_sid="AC…", api_key="…") as c:
    call = c.calls.create(CreateCallRequest(
        To="+14155550100",
        From="+14155550101",
        Url="https://example.com/twiml",
    ))
    # On a live call, open a Pay session:
    session = c.calls.start_payment(
        call.sid,
        idempotency_key="order-482917",
        status_callback="https://example.com/pay-status",
    )
    print(session.sid)

    # SMS and MMS (at least one of body / media_url is required):
    message = c.messages.create(
        to="+14155550100",
        from_="+14155550101",
        body="Your order has shipped",
        media_url=["https://example.com/label.png"],
    )
    print(message.sid, message.status)

    # Confirm delivery of a message you sent:
    feedback = c.messages.create_feedback(message.sid, outcome="confirmed")
    print(feedback.outcome)

    # Scan failure events (call errors, message delivery failures):
    for alert in c.monitor_v1.alerts.iter(log_level="error", page_size=50):
        print(alert.error_code, alert.alert_text)

    # Rotate the API key (the new key is returned exactly once — store it now;
    # the previous key stops working immediately):
    rotated = c.accounts.rotate_key()
    print(rotated.sid, rotated.api_key[:4] + "…")
```

### Product hosts

Each product is served from its own host, as Twilio-compatible clients expect: Conversations on `conversations.voicetel.com`, the Messaging Service (including its sender pool) on `messaging.voicetel.com`, and everything else on `voiceml.voicetel.com`. Conversations and Messaging Service share the `/v1/Services` path, so the host is what tells them apart. The client derives these hosts from `base_url` automatically.

For a self-hosted deployment on a custom host, point the product base URLs at your own hosts explicitly (otherwise every product uses the single host you configured):

```python
from voiceml import Client

client = Client(
    account_sid="AC…",
    api_key="…",
    base_url="https://pbx.example.com",
    messaging_base_url="https://messaging.example.com",
    conversations_base_url="https://conversations.example.com",
)
client.close()
```

Requests always go to these configured hosts — the `base_url` of an injected `http_client` is never used. When you pass `http_client=`, its own timeout, proxy and TLS settings apply (the `timeout=` argument only configures the client the SDK creates for you).

## 🚨 Error Handling

Every failure raises a subclass of `voiceml.ApiError` (itself a `voiceml.VoiceMLError`):

| Condition | Exception |
|--------|-----------|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `PermissionDeniedError` |
| 404 | `NotFoundError` |
| 405 | `MethodNotAllowedError` |
| 409 | `ConflictError` |
| 410 | `GoneError` |
| 429 | `RateLimitError` |
| 501 | `NotImplementedAPIError` |
| other 5xx | `ServerError` |
| timeout | `APITimeoutError` (a subclass of `APIConnectionError`) |
| DNS / connection / TLS failure | `APIConnectionError` (`status_code == 0`) |
| other | `ApiError` |

```python
from voiceml import ApiError, Client, NotFoundError, RateLimitError

with Client(account_sid="AC…", api_key="…") as c:
    try:
        call = c.calls.get("CA0000000000000000000000000000aaaa")
    except NotFoundError:
        print("That call isn't on your account.")
    except RateLimitError as e:
        print(f"Slow down — retry in {e.retry_after or '?'}s")
    except ApiError as e:
        print(e.status_code, e.code, e.message, e.more_info)
```

The error body (`code`, `message`, `more_info`, `status`) is parsed into `error.code` (an `int`), `error.message` and `error.more_info`, with the raw payload on `error.body`. A non-JSON error body still raises the matching exception. The underlying `httpx` exception is preserved as `__cause__` for network errors. Misconfiguration (a bad `base_url`, missing credentials) raises `voiceml.ConfigurationError`.

## ⏱️ Retries and Rate Limits

The SDK retries up to `max_retries` times (default `2`):

- **`GET`, `DELETE`, `PUT`** are retried on 429, 500, 502, 503, 504 and on connection or read failures.
- **`POST` / `PATCH`** (e.g. `calls.create`, `messages.create`) are retried **only** on 429 and when the connection was never established (DNS failure, connection refused, connect timeout, TLS handshake failure). They are never retried after a 5xx, a read timeout or a reset connection, because the server may already have acted — so the SDK cannot place a duplicate call or send a duplicate SMS.
- A `Retry-After` header (seconds or HTTP date) sets the delay. If it asks for more than 60 seconds, the SDK raises `RateLimitError` (or `ServerError` for 503) immediately instead of sleeping, with the value on `error.retry_after`.
- Otherwise the delay is exponential backoff with full jitter (0.5 s base, 8 s maximum).

```python
from voiceml import Client

client = Client(account_sid="AC…", api_key="…", max_retries=4, timeout=60.0)
client.close()
```

## ⚡ Async Support

`AsyncClient` has the same surface as `Client`, with awaitable methods and async iterators:

```python
import asyncio

from voiceml import AsyncClient


async def main() -> None:
    async with AsyncClient(account_sid="AC…", api_key="…") as c:
        page = await c.calls.list(status="in-progress")
        for call in page.calls:
            print(call.sid, call.duration)
        async for call in c.calls.iter(status="completed", page_size=100):
            print(call.sid)


asyncio.run(main())
```

Cancelling a task cancels the in-flight request; cancellation is never retried.

## 📄 Pagination

`list()` returns one page: a `…List` model whose envelope carries `page`, `page_size`, `start`, `end`, `uri`, `first_page_uri`, `previous_page_uri` and `next_page_uri` (`/v1` lists carry a `meta` object instead). The SDK follows the server's `next_page_uri` (which carries a `PageToken`) verbatim — it never constructs page numbers itself.

```python
from voiceml import Client

with Client(account_sid="AC…", api_key="…") as c:
    # Lazy: one request per page, only as you iterate. Stop early and no further
    # requests are made.
    for call in c.calls.iter(status="completed", page_size=200):
        print(call.sid)

    for msg in c.messages.iter(from_="+14155550101", page_size=200):
        print(msg.sid)

    # Any list, page by page:
    page = c.applications.list(page_size=50)
    while page is not None:
        for app in page.applications:
            print(app.friendly_name)
        page = c.next_page(page)

    # Or flatten any list lazily:
    for number in c.paginate(c.incoming_phone_numbers.list()):
        print(number.phone_number)
```

`iter()` is available on calls, conferences, messages, queues, recordings, transcriptions, incoming phone numbers, outgoing caller IDs, usage records, SIP domains, SIP registrations and monitor v1 alerts; `client.paginate(page)` and `client.next_page(page)` work for every list. For `/v1` lists the SDK only follows `meta.next_page_url` when it points at the configured product host, and raises `voiceml.PaginationError` otherwise.

## ✍️ Webhook Signatures

VoiceML signs every webhook it sends with your API key in the `X-Twilio-Signature` header. Validate it before trusting the request:

```python
from voiceml import RequestValidator, validate_request

params = {
    "CallSid": "CA0123456789abcdef0123456789abcdef",
    "From": "+14155550100",
    "To": "+14155550101",
    "Digits": "1234",
    "AccountSid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
}
assert validate_request(
    api_key="test-api-key-0123456789",
    url="https://example.com/voice/answer?case=1",
    params=params,                      # POST form fields; None for GET
    signature="RweoLyWqNC7H8+MLXPb7EPz18OI=",
)

# Or bind the key once:
validator = RequestValidator("test-api-key-0123456789")
print(validator.validate("https://example.com:443/voice/answer?case=1", params,
                         "RweoLyWqNC7H8+MLXPb7EPz18OI="))
```

The signature is HMAC-SHA1 over the full URL (fragment removed) followed by each POST form `key + value` in sorted key order, Base64-encoded. Repeated form keys — pass a list of `(key, value)` pairs or a dict of lists — keep their received order. Comparison is constant-time, and the URL is also accepted with the default port (`:443` / `:80`) added or removed.

## 🩺 Diagnostics

`/health` and the OpenAPI documents need no credentials. They go through the client's normal transport (your `http_client`, timeout and proxy apply) and never send the `Authorization` header — so you can create a client without credentials just for them:

```python
from voiceml import Client, ServerError

with Client() as c:  # diagnostics-only client: no account_sid / api_key
    try:
        health = c.diagnostics.health()
        print(health.ok, [w.check for w in health.warnings])
    except ServerError as e:  # 503: a hard check failed
        print("unhealthy:", e.body)
    spec_yaml = c.diagnostics.openapi_yaml()
```

Any other call on a credential-less client raises `voiceml.ConfigurationError`.

## 🔁 Migrating from twilio-python

The constructor takes the same two values in the same positions — your AccountSid and, in place of the Twilio auth token, your **VoiceML API key**:

```python
# Before — twilio-python
#   from twilio.rest import Client as TwilioClient
#   client = TwilioClient("AC…", "<twilio-auth-token>")

# After — VoiceML (Twilio-compatible)
from voiceml import Client

client = Client(account_sid="AC…", api_key="<voiceml-api-key>")
client.close()
```

Method names follow the resource map above (`client.calls.create(...)`, `client.queues.list()`, …) rather than twilio-python's `client.api.v2010.accounts(sid).calls.create(...)` chain. Webhook validation moves from `twilio.request_validator.RequestValidator` to `voiceml.RequestValidator` — keyed with your VoiceML API key.

## 🛠️ Development

```bash
git clone https://github.com/voicetel/voiceml-python-sdk
cd voiceml-python-sdk
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Tests (no network: every request goes through a mock transport)
pytest

# Lint, format and type-check (all must be clean)
ruff check src tests
ruff format --check src tests
mypy

# Build wheel + sdist
python -m build
twine check dist/*
```

`tests/contract` loads the public OpenAPI document vendored at `tests/fixtures/voiceml-openapi.json` (test-only; it is not shipped in the package). `tests/integration/test_conformance.py` validates the models against callBroadcast's private response-fixture corpus and is skipped, with a visible reason, unless `VOICEML_CONFORMANCE_FIXTURES` points at that corpus. The code blocks in this README are executed by `tests/test_readme.py`.

## 📖 API Documentation

- **Reference docs:** [voicetel.com/docs/api/v0.9/voiceml/](https://voicetel.com/docs/api/v0.9/voiceml/)
- **Validator:** [voicetel.com/voiceml/validator/](https://voicetel.com/voiceml/validator/)
- **SDK catalogue:** [voicetel.com/docs/voiceml-sdks/](https://voicetel.com/docs/voiceml-sdks/)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **Type definitions:** the `voiceml.models` module — every wire shape has a Pydantic model.

## 🙌 Contributors

- [Michael Mavroudis](https://github.com/mavroudis) — Lead Developer

Contributions welcome. Open an issue describing the change you want to make, or send a pull request against `main`.

## 💖 Sponsors

| Sponsor | Contribution |
|---------|--------------|
| [VoiceTel Communications](https://voicetel.com) | Primary development and production hosting |

## 📄 License

MIT with the Commons Clause restriction. See [LICENSE](LICENSE) and [voicetel.com/legal/](https://voicetel.com/legal/).
