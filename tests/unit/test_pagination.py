"""Pagination follows the server's next-page links verbatim and is lazy."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
import pytest

from voiceml import AsyncClient, Client, PaginationError
from voiceml.models import CallList, ConversationsV1RoleList, MessagingServiceList

from ..contract import _harness as H

ACCOUNT_SID = "AC" + "b" * 32
API_KEY = "pagination-test-key"
ROOT = f"/2010-04-01/Accounts/{ACCOUNT_SID}"


def page(
    key: str, items: list[dict[str, Any]], next_uri: str | None, **extra: Any
) -> dict[str, Any]:
    return {key: items, "page": 0, "page_size": len(items), "next_page_uri": next_uri, **extra}


class Server:
    """Serves queued JSON bodies and records every request."""

    def __init__(self, *bodies: dict[str, Any]) -> None:
        self.bodies = list(bodies)
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return httpx.Response(200, json=self.bodies.pop(0))

    def client(self, **kwargs: Any) -> Client:
        return Client(
            account_sid=ACCOUNT_SID,
            api_key=API_KEY,
            http_client=httpx.Client(transport=httpx.MockTransport(self)),
            **kwargs,
        )

    def aclient(self) -> AsyncClient:
        return AsyncClient(
            account_sid=ACCOUNT_SID,
            api_key=API_KEY,
            http_client=httpx.AsyncClient(transport=httpx.MockTransport(self)),
        )


def item(schema: str) -> dict[str, Any]:
    """The smallest spec-valid representation of a resource (required fields only)."""
    data: dict[str, Any] = H.synth(H.load_spec()["components"]["schemas"][schema], "minimal")
    return data


def call(n: int) -> dict[str, Any]:
    return {**item("Call"), "sid": f"CA{n:032d}"}


NEXT = f"{ROOT}/Calls.json?PageSize=2&Page=1&PageToken=PAabc%2B123"


def test_iter_follows_next_page_uri_verbatim_and_terminates() -> None:
    server = Server(
        page("calls", [call(1), call(2)], NEXT),
        page("calls", [call(3)], None),
    )
    with server.client() as c:
        sids = [x.sid for x in c.calls.iter(status="completed", page_size=2)]
    assert sids == [call(1)["sid"], call(2)["sid"], call(3)["sid"]]
    assert [str(r.url) for r in server.requests] == [
        f"https://voiceml.voicetel.com{ROOT}/Calls.json?Status=completed&PageSize=2",
        f"https://voiceml.voicetel.com{NEXT}",
    ]
    # The PageToken is sent byte-for-byte as the server issued it.
    assert server.requests[1].url.raw_path.endswith(b"PageToken=PAabc%2B123")


@pytest.mark.parametrize("terminal", [None, "", "absent"])
def test_iter_stops_on_null_empty_or_absent_link(terminal: str | None) -> None:
    last = page("calls", [call(3)], None)
    if terminal == "absent":
        del last["next_page_uri"]
    else:
        last["next_page_uri"] = terminal
    server = Server(page("calls", [call(1)], NEXT), last)
    with server.client() as c:
        assert len(list(c.calls.iter())) == 2
    assert len(server.requests) == 2


def test_iter_does_not_stop_on_an_empty_page_with_a_link() -> None:
    server = Server(page("calls", [], NEXT), page("calls", [call(1)], None))
    with server.client() as c:
        assert len(list(c.calls.iter())) == 1
    assert len(server.requests) == 2


def test_iter_is_lazy_and_stops_requesting_when_the_consumer_stops() -> None:
    # A server that always links onward (as Calls does from a full page).
    server = Server(*[page("calls", [call(i), call(i + 1)], NEXT) for i in range(0, 20, 2)])
    with server.client() as c:
        iterator = c.calls.iter(page_size=2)
        assert server.requests == []  # nothing sent until consumed
        taken = [next(iterator) for _ in range(3)]
    assert len(taken) == 3
    assert len(server.requests) == 2


def test_next_page_resolves_relative_links_against_the_configured_host() -> None:
    server = Server(page("calls", [call(2)], None))
    with server.client(base_url="https://staging.example.com:8443") as c:
        first = CallList.model_validate(page("calls", [call(1)], NEXT))
        second = c.next_page(first)
        assert second is not None
        assert c.next_page(second) is None
    assert str(server.requests[0].url) == f"https://staging.example.com:8443{NEXT}"


def test_client_paginate_works_for_any_list() -> None:
    server = Server(
        page("queues", [{**item("Queue"), "sid": "QU1"}], f"{ROOT}/Queues.json?PageToken=x"),
        page("queues", [{**item("Queue"), "sid": "QU2"}], None),
    )
    with server.client() as c:
        sids = [q.sid for q in c.paginate(c.queues.list())]
    assert sids == ["QU1", "QU2"]


def test_v1_next_page_url_on_the_product_host_is_followed() -> None:
    server = Server(
        {
            "roles": [{"sid": "RL2"}],
            "meta": {"next_page_url": None},
        }
    )
    with server.client() as c:
        first = ConversationsV1RoleList.model_validate(
            {
                "roles": [{"sid": "RL1"}],
                "meta": {"next_page_url": "https://conversations.voicetel.com/v1/Roles?Page=1"},
            }
        )
        assert [r.sid for r in c.paginate(first)] == ["RL1", "RL2"]
    assert str(server.requests[0].url) == "https://conversations.voicetel.com/v1/Roles?Page=1"


@pytest.mark.parametrize(
    "link",
    [
        "https://evil.example.com/v1/Services?Page=1",
        "http://messaging.voicetel.com/v1/Services?Page=1",
        "https://voiceml.voicetel.com/v1/Services?Page=1",
    ],
)
def test_v1_next_page_url_on_another_origin_is_refused(link: str) -> None:
    server = Server()
    with server.client() as c:
        first = MessagingServiceList.model_validate(
            {"services": [{"sid": "MG1"}], "meta": {"next_page_url": link}}
        )
        with pytest.raises(PaginationError):
            c.next_page(first)
        with pytest.raises(PaginationError):
            list(c.paginate(first))
    assert server.requests == []


def test_list_envelopes_have_no_total_or_num_pages() -> None:
    parsed = CallList.model_validate(
        {
            "calls": [],
            "page": 0,
            "page_size": 50,
            "start": 0,
            "end": 0,
            "first_page_uri": f"{ROOT}/Calls.json?PageSize=50&Page=0",
            "next_page_uri": None,
            "previous_page_uri": None,
            "uri": f"{ROOT}/Calls.json",
        }
    )
    assert "total" not in CallList.model_fields
    assert "num_pages" not in CallList.model_fields
    assert (parsed.start, parsed.end) == (0, 0)
    assert parsed.items == []


ITERATORS: list[tuple[str, Callable[[Any], Any], str, str, dict[str, Any]]] = [
    ("calls", lambda c: c.calls.iter(), "Calls.json", "calls", item("Call")),
    (
        "conferences",
        lambda c: c.conferences.iter(),
        "Conferences.json",
        "conferences",
        item("Conference"),
    ),
    ("messages", lambda c: c.messages.iter(), "Messages.json", "messages", item("Message")),
    ("queues", lambda c: c.queues.iter(), "Queues.json", "queues", item("Queue")),
    (
        "recordings",
        lambda c: c.recordings.iter(),
        "Recordings.json",
        "recordings",
        item("Recording"),
    ),
    (
        "sip domains",
        lambda c: c.sip.domains.iter(),
        "SIP/Domains.json",
        "domains",
        item("SipDomain"),
    ),
    (
        "sip registrations",
        lambda c: c.sip.registrations.iter(),
        "SIP/Registrations.json",
        "registrations",
        item("SipRegistration"),
    ),
    (
        "incoming numbers",
        lambda c: c.incoming_phone_numbers.iter(),
        "IncomingPhoneNumbers.json",
        "incoming_phone_numbers",
        item("IncomingPhoneNumber"),
    ),
    (
        "caller ids",
        lambda c: c.outgoing_caller_ids.iter(),
        "OutgoingCallerIds.json",
        "outgoing_caller_ids",
        item("OutgoingCallerId"),
    ),
    (
        "usage",
        lambda c: c.usage_records.iter(),
        "Usage/Records.json",
        "usage_records",
        item("UsageRecord"),
    ),
    (
        "transcriptions",
        lambda c: c.transcriptions.iter(),
        "Transcriptions.json",
        "transcriptions",
        item("Transcription"),
    ),
]


@pytest.mark.parametrize(("name", "make", "path", "key", "item"), ITERATORS)
def test_every_iterator_follows_page_tokens(
    name: str, make: Callable[[Any], Any], path: str, key: str, item: dict[str, Any]
) -> None:
    link = f"{ROOT}/{path}?PageToken=T2"
    server = Server(page(key, [item, item], link), page(key, [item], None))
    with server.client() as c:
        assert len(list(make(c))) == 3
    assert server.requests[1].url.raw_path.decode() == link


@pytest.mark.parametrize(("name", "make", "path", "key", "item"), ITERATORS)
async def test_every_async_iterator_follows_page_tokens(
    name: str, make: Callable[[Any], Any], path: str, key: str, item: dict[str, Any]
) -> None:
    link = f"{ROOT}/{path}?PageToken=T2"
    server = Server(page(key, [item, item], link), page(key, [item], None))
    async with server.aclient() as c:
        assert len([x async for x in make(c)]) == 3
    assert server.requests[1].url.raw_path.decode() == link


async def test_async_iter_is_lazy() -> None:
    server = Server(*[page("calls", [call(i), call(i + 1)], NEXT) for i in range(0, 20, 2)])
    async with server.aclient() as c:
        iterator = c.calls.iter(page_size=2)
        taken = [await iterator.__anext__() for _ in range(3)]
        await iterator.aclose()
    assert len(taken) == 3
    assert len(server.requests) == 2


async def test_async_client_paginate_and_next_page() -> None:
    server = Server(page("calls", [call(2)], None))
    async with server.aclient() as c:
        first = CallList.model_validate(page("calls", [call(1)], NEXT))
        sids = [x.sid async for x in c.paginate(first)]
        assert await c.next_page(CallList.model_validate(page("calls", [], None))) is None
    assert sids == [call(1)["sid"], call(2)["sid"]]
