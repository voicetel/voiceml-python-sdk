# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.7.x   | ✅        |
| < 0.7   | ❌        |

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
  Basic form.
- Keep `account_sid` + secret out of source control; load from a
  secret manager or environment.
- The SDK uses httpx with its default TLS posture (TLS 1.2+ via
  OpenSSL). If you supply a custom `httpx.Client` / `httpx.AsyncClient`,
  you are responsible for matching that posture.
- Retries on 429 / 5xx replay the same request body. Do not pass
  non-idempotent payloads through clients with `max_retries > 0`
  unless the server enforces an idempotency key.

Out of scope: vulnerabilities in the published `voiceml` PyPI package
caused by a forked / vendored copy that has been modified.
