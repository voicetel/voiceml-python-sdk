# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.9.x   | ✅        |
| < 0.9   | ❌        |

## Reporting a Vulnerability

Please **do not** open a public issue for security vulnerabilities.

Use GitHub's private vulnerability reporting for this repository:
**Security → Report a vulnerability** (or
<https://github.com/voicetel/voiceml-python-sdk/security/advisories/new>).

Include, where possible:

- A description of the issue and its impact
- Steps to reproduce or a proof of concept
- Affected version(s) and configuration

You can expect an acknowledgement within a few business days. Please
allow reasonable time for a fix before any public disclosure.

## Scope Notes

This SDK constructs authenticated HTTP requests to the VoiceML REST
API. Hardening expectations on the consumer side:

- Do not log `Client(api_key=...)` / `auth_token=...` or the
  `Authorization` header — both carry the per-tenant secret in HTTP
  Basic form. The SDK keeps the key out of `repr()` / `str()` of the
  client, transports, resources, errors and request models.
- Keep `account_sid` + secret out of source control; load from a
  secret manager or environment.
- The SDK uses httpx with its default TLS posture (TLS 1.2+ via
  OpenSSL) and never disables certificate verification. If you supply
  a custom `httpx.Client` / `httpx.AsyncClient`, you are responsible
  for matching that posture.
- Redirects on binary downloads (recording audio, exports) are followed
  by the SDK itself: the `Authorization` header is dropped as soon as the
  scheme or host changes, and an https→http downgrade is refused.
- Validate inbound webhooks with `voiceml.validate_request` /
  `voiceml.RequestValidator` (HMAC-SHA1 `X-Twilio-Signature`, compared in
  constant time) before acting on them.

### Retry policy

Retries (default `max_retries=2`) never replay a request the server may
already have acted on:

- `GET`, `HEAD`, `DELETE` and `PUT` are retried on 429 / 500 / 502 /
  503 / 504 and on connection or read failures.
- `POST` and `PATCH` (creating calls, sending messages, …) are retried
  only on 429 and when the connection was never established (DNS
  failure, connection refused, connect timeout, TLS handshake failure).
  They are never retried on 5xx, read timeouts or reset connections.
- `Retry-After` (seconds or HTTP-date) is honoured up to 60 seconds; a
  longer value raises immediately with `error.retry_after` set.

Out of scope: vulnerabilities in the published `voiceml` PyPI package
caused by a forked / vendored copy that has been modified.
