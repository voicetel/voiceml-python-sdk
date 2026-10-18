"""Recording audio and export downloads: authenticated GET, manual redirect handling."""

from __future__ import annotations

import httpx
import pytest

from voiceml import ApiError, AsyncClient, Client, GoneError

ACCOUNT_SID = "AC" + "e" * 32
API_KEY = "binary-test-key"
API = "https://voiceml.voicetel.com"
AUDIO_PATH = f"/2010-04-01/Accounts/{ACCOUNT_SID}/Recordings/RE1.wav"
S3 = "https://bucket.s3.amazonaws.com/rec/RE1.wav?X-Amz-Signature=abc"


class Server:
    def __init__(self, routes: dict[str, httpx.Response]) -> None:
        self.routes = routes
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.routes[str(request.url)]

    def client(self) -> Client:
        return Client(
            account_sid=ACCOUNT_SID,
            api_key=API_KEY,
            http_client=httpx.Client(transport=httpx.MockTransport(self), follow_redirects=True),
        )


def test_audio_is_fetched_with_auth_and_audio_accept_header() -> None:
    server = Server(
        {
            API + AUDIO_PATH: httpx.Response(
                200, content=b"RIFF", headers={"content-type": "audio/wav"}
            )
        }
    )
    with server.client() as c:
        audio = c.recordings.get_audio("RE1")
    assert audio.content == b"RIFF"
    assert audio.content_type == "audio/wav"
    assert audio.via_redirect is False
    sent = server.requests[0]
    assert sent.headers["authorization"].startswith("Basic ")
    assert sent.headers["accept"] == "audio/*, */*"


def test_cross_host_redirect_drops_authorization() -> None:
    server = Server(
        {
            API + AUDIO_PATH: httpx.Response(302, headers={"location": S3}),
            S3: httpx.Response(200, content=b"WAVE", headers={"content-type": "audio/x-wav"}),
        }
    )
    with server.client() as c:
        audio = c.recordings.get_audio("RE1")
    assert audio.content == b"WAVE"
    assert audio.via_redirect is True
    first, second = server.requests
    assert "authorization" in first.headers
    assert "authorization" not in second.headers
    assert str(second.url) == S3


def test_same_origin_redirect_keeps_authorization() -> None:
    moved = f"{API}/2010-04-01/Accounts/{ACCOUNT_SID}/Recordings/RE1-archived.wav"
    server = Server(
        {
            API + AUDIO_PATH: httpx.Response(307, headers={"location": moved}),
            moved: httpx.Response(200, content=b"WAVE"),
        }
    )
    with server.client() as c:
        c.recordings.get_audio("RE1")
    assert all("authorization" in r.headers for r in server.requests)


def test_https_to_http_downgrade_is_refused() -> None:
    server = Server(
        {API + AUDIO_PATH: httpx.Response(302, headers={"location": "http://bucket.example.com/x"})}
    )
    with server.client() as c, pytest.raises(ApiError, match="https to http"):
        c.recordings.get_audio("RE1")
    assert len(server.requests) == 1


def test_redirect_loops_are_bounded() -> None:
    server = Server({API + AUDIO_PATH: httpx.Response(302, headers={"location": API + AUDIO_PATH})})
    with server.client() as c, pytest.raises(ApiError, match="too many redirects"):
        c.recordings.get_audio("RE1")
    assert len(server.requests) == 6


def test_gone_audio_raises_gone_error() -> None:
    server = Server(
        {API + AUDIO_PATH: httpx.Response(410, json={"code": 20410, "message": "gone"})}
    )
    with server.client() as c, pytest.raises(GoneError):
        c.recordings.get_audio("RE1")


def test_export_download_follows_presigned_redirect_without_credentials() -> None:
    export = f"{API}/2010-04-01/Accounts/{ACCOUNT_SID}/Exports/2026-07-01"
    presigned = "https://exports.s3.amazonaws.com/2026-07-01.gz?sig=1"
    server = Server(
        {
            export: httpx.Response(302, headers={"location": presigned}),
            presigned: httpx.Response(
                200, content=b"\x1f\x8b", headers={"content-type": "application/gzip"}
            ),
        }
    )
    with server.client() as c:
        archive = c.exports.download("2026-07-01")
    assert archive.content == b"\x1f\x8b"
    assert archive.content_type == "application/gzip"
    assert server.requests[0].url.raw_path.endswith(b"/Exports/2026-07-01")
    assert "authorization" in server.requests[0].headers
    assert "authorization" not in server.requests[1].headers
    assert "bytes=2" in repr(archive)


async def test_async_audio_redirect_drops_authorization() -> None:
    server = Server(
        {
            API + AUDIO_PATH: httpx.Response(302, headers={"location": S3}),
            S3: httpx.Response(200, content=b"WAVE"),
        }
    )
    async with AsyncClient(
        account_sid=ACCOUNT_SID,
        api_key=API_KEY,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(server)),
    ) as c:
        audio = await c.recordings.get_audio("RE1")
    assert audio.via_redirect is True
    assert "authorization" not in server.requests[1].headers
