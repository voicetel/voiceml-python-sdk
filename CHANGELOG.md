# Changelog

All notable changes to the VoiceML Python SDK are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.9.3] - 2026-10-18

### Breaking changes

- **Removed the six methods for endpoints the API no longer serves** (the server answers
  `405` / code `20004`), sync and async:
  - `calls.list_streams` — `GET /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}/Streams.json`
  - `calls.get_stream` — `GET /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}/Streams/{Sid}.json`
  - `calls.list_siprec` — `GET /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}/Siprec.json`
  - `calls.get_siprec` — `GET /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}/Siprec/{Sid}.json`
  - `calls.list_transcriptions` — `GET /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}/Transcriptions.json`
  - `calls.get_transcription` — `GET /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}/Transcriptions/{Sid}.json`

  The list models `StreamList`, `SiprecList` and `TranscriptionList` are removed. Starting
  and stopping streams, SIPREC sessions and transcriptions (`start_*` / `stop_*`, the
  `POST` operations) is unchanged.
- **`iter()` returns a lazy iterator instead of a list** and follows the server's
  `next_page_uri` (with its `PageToken`) instead of incrementing `Page`. Wrap it in
  `list(...)` if you need a list. Affects `calls`, `conferences`, `messages`, `queues`,
  `recordings` and `sip.domains`.
- **List envelopes no longer have `total` or `num_pages`** (the server stopped sending
  them); `page` / `page_size` are now optional and `start`, `end`, `first_page_uri`,
  `previous_page_uri` and `next_page_uri` are typed on every `/2010-04-01` list.
- `calls.list` / `calls.iter` (`GET /2010-04-01/Accounts/{AccountSid}/Calls.json`): removed
  the non-spec `start_time_gte` / `start_time_lte` filters (`StartTime>=` / `StartTime<=`).
  Use `start_time_gt` / `start_time_lt` / `start_time`.
- `incoming_phone_numbers.create` / `.update`
  (`POST /2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers.json`,
  `POST /2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers/{Sid}.json`): removed
  `friendly_name`, which the API does not let you set.
- `incoming_phone_numbers.create_local` / `create_mobile` / `create_toll_free`
  (`POST /2010-04-01/Accounts/{AccountSid}/IncomingPhoneNumbers/{Local,Mobile,TollFree}.json`):
  these accept only `phone_number`, `voice_url` and `voice_method`; `voice_fallback_url`,
  `voice_fallback_method` and `friendly_name` are removed (they now use the new
  `CreateTypedIncomingPhoneNumberRequest`).
- `calls.send_user_defined_message(call_sid)`
  (`POST /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}/UserDefinedMessages.json`): the
  `payload` argument is removed; the operation declares no body parameters (and the
  server answers `501`).
- `conferences.update_recording`
  (`POST /2010-04-01/Accounts/{AccountSid}/Conferences/{ConferenceSid}/Recordings/{Sid}.json`)
  sends only `Status`; it now takes `UpdateConferenceRecordingRequest` (an
  `UpdateRecordingRequest` is still accepted, but its `pause_behavior` is not sent).
- `PaymentCapture` (`calls.update_payment`,
  `POST /2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}/Payments/{Sid}.json`) accepts
  only the six values the spec defines; the `*-matcher` values are removed.
