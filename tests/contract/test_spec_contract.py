"""Spec-driven contract test.

Every public method reachable from ``Client`` and ``AsyncClient`` is called through a
mocked transport (once with only required arguments, once with every argument) and
each recorded request is matched against the vendored OpenAPI document:

* ``(method, path template incl. .json)`` matches exactly one operationId;
* query / form / JSON keys are a subset of the operation's declared parameters and
  properties, and the required ones are present;
* the host is the product host for the operation's tag;
* ``Authorization`` is present exactly when the operation's ``security`` requires it.

It also asserts that every operation in the spec is reachable (333/333).
"""

from __future__ import annotations

from functools import cache
from typing import Literal

import pytest

from . import _harness as H

# Operations that cannot be expressed through the SDK. Must stay empty unless an
# operation is genuinely impossible to call (document the reason next to the entry).
UNCOVERABLE_OPS: dict[str, str] = {}

# Spec parameters the SDK deliberately does not expose (none today).
UNEXPOSED_PARAMS: dict[str, set[str]] = {}

Which = Literal["sync", "async"]


@cache
def report(which: Which) -> H.Report:
    return H.exercise(which)


def test_spec_fixture_is_the_full_public_spec() -> None:
    assert len(H.build_ops()) == 333


@pytest.mark.parametrize("which", ["sync", "async"])
def test_every_spec_operation_is_reachable(which: Which) -> None:
    covered = set(report(which).covered)
    missing = sorted(
        f"{op.op_id} ({op.method} {op.path})"
        for op in H.build_ops()
        if op.op_id not in covered and op.op_id not in UNCOVERABLE_OPS
    )
    assert missing == [], f"{len(missing)} spec operations have no SDK method"
    assert len(covered) == 333


@pytest.mark.parametrize("which", ["sync", "async"])
def test_every_request_matches_the_spec(which: Which) -> None:
    issues = list(report(which).issues)
    assert issues == []


@pytest.mark.parametrize("which", ["sync", "async"])
def test_every_spec_parameter_is_sendable(which: Which) -> None:
    rep = report(which)
    gaps: dict[str, list[str]] = {}
    for op in H.build_ops():
        if op.op_id not in rep.covered:
            continue
        declared = set(op.query)
        for body in op.bodies[:1]:
            declared |= set(body.props)
        missing = (
            declared - rep.sent_keys.get(op.op_id, set()) - UNEXPOSED_PARAMS.get(op.op_id, set())
        )
        if missing:
            gaps[op.op_id] = sorted(missing)
    assert gaps == {}


def test_sync_and_async_surfaces_match() -> None:
    sync_methods = set(report("sync").methods)
    async_methods = set(report("async").methods)
    assert sync_methods == async_methods


@pytest.mark.parametrize("which", ["sync", "async"])
def test_list_envelopes_know_their_product_host(which: Which) -> None:
    hosts = {
        "default": H.DEFAULT_HOST,
        "messaging": H.MESSAGING_HOST,
        "conversations": H.CONVERSATIONS_HOST,
    }
    wrong = [
        f"{label}: page product {product!r} but fetched from {host}"
        for label, product, host in report(which).list_products
        if hosts[product] != host
    ]
    assert wrong == []


def test_request_enums_are_constrained_to_the_spec() -> None:
    assert H.request_model_enum_issues() == []
