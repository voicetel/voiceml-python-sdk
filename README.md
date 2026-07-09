# 📞 VoiceML Python SDK

The official Python client for the [VoiceML REST API](https://voicetel.com/docs/api/v0.9/voiceml/) — Twilio-compatible outbound voice and answering-machine-detection from VoiceTel, with type-safe, async-ready Python.

![Version](https://img.shields.io/badge/version-0.9.2-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT%20%2B%20Commons%20Clause-green)
![Tests](https://img.shields.io/badge/tests-176%20unit-brightgreen)
![Typed](https://img.shields.io/badge/typed-pydantic--v2-blue)

## 📚 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quickstart](#-quickstart)
- [Authentication](#-authentication)
- [Resource Reference](#-resource-reference)
- [Error Handling](#-error-handling)
- [Async Support](#-async-support)
- [Pagination](#-pagination)
- [Migration from twilio-python](#-migration-from-twilio-python)
- [Rate Limits](#-rate-limits)
- [Development](#-development)
- [API Documentation](#-api-documentation)
- [Contributors](#-contributors)
- [Sponsors](#-sponsors)
- [License](#-license)

## ✨ Features

### 🛡️ Strongly Typed End-to-End
- **Pydantic v2 models** for every one of the 81 API operations — request bodies validated before they leave your machine, responses validated when they arrive.
- **Autocomplete everywhere.** Your IDE knows the shape of every field — `Call.sid`, `Recording.duration`, `Queue.current_size` are all typed.
- **Twilio-compatible wire shapes** — `account_sid`, `from_number`, `to_number`, status callbacks, pagination envelopes — match what Twilio's Programmable Voice API documents.

### ⚡ Sync + Async, Same Surface
- `Client` for blocking calls, `AsyncClient` for `await`-based async — identical method names, identical return types.
- Built on `httpx` — HTTP/2 ready, connection pooling, custom transports if you need them.
- TLS session cache + persistent connections out of the box.

### 🔁 Production-Grade Transport
- **Automatic retry** with exponential backoff on 429 / 5xx — honors `Retry-After` headers.
- **Configurable timeouts** per client or per call.
- **HTTP Basic auth** with `AccountSid:ApiKey` — exactly what the Twilio SDK uses, so existing credentials work unchanged.
- **Structured exception hierarchy** — `RateLimitError`, `AuthenticationError`, `NotFoundError`, etc. all subclasses of `ApiError` you can catch broadly or narrowly.

### 📞 Complete API Coverage
- **Calls** — originate, fetch, terminate, update + per-call recordings, streams, siprec, transcriptions, notifications, events, and the `/Calls/{sid}/Payments` lifecycle (Pay TwiML companion).
- **Conferences** — list, fetch, end conferences, plus participants (mute / hold / kick) and conference-scoped recordings.
- **Queues** — create, list, update, delete, peek, dequeue (front or specific member).
- **Applications** — CRUD on stored TwiML + callback bundles.
- **Recordings** — account-wide list, metadata fetch, audio fetch (follows S3 redirect), delete.
- **Messages** — create, fetch, list (To/From/DateSent filters + pagination), update (Body redaction; Status=canceled), delete.
- **IncomingPhoneNumbers** — list, fetch, update.
- **Notifications** — fetch, list.
- **SIP** — SIP Trunking: Domains (CRUD), CredentialLists + Credentials (CRUD), IpAccessControlLists + IpAddresses (CRUD), Domain↔ACL/CredentialList mappings (historical, Auth/Calls, Auth/Registrations namespaces).
- **Routes V2** — Twilio Inbound Processing Region API: `client.routes_v2.sip_domains.fetch(name)` / `update(name, voice_region=..., friendly_name=...)`.
- **Diagnostics** — `/health` deep probe, OpenAPI spec.

### 🧪 Tested
- **176 unit tests** with mocked HTTP layer (`pytest-httpx`) and real Pydantic validation on every fixture — spec drift gets caught at parse time.
- **Integration test suite** that runs against a callBroadcast / VoiceML instance — gated by env vars, safe for CI.

### 📦 Clean Distribution
- Zero codegen footprint — every byte hand-written.
- Built with `hatchling`; ships as wheel + sdist.
- `py.typed` marker — downstream type checkers see your imports natively.

## 🚀 Installation

```bash
pip install voiceml
```

Requires Python 3.10 or later. Tested against 3.10, 3.11, 3.12, and 3.13.

## 🏁 Quickstart

```python
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

    for q in c.queues.list().queues:
        print(q.friendly_name, q.current_size)
```

## 🔑 Authentication

Every endpoint uses **HTTP Basic** with your `AccountSid` as the username and your per-tenant API key as the password — identical to Twilio's auth shape, so credentials issued for Twilio code work here unchanged.

```python
from voiceml import Client

with Client(account_sid="AC…", api_key="…") as c:
    me = c.diagnostics.health()  # uses your AccountSid + key on every call
```

> Don't have credentials yet? See **[voicetel.com/docs/api/v0.9/voiceml/](https://voicetel.com/docs/api/v0.9/voiceml/)** for issuance and rotation.

## 🗺️ Resource Reference

| Resource | Sync + Async | Covers |
|---|---|---|
| `client.calls` | originate, fetch, list, terminate, update | + per-call recordings, streams, siprec, transcriptions, notifications, events, payments |
| `client.conferences` | list, fetch, end | participants (mute / hold / kick), conference-scoped recordings |
| `client.queues` | create, list, update, delete | peek, dequeue (front or specific member) |
| `client.applications` | CRUD on TwiML + callback bundles | |
| `client.recordings` | account-wide list, metadata, audio fetch, delete | follows S3 redirect for audio |
| `client.messages` | create, fetch, list, update, delete | To/From/DateSent filters; Body redaction; Status=canceled |
| `client.incoming_phone_numbers` | list, fetch, update | |
| `client.notifications` | fetch, list | |
| `client.conversations_v1` | conversations, messages, participants, roles, users, credentials, configuration, services | rides `conversations.voicetel.com` |
| `client.messaging_v1.services` | create, list, fetch, update, delete | Messaging Service (`MG…`); rides `messaging.voicetel.com` |
| `client.voice_v1` | byoc_trunks, connection_policies (+ targets), settings, source_ip_mappings, ip_records | |
| `client.routes_v2` | phone_numbers, sip_domains | Inbound Processing Region |
| `client.pricing` | `v1.{voice,messaging,phone_numbers}`, `v2.{voice,trunking}` | read-only rate lookups |
| `client.diagnostics` | `/health`, OpenAPI spec | |

Every method that takes a request body accepts a typed Pydantic model imported from `voiceml.models`:

```python
from voiceml import Client
from voiceml.models import CreateCallRequest, StartPaymentRequest

with Client(account_sid="AC…", api_key="…") as c:
    call = c.calls.create(CreateCallRequest(
        To="+18005551234",
        From="+18005550000",
        Url="https://example.com/twiml",
    ))
    # On a live call, open a Pay session:
    session = c.calls.start_payment(call.sid, StartPaymentRequest(
        IdempotencyKey="order-482917",
        StatusCallback="https://example.com/pay-status",
    ))
    print(session.sid, session.status)
```

### Product hosts

VoiceML mirrors Twilio's product-per-subdomain model: the Conversations product
answers on `conversations.voicetel.com` and Messaging Service on
`messaging.voicetel.com`, while everything else stays on the default
`voiceml.voicetel.com`. The two share the `/v1/Services` path shape, so the host
is what disambiguates them. The client derives these automatically from
`base_url` — you don't set anything for the hosted service.

For a self-hosted deployment on a custom host, point the product base URLs at
your own subdomains explicitly (otherwise every product stays on the single host
you configured):

```python
Client(
    account_sid="AC…",
    api_key="…",
    base_url="https://pbx.example.com",
    messaging_base_url="https://messaging.example.com",
    conversations_base_url="https://conversations.example.com",
)
```

## 🚨 Error Handling

All HTTP errors raise subclasses of `voiceml.ApiError`. Catch broadly or narrowly:

| Status | Exception |
|--------|-----------|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `PermissionDeniedError` |
| 404 | `NotFoundError` |
| 409 | `ConflictError` |
| 410 | `GoneError` |
| 429 | `RateLimitError` |
| 501 | `NotImplementedAPIError` |
| 5xx | `ServerError` |
| other | `ApiError` |

```python
from voiceml import Client, NotFoundError, RateLimitError

with Client(account_sid="AC…", api_key="…") as c:
    try:
        call = c.calls.get("CA0000000000000000000000000000aaaa")
    except NotFoundError:
        print("That call isn't on your account.")
    except RateLimitError as e:
        print(f"Slow down — retry in {e.body.get('retry_after', '?')}s")
```

The Twilio-compatible error body (`code`, `message`, `more_info`, `status`) is parsed into `error.code` / `error.message` with the raw payload on `error.body`.

## ⚡ Async Support

Identical surface to `Client`, with `await`-based methods:

```python
import asyncio
from voiceml import AsyncClient

async def main() -> None:
    async with AsyncClient(account_sid="AC…", api_key="…") as c:
        calls = await c.calls.list(status="in-progress")
        for call in calls.calls:
            print(call.sid, call.duration)

asyncio.run(main())
```

## 📄 Pagination

List operations return a `…List` model with a Twilio-compatible pagination envelope (`page`, `page_size`, `total`, `next_page_uri`, `previous_page_uri`, …). For `/Calls` and `/Messages`, use the `iter()` helper to walk all pages transparently:

```python
for call in c.calls.iter(status="completed", page_size=200):
    process(call)

for msg in c.messages.iter(from_number="+18005550000", page_size=200):
    archive(msg)
```

For other resources, page manually with `client.<resource>.list(page=n)`.

## 🔁 Migration from twilio-python

The `account_sid` + `api_key` pair Twilio's SDK validates in its constructor works unchanged here:

```python
# Before — Twilio
from twilio.rest import Client as TwilioClient
client = TwilioClient("AC…", "<token>", region=None)

# After — VoiceML (Twilio-compatible)
from voiceml import Client
client = Client(account_sid="AC…", api_key="<api-key>")
```

Method names follow the resource map above (`client.calls.create(...)`, `client.queues.list()`, …) rather than Twilio's `client.api.v2010.accounts(sid).calls.create(...)` chain — flatter, fewer keystrokes, same wire format on the way out.

## ⏱️ Rate Limits

VoiceML applies per-tenant rate limits at the edge. The SDK automatically retries 429 responses with `Retry-After` honored, up to `max_retries` (default `2`). To bump it:

```python
Client(account_sid="AC…", api_key="…", max_retries=4, timeout=60.0)
```

## 🛠️ Development

```bash
git clone https://github.com/voicetel/voiceml-python-sdk
cd voiceml-python-sdk
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Unit tests (fast, no network)
pytest tests/unit

# Lint + type-check
ruff check src tests
mypy src

# Integration tests (live, read-only against a configured VoiceML instance)
cp .env.example .env  # fill in VOICEML_ACCOUNT_SID / VOICEML_API_KEY / VOICEML_BASE_URL
pytest tests/integration

# Build wheel + sdist
python -m build
twine check dist/*
```

## 📖 API Documentation

- **Reference docs:** [voicetel.com/docs/api/v0.9/voiceml/](https://voicetel.com/docs/api/v0.9/voiceml/)
- **Validator:** [voicetel.com/voiceml/validator/](https://voicetel.com/voiceml/validator/)
- **SDK catalogue:** [voicetel.com/docs/voiceml-sdks/](https://voicetel.com/docs/voiceml-sdks/)
- **Type definitions:** see the `voiceml.models` module — every wire shape has a Pydantic model.

## 🙌 Contributors

- [Michael Mavroudis](https://github.com/mavroudis) — Lead Developer

Contributions welcome. Open an issue describing the change you want to make, or send a pull request against `main`.

## 💖 Sponsors

| Sponsor | Contribution |
|---------|--------------|
| [VoiceTel Communications](https://voicetel.com) | Primary development and production hosting |

## 📄 License

MIT with the Commons Clause restriction. See [LICENSE](LICENSE) and [voicetel.com/legal/](https://voicetel.com/legal/).
