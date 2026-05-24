# voiceml

Official Python SDK for the [VoiceML](https://voicetel.com/docs/api/v0.6/voiceml/) REST API — VoiceTel's outbound voice + AMD service with a Twilio-compatible REST surface.

The wire format, auth model (HTTP Basic with `AccountSid` as username, per-tenant API key as password), error codes, and pagination envelope all match Twilio's documented Programmable Voice surface. If you've used the Twilio Python SDK, the patterns here will look familiar.

## Install

```bash
pip install voiceml
```

Requires Python 3.10+.

## Quickstart

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

Async:

```python
import asyncio
from voiceml import AsyncClient

async def main():
    async with AsyncClient(account_sid="AC…", api_key="…") as c:
        calls = await c.calls.list(status="in-progress")
        for call in calls.calls:
            print(call.sid, call.duration)

asyncio.run(main())
```

## Resources

| Group | Sync | Async | Covers |
| --- | --- | --- | --- |
| Calls | `client.calls` | `client.calls` | originate, fetch, terminate, update + per-call recordings, streams, siprec, transcriptions, notifications, events |
| Conferences | `client.conferences` | `client.conferences` | list/fetch/end conferences, participants (mute/hold/kick), conference-scoped recordings |
| Queues | `client.queues` | `client.queues` | create/list/update/delete queues, peek, dequeue (front or specific member) |
| Applications | `client.applications` | `client.applications` | CRUD on stored TwiML+callback bundles |
| Recordings | `client.recordings` | `client.recordings` | account-wide list, metadata fetch, audio fetch (follows S3 redirect), delete |
| Diagnostics | `client.diagnostics` | `client.diagnostics` | `/health` deep probe, OpenAPI spec |

## Errors

The transport raises subclasses of `voiceml.ApiError` keyed off HTTP status:

| Status | Exception |
| --- | --- |
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `PermissionDeniedError` |
| 404 | `NotFoundError` |
| 409 | `ConflictError` |
| 410 | `GoneError` |
| 429 | `RateLimitError` |
| 501 | `NotImplementedAPIError` |
| 5xx | `ServerError` |

Catch `ApiError` to handle any of them. The Twilio-compatible body (`code`, `message`, `more_info`, `status`) is parsed into `error.code` / `error.message` with the raw payload on `error.body`.

## Pagination

List operations return a `…List` model with a Twilio-compatible pagination envelope (`page`, `page_size`, `total`, `next_page_uri`, `previous_page_uri`, …). For `/Calls`, use the `iter()` helper to walk all pages:

```python
for call in c.calls.iter(status="completed", page_size=200):
    process(call)
```

For other resources, page manually with `client.<resource>.list(page=n)`.

## Twilio drop-in

The same `account_sid` / `api_key` pair the Twilio SDK validates in its constructor works here. The most direct migration path is:

```python
# Before
from twilio.rest import Client as TwilioClient
client = TwilioClient("AC…", "<token>", region=None)

# After — point at VoiceML
from voiceml import Client
client = Client(account_sid="AC…", api_key="<api-key>")
```

Method names follow the resource map above (`client.calls.create(...)` etc.) rather than Twilio's `client.calls.create(...)`/`client.api.v2010.accounts(sid).calls.create(...)` chain.

## Development

```bash
pip install -e ".[dev]"
pytest
mypy
ruff check .
```

## 📖 API Documentation

- **Reference docs:** [voicetel.com/docs/api/v0.6/voiceml/](https://voicetel.com/docs/api/v0.6/voiceml/)
- **Validator:** [voicetel.com/voiceml/validator/](https://voicetel.com/voiceml/validator/)
- **SDK catalogue:** [voicetel.com/docs/voiceml-sdks/](https://voicetel.com/docs/voiceml-sdks/)

## License

MIT with the Commons Clause restriction. See [LICENSE](LICENSE) and [voicetel.com/legal/](https://voicetel.com/legal/).