- The spec now types the list-valued form parameters as arrays, and the request models
  follow it — the field is a list and each value is sent as a repeated key (a single
  space- or comma-separated string is no longer the SDK's spelling):
  - `CreateCallRequest.recording_status_callback_event` /
    `StartRecordingRequest.recording_status_callback_event` /
    `StartConferenceRecordingRequest.recording_status_callback_event`:
    `str` → `list[RecordingStatusCallbackEvent]` (`in-progress`, `completed`, `absent`)
  - `CreateParticipantRequest.status_callback_event`,
    `CreateApplicationRequest.status_callback_event` /
    `UpdateApplicationRequest.status_callback_event`:
    `str` → `list[CallStatusCallbackEvent]` (`initiated`, `ringing`, `answered`,
    `completed`)
- **Request models reject unknown fields** (`extra="forbid"`): a misspelled argument
  raises `pydantic.ValidationError` instead of being sent as a wire parameter.
- **Enum-typed request fields are constrained to the spec values** (`Literal`), e.g.
  `voice_method="get"` now raises. This restores the `Literal["GET", "POST"]` typing on
  the IncomingPhoneNumbers request models and resource arguments and extends it to every
  enum in the spec.
- **Response models are tolerant readers**: every field the spec marks nullable is now
  `X | None` (for example `Call.sid`, `Call.account_sid`, `Call.direction`,
  `Call.date_created`, `Participant.muted`), and enum-typed response fields accept unknown
  values as plain strings. Type checkers will ask you to handle `None`.
- `calls.get_notification` and `notifications.get` return a typed `Notification` instead
  of a `dict`; `NotificationsList.notifications` and `EventsList.events` are typed
  (`Notification`, `CallEvent`).
- `ApiError.code` is an `int` (numeric strings are converted); network failures raise
  `APIConnectionError` / `APITimeoutError` (subclasses of `ApiError`, `status_code == 0`)
  instead of a bare `ApiError`; a 2xx response that is not JSON raises an `ApiError`
  whose message says "could not decode".
- `POST` / `PATCH` requests are no longer retried on 5xx responses or read timeouts — see
  *Fixed*.
- Requests always go to the configured `base_url` (or product host); the `base_url` of an
  injected `http_client` is no longer used.
- Minimum `pydantic` raised from 2.6 to **2.8**: pydantic 2.6 and 2.7 cannot be installed
  on Python 3.13 (no `pydantic-core` wheels), so they could not be tested. 2.8.0 and
  `httpx` 0.27.0 (the unchanged `httpx` floor) are now tested in CI on Python 3.10.

### Fixed

- **Duplicate calls / messages**: `POST` and `PATCH` are retried only on `429` and on
  connection-establishment failures (DNS, connection refused, connect timeout, TLS
  handshake, pool timeout). `GET` / `HEAD` / `DELETE` / `PUT` are retried on
  429/500/502/503/504 and on connect / read failures.
- **Pagination never terminated or failed on page 2**: iterators and the new helpers
  follow `next_page_uri` verbatim and stop when it is null, empty or absent.
- `Retry-After` is parsed as delta-seconds **or** an HTTP-date; values above 60 seconds
  raise immediately (no hour-long sleep) with `error.retry_after` set; backoff uses full
  jitter (0.5 s base, 8 s cap). Discarded responses are closed before retrying.
- `calls.update_recording(call_sid, "Twilio.CURRENT", …)` now sends
  `…/Recordings/Twilio.CURRENT.json`; the `.json` suffix comes from the route instead of
  "does the last segment contain a dot".
- Every caller-supplied path segment is percent-encoded (RFC 3986 unreserved set kept):
  `../` can no longer traverse, `?` / `#` can no longer inject a query or truncate the
  path, and E.164 numbers (`+` → `%2B`) are encoded exactly once.
- `http_client=` no longer splits traffic across hosts or ignores `base_url`.
- `client.diagnostics` goes through the normal transport (injected client, timeout,
  proxy, User-Agent), sends no `Authorization` header, and maps a `503` from `/health` to
  `ServerError` instead of leaking `httpx.HTTPStatusError`.
- `RecordingAudio.via_redirect` reports whether the server redirected to archived audio.
- `HealthStatus.warnings` / `failures` are optional and default to empty lists.
- `ApiError.message` exists (the README promised it).
- SIP domain, credential-list, IP-ACL and IP-address lists accept the spec's
  `FriendlyName` filter; `conferences.list_recordings` accepts the `DateCreated` filters;
  `assistants_v1.assistants.list` accepts `page` / `page_token`.
- Pricing `countries.fetch` encodes the country code and is typed with the product's
  model instead of `object`.
- JSON request bodies are serialised compactly and identically regardless of the `httpx`
  version.
- The 22 lint errors and import-order issues introduced by the September type-safety
  sweep are fixed; the sweep's removal of every `# type: ignore` is kept, and `ruff`,
  `ruff format` and `mypy --strict` are clean.

### Added

- The 4 operations documented by the final spec revision (sync and async):
  - `client.monitor_v1.alerts.list / iter / fetch` — `GET /v1/Alerts`,
    `GET /v1/Alerts/{Sid}` (failure events: call-scoped errors and messaging
    delivery failures; `LogLevel` / `StartDate` / `EndDate` / `PageSize` filters,
    `meta` envelope, single page today)
  - `client.messages.create_feedback(message_sid, outcome=…)` —
    `POST /2010-04-01/Accounts/{AccountSid}/Messages/{Sid}/Feedback.json`
    (`Outcome`: `confirmed` / `unconfirmed`)
  - `client.accounts.rotate_key()` —
    `POST /2010-04-01/Accounts/{AccountSid}/RotateKey.json`; returns
    `AccountWithKey` with the freshly generated `api_key` (excluded from `repr()`;
    the previous key stops working immediately)
- The 36 operations that had no SDK method (sync and async):
  - `client.accounts.fetch()` / `.update(...)` — `GET` / `POST /2010-04-01/Accounts/{Sid}.json`
    (a concurrent modification raises `ConflictError`, code 20409)
  - `client.balance.fetch()` — `GET …/Balance.json`
  - `client.outgoing_caller_ids.list / iter / create / get / update / delete` —
    `…/OutgoingCallerIds.json`, `…/OutgoingCallerIds/{Sid}.json`
  - `client.messages.list_media / get_media / delete_media` —
    `…/Messages/{MessageSid}/Media.json`, `…/Media/{Sid}.json`
  - `client.exports.list()` / `.download(date)` — `…/Exports.json`, `…/Exports/{Date}`
  - `client.transcriptions.list / iter / get / delete` — `…/Transcriptions.json`,
    `…/Transcriptions/{Sid}.json`
  - `client.recordings.list_transcriptions / get_transcription / delete_transcription` —
    `…/Recordings/{RecordingSid}/Transcriptions.json`, `…/Transcriptions/{Sid}.json`
  - `client.conferences.start_recording` — `POST …/Conferences/{ConferenceSid}/Recordings.json`
  - `client.diagnostics.openapi_yaml()` / `.openapi_yml()` — `GET /openapi.yaml`, `/openapi.yml`
  - `client.usage_records.list / iter / list_all_time / list_daily / list_last_month /
    list_monthly / list_this_month / list_today / list_yearly / list_yesterday` —
    `…/Usage/Records.json` and `…/Usage/Records/{AllTime,Daily,LastMonth,Monthly,ThisMonth,Today,Yearly,Yesterday}.json`
  - `client.sip.registrations.list / iter` — `GET …/SIP/Registrations.json`
  - `client.messaging_v1.services.phone_numbers(service_sid).list / create / fetch / delete` —
    `/v1/Services/{ChatServiceSid}/PhoneNumbers[/{Sid}]` on the messaging host
- `messages.create`: `media_url` (MMS, repeated `MediaUrl` keys), `validity_period` and
  `status_callback_method`; `body` is optional, with a client-side check that `body` or
  `media_url` is present.
- IncomingPhoneNumbers create/update: `sms_url`, `sms_method`, `sms_fallback_url`,
  `sms_fallback_method` and `sms_application_sid` (`AP…`); list filters `friendly_name`,
  `beta`, `origin` on all four list operations.
- Applications: `message_status_callback`, `sms_status_callback`. Call recordings:
  `recording_track` on start, `pause_behavior` on update.
- Response fields: IncomingPhoneNumber `subresource_uris`; Application `sms_*`,
  `message_status_callback`, `sms_status_callback`; Recording `track`; MessagingService
  `advanced_opt_out`; typed `Notification` and `CallEvent` models.
- Webhook signature validation: `voiceml.validate_request`, `voiceml.RequestValidator`
  and `voiceml.webhooks.compute_signature`.
- Pagination helpers: `client.next_page(page)`, `client.paginate(page)` (lazy, every list
  type), `Resource.next_page(page)`, and async `iter()` / `paginate()` on `AsyncClient`.
  `/v1` `meta.next_page_url` is followed only on the configured product host
  (`PaginationError` otherwise).
- Diagnostics-only client: `Client()` / `AsyncClient()` without credentials.
- `APIConnectionError`, `APITimeoutError`, `MethodNotAllowedError` (405),
  `PaginationError`; `ApiError.retry_after`.
- `datetime` / `date` values for date filters are serialised as ISO-8601 UTC /
  `YYYY-MM-DD`; dict values for JSON-typed form fields as compact JSON.
- A spec-driven contract test (`tests/contract`) that calls every public method and
  checks it against the vendored OpenAPI document, including 333/333 operation coverage,
  and a tolerant-decoding test over synthesized null / minimal / unknown-enum /
  extra-field payloads. The vendored fixture is the final spec (333 operations;
  `SmsApplicationSid` restored, list-valued form parameters typed as arrays,
  OpenAPI 3.1 null typing).

### Security

- `POST` requests that may already have been processed are never replayed (no duplicate
  calls or SMS from SDK retries).
- Binary downloads (recording audio, exports) follow redirects manually: `Authorization`
  is dropped when the scheme or host changes and https→http downgrades are refused.
- Path segments are percent-encoded, so untrusted identifiers cannot retarget
  authenticated requests.
- Pagination never sends credentials to a host other than the configured product host.
- Secret fields of `UpdateAccountRequest` (`aws_secret_access_key`, `stt_http_token`,
  `tts_http_token`) are excluded from `repr()`; the freshly rotated key on
  `AccountWithKey.api_key` is excluded the same way; the client, transports, resources
  and errors never include the API key in their string output.
- The test suite blocks all network access.

### Docs

- README rewritten: correct operation count (333 of 333), working examples (executed by
  the test suite), the retry / `Retry-After` policy, pagination without `total`,
  webhook validation, diagnostics without credentials, and accurate authentication
  wording — VoiceML uses your AccountSid and a VoiceML API key in the HTTP Basic
  positions Twilio SDKs use; Twilio-issued credentials do not work.
- SECURITY.md: supported versions are `0.9.x`; documents the retry and redirect policy.
- Package metadata: the licence is declared as `LicenseRef-MIT-Commons-Clause` with the
  `LICENSE` file (PEP 639) instead of plain MIT / an OSI classifier; the homepage points
  at the documentation.
- Example phone numbers use the fictional `+1 415 555 01xx` range.

### Packaging and CI

- CI runs `ruff check`, `ruff format --check` and `mypy --strict`, the test suite on
  Python 3.10–3.13, the test suite against the minimum `httpx` / `pydantic`, and builds
  the distributions with `twine check --strict`, a check that test fixtures are not
  shipped, and a clean-environment import smoke test.
- Publishing runs the full CI workflow first and refuses to publish unless the tag
  matches the package version.
