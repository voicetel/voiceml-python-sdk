"""Spec-driven contract harness.

Loads the vendored public OpenAPI document (``tests/fixtures/voiceml-openapi.json``),
walks every public method reachable from :class:`voiceml.Client` /
:class:`voiceml.AsyncClient` through an ``httpx.MockTransport``, and matches each
recorded request against the spec's operations.

The fixture is test-only data: it is excluded from the sdist and wheel (see
``[tool.hatch.build]`` in ``pyproject.toml``).
"""

from __future__ import annotations

import asyncio
import collections.abc
import contextvars
import inspect
import json
import re
import types
import urllib.parse
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import cache
from pathlib import Path
from typing import Any, Literal, Union, get_args, get_origin, get_type_hints

import httpx
from pydantic import BaseModel

import voiceml

SPEC_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "voiceml-openapi.json"

ACCOUNT_SID = "AC" + "0" * 32
API_KEY = "contract-test-key"
BASE_URL = "https://voiceml.voicetel.com"
DEFAULT_HOST = "voiceml.voicetel.com"
MESSAGING_HOST = "messaging.voicetel.com"
CONVERSATIONS_HOST = "conversations.voicetel.com"

_HTTP_METHODS = ("get", "post", "put", "patch", "delete")


# ---------------------------------------------------------------------------
# Spec model
# ---------------------------------------------------------------------------


@dataclass
class BodySpec:
    content_type: str
    props: dict[str, dict[str, Any]]
    required: set[str]


@dataclass
class Op:
    op_id: str
    method: str
    path: str
    tags: list[str]
    auth: bool
    regex: re.Pattern[str]
    template_params: int
    query: dict[str, dict[str, Any]]
    required_query: set[str]
    bodies: list[BodySpec]
    body_required: bool
    success_status: int
    success_schema: dict[str, Any] | None
    success_binary: bool

    @property
    def expected_host(self) -> str:
        hosts = set()
        for tag in self.tags:
            if tag.startswith("ConversationsV1"):
                hosts.add(CONVERSATIONS_HOST)
            elif tag == "MessagingV1Service":
                hosts.add(MESSAGING_HOST)
            else:
                hosts.add(DEFAULT_HOST)
        if len(hosts) != 1:
            # Double-tagged ``/v1/Services`` ops live on both product hosts; the
            # caller resolves which one applies from the request host.
            return "|".join(sorted(hosts))
        return hosts.pop()

    def host_ok(self, host: str) -> bool:
        return host in self.expected_host.split("|")


@cache
def load_spec() -> dict[str, Any]:
    with SPEC_PATH.open(encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)
    return data


def resolve(obj: Any) -> Any:
    spec = load_spec()
    seen = 0
    while isinstance(obj, dict) and "$ref" in obj:
        ref = obj["$ref"]
        assert ref.startswith("#/"), ref
        node: Any = spec
        for part in ref[2:].split("/"):
            node = node[part]
        obj = node
        seen += 1
        assert seen < 50, "ref cycle"
    return obj


# ``oneOf`` responses shared by two products (``/v1/Services``) synthesize the variant
# that matches the host being called.
_ONEOF_PREFERENCE: contextvars.ContextVar[str] = contextvars.ContextVar(
    "oneof_preference", default=""
)


def merge_schema(schema: Any) -> dict[str, Any]:
    """Resolve ``$ref`` and flatten ``allOf`` into a single object schema."""
    schema = resolve(schema)
    if not isinstance(schema, dict):
        return {}
    if "allOf" in schema:
        out: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
        for sub in schema["allOf"]:
            merged = merge_schema(sub)
            out["properties"].update(merged.get("properties", {}))
            out["required"] += merged.get("required", [])
        for k, v in schema.items():
            if k != "allOf":
                out.setdefault(k, v)
        return out
    for key in ("oneOf", "anyOf"):
        if key in schema:
            preferred = _ONEOF_PREFERENCE.get()
            refs = [s.get("$ref", "") for s in schema[key] if isinstance(s, dict)]
            if preferred and any(preferred in r for r in refs):
                chosen = next(s for s in schema[key] if preferred in s.get("$ref", ""))
                return merge_schema(chosen)
            variants = [merge_schema(s) for s in schema[key]]
            non_null = [v for v in variants if v.get("type") != "null"]
            base = dict(non_null[0] if non_null else variants[0])
            if len(non_null) != len(variants):
                base["nullable"] = True
            return base
    return schema


def is_nullable(schema: dict[str, Any]) -> bool:
    t = schema.get("type")
    return schema.get("nullable") is True or (isinstance(t, list) and "null" in t)


def base_type(schema: dict[str, Any]) -> str | None:
    t = schema.get("type")
    if isinstance(t, list):
        non_null = [x for x in t if x != "null"]
        t = non_null[0] if non_null else "null"
    if t is None:
        if "properties" in schema or "additionalProperties" in schema:
            return "object"
        if "items" in schema:
            return "array"
    return t if isinstance(t, str) else None


@cache
def build_ops() -> tuple[Op, ...]:
    spec = load_spec()
    global_security = spec.get("security", [])
    ops: list[Op] = []
    for path, item in spec["paths"].items():
        path_params = [resolve(p) for p in item.get("parameters", [])]
        for method in _HTTP_METHODS:
            if method not in item:
                continue
            op = item[method]
            params = path_params + [resolve(p) for p in op.get("parameters", [])]
            query = {p["name"]: resolve(p.get("schema", {})) for p in params if p["in"] == "query"}
            required_query = {p["name"] for p in params if p["in"] == "query" and p.get("required")}
            bodies: list[BodySpec] = []
            body_required = False
            rb = op.get("requestBody")
            if rb:
                rb = resolve(rb)
                body_required = bool(rb.get("required"))
                for ct, media in rb.get("content", {}).items():
                    schema = merge_schema(media.get("schema", {}))
                    bodies.append(
                        BodySpec(
                            content_type=ct,
                            props=dict(schema.get("properties", {})),
                            required=set(schema.get("required", [])),
                        )
                    )
            security = op.get("security", global_security)
            success_status = 200
            success_schema: dict[str, Any] | None = None
            success_binary = False
            for code in ("200", "201", "202", "204", "302"):
                resp = op.get("responses", {}).get(code)
                if resp is None:
                    continue
                resp = resolve(resp)
                success_status = int(code)
                content = resp.get("content", {})
                if "application/json" in content:
                    success_schema = content["application/json"].get("schema", {})
                elif content or code == "302":
                    success_binary = True
                break
            rx = "^" + re.sub(r"\\\{[^}]+\\\}", "[^/]+", re.escape(path)) + "$"
            ops.append(
                Op(
                    op_id=op["operationId"],
                    method=method.upper(),
                    path=path,
                    tags=list(op.get("tags", [])),
                    auth=bool(security),
                    regex=re.compile(rx),
                    template_params=path.count("{"),
                    query=query,
                    required_query=required_query,
                    bodies=bodies,
                    body_required=body_required,
                    success_status=success_status,
                    success_schema=success_schema,
                    success_binary=success_binary,
                )
            )
    return tuple(ops)


def match_op(method: str, raw_path: str) -> Op | None:
    hits = [o for o in build_ops() if o.method == method and o.regex.match(raw_path)]
    if not hits:
        return None
    hits.sort(key=lambda o: o.template_params)
    return hits[0]


# ---------------------------------------------------------------------------
# Response synthesis
# ---------------------------------------------------------------------------

Variant = Literal["full", "nulls", "minimal", "unknown-enum", "extra"]


def synth(schema: Any, variant: Variant = "full", depth: int = 0) -> Any:
    s = merge_schema(schema)
    if depth > 8:
        return None
    if variant == "nulls" and is_nullable(s):
        return None
    t = base_type(s)
    if "enum" in s:
        if variant == "unknown-enum" and t == "string":
            return "zz-new-value"
        values = [v for v in s["enum"] if v not in ("", None)] or s["enum"]
        return values[0]
    if t == "string":
        fmt = s.get("format", "")
        if fmt == "date-time":
            return "2026-07-01T00:00:00Z"
        if fmt == "date":
            return "2026-07-01"
        if fmt == "uri":
            return "https://example.com/x"
        return "str"
    if t == "integer":
        return 1
    if t == "number":
        return 1.5
    if t == "boolean":
        return True
    if t == "array":
        return [synth(s.get("items", {}), variant, depth + 1)]
    if t == "object" or t is None:
        out: dict[str, Any] = {}
        props: dict[str, Any] = s.get("properties", {})
        required = set(s.get("required", []))
        for key, sub in props.items():
            if variant == "minimal" and key not in required:
                continue
            if key in ("next_page_uri", "next_page_url"):
                # Never link onward from synthesized pages: the walk must
                # terminate after one request per call.
                out[key] = None
                continue
            out[key] = synth(sub, variant, depth + 1)
        extra = s.get("additionalProperties")
        if not props and isinstance(extra, dict):
            out["k"] = synth(extra, variant, depth + 1)
        if variant == "extra" and (props or not extra):
            # Maps (``additionalProperties`` only) keep their declared value type.
            out["zz_new_field"] = {"nested": [1, None]}
        return out
    return None


# ---------------------------------------------------------------------------
# Recording transport
# ---------------------------------------------------------------------------


@dataclass
class Recorder:
    variant: Variant = "full"
    requests: list[httpx.Request] = field(default_factory=list)

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        op = match_op(request.method, request.url.raw_path.decode().split("?")[0])
        if op is None:
            return httpx.Response(404, json={"code": 20404, "message": "no spec op", "status": 404})
        if op.success_binary or op.success_schema is None:
            if op.success_status == 204:
                return httpx.Response(204)
            return httpx.Response(
                200, content=b"RIFF....WAVE", headers={"content-type": "audio/wav"}
            )
        status = op.success_status if op.success_status != 302 else 200
        preference = {MESSAGING_HOST: "Messaging", CONVERSATIONS_HOST: "Conversations"}
        token = _ONEOF_PREFERENCE.set(preference.get(request.url.host, ""))
        try:
            body = synth(op.success_schema, self.variant)
        finally:
            _ONEOF_PREFERENCE.reset(token)
        return httpx.Response(status, json=body)


def make_clients(recorder: Recorder) -> tuple[voiceml.Client, voiceml.AsyncClient]:
    sync_http = httpx.Client(transport=httpx.MockTransport(recorder.handler))
    async_http = httpx.AsyncClient(transport=httpx.MockTransport(recorder.handler))
    client = voiceml.Client(
        account_sid=ACCOUNT_SID,
        api_key=API_KEY,
        base_url=BASE_URL,
        http_client=sync_http,
        max_retries=0,
    )
    aclient = voiceml.AsyncClient(
        account_sid=ACCOUNT_SID,
        api_key=API_KEY,
        base_url=BASE_URL,
        http_client=async_http,
        max_retries=0,
    )
    return client, aclient


# ---------------------------------------------------------------------------
# Argument synthesis
# ---------------------------------------------------------------------------


def _is_union(tp: Any) -> bool:
    return get_origin(tp) in (Union, types.UnionType)


# Arguments whose server-side format is validated client-side get a well-formed value.
VALUE_OVERRIDES: dict[str, Any] = {
    "sms_application_sid": "AP" + "0" * 32,
    "voice_application_sid": "AP" + "0" * 32,
}


def value_for(tp: Any, name: str, *, full: bool) -> Any:
    if name in VALUE_OVERRIDES:
        return VALUE_OVERRIDES[name]
    if _is_union(tp):
        args = [a for a in get_args(tp) if a is not type(None)]
        return value_for(args[0], name, full=full)
    origin = get_origin(tp)
    if origin is Literal:
        return get_args(tp)[0]
    if origin in (list, tuple, collections.abc.Sequence):
        args = get_args(tp) or (str,)
        if get_origin(args[0]) is Literal:
            return list(get_args(args[0])[:2])
        first = value_for(args[0], name, full=full)
        if isinstance(first, str):
            return [f"{first}1", f"{first}2"]
        return [first, first]
    if origin in (dict, collections.abc.Mapping):
        return {"k": "v"}
    if tp is Any or tp is object:
        return f"X{name}"
    if tp is datetime:
        return datetime(2026, 7, 1, tzinfo=timezone.utc)
    if tp is str:
        return f"X{name}"
    if tp is bool:
        return True
    if tp is int:
        return 1
    if tp is float:
        return 1.5
    if isinstance(tp, type) and issubclass(tp, BaseModel):
        return build_model(tp, full=full)
    raise TypeError(f"cannot synthesize a value for {name}: {tp!r}")


def build_model(cls: type[BaseModel], *, full: bool) -> BaseModel:
    kwargs: dict[str, Any] = {}
    for fname, info in cls.model_fields.items():
        if full or info.is_required():
            kwargs[fname] = value_for(info.annotation, fname, full=full)
    return cls(**kwargs)


def call_args(fn: Callable[..., Any], *, full: bool) -> tuple[list[Any], dict[str, Any]]:
    hints = get_type_hints(fn)
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    for p in inspect.signature(fn).parameters.values():
        if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            continue
        if p.default is not inspect.Parameter.empty and not full:
            continue
        value = value_for(hints.get(p.name, str), p.name, full=full)
        if p.kind == p.KEYWORD_ONLY:
            kwargs[p.name] = value
        else:
            args.append(value)
    return args, kwargs


# ---------------------------------------------------------------------------
# Resource walk
# ---------------------------------------------------------------------------

# Methods that never issue a request on their own (pagination helpers take a
# page object produced by another call); exercised in tests/unit/test_pagination.py.
SKIP_METHODS = frozenset({"next_page"})


def _is_resource(obj: Any) -> bool:
    return type(obj).__module__.startswith("voiceml.resources")


@dataclass
class MethodSite:
    label: str
    fn: Callable[..., Any]


def iter_methods(root: Any) -> Iterator[MethodSite]:
    """Yield every public request-issuing method reachable from ``root``.

    Factory methods / callables that return sid-bound sub-resources are
    invoked with placeholder sids and walked recursively.
    """
    seen: set[int] = set()
    keep: list[Any] = []

    def walk(obj: Any, label: str, depth: int) -> Iterator[MethodSite]:
        if depth > 8 or id(obj) in seen:
            return
        seen.add(id(obj))
        keep.append(obj)
        if callable(obj) and "__call__" in type(obj).__dict__:
            args, kwargs = call_args(obj.__call__, full=False)
            child = obj(*args, **kwargs)
            if _is_resource(child):
                yield from walk(child, f"{label}()", depth + 1)
        for name in sorted(dir(obj)):
            if name.startswith("_") or name in SKIP_METHODS:
                continue
            attr = getattr(obj, name)
            if inspect.ismethod(attr):
                sig_ret = get_type_hints(attr).get("return")
                if isinstance(sig_ret, type) and sig_ret.__module__.startswith("voiceml.resources"):
                    args, kwargs = call_args(attr, full=False)
                    yield from walk(attr(*args, **kwargs), f"{label}.{name}()", depth + 1)
                    continue
                yield MethodSite(f"{label}.{name}", attr)
            elif _is_resource(attr):
                yield from walk(attr, f"{label}.{name}", depth + 1)

    for name in sorted(dir(root)):
        if name.startswith("_"):
            continue
        attr = getattr(root, name)
        if _is_resource(attr):
            yield from walk(attr, name, 0)


# ---------------------------------------------------------------------------
# Request checks
# ---------------------------------------------------------------------------


@dataclass
class Observed:
    op: Op
    query_keys: list[str]
    body_keys: list[str]
    content_type: str


def parse_keys(raw: str) -> list[str]:
    return [k for k, _ in urllib.parse.parse_qsl(raw, keep_blank_values=True)]


def check_request(request: httpx.Request) -> tuple[Observed | None, list[str]]:
    raw_path = request.url.raw_path.decode().split("?")[0]
    op = match_op(request.method, raw_path)
    if op is None:
        return None, [f"no spec operation for {request.method} {raw_path}"]
    issues: list[str] = []
    if not op.host_ok(request.url.host):
        issues.append(f"host {request.url.host} (expected {op.expected_host})")
    has_auth = "authorization" in request.headers
    if has_auth != op.auth:
        issues.append(f"auth header present={has_auth} but spec security requires {op.auth}")
    query_keys = parse_keys(request.url.query.decode())
    unknown_q = sorted({k for k in query_keys if k not in op.query})
    if unknown_q:
        issues.append(f"non-spec query params {unknown_q}")
    missing_q = sorted(op.required_query - set(query_keys))
    if missing_q:
        issues.append(f"missing required query params {missing_q}")
    for key in {k for k in query_keys if query_keys.count(k) > 1}:
        if base_type(merge_schema(op.query.get(key, {}))) != "array":
            issues.append(f"repeated non-array query param {key}")
    body_keys: list[str] = []
    ctype = request.headers.get("content-type", "").split(";")[0].strip()
    content = request.content
    if content:
        spec_body = next((b for b in op.bodies if b.content_type == ctype), None)
        if spec_body is None:
            issues.append(
                f"content-type {ctype!r} not declared (spec: {[b.content_type for b in op.bodies]})"
            )
        else:
            if ctype == "application/json":
                payload = json.loads(content)
                body_keys = list(payload) if isinstance(payload, dict) else []
            else:
                body_keys = parse_keys(content.decode())
            unknown_b = sorted({k for k in body_keys if k not in spec_body.props})
            if unknown_b:
                issues.append(f"non-spec body props {unknown_b}")
            missing_b = sorted(spec_body.required - set(body_keys))
            if missing_b:
                issues.append(f"missing required body props {missing_b}")
            for key in {k for k in body_keys if body_keys.count(k) > 1}:
                prop = merge_schema(spec_body.props.get(key, {}))
                if base_type(prop) != "array":
                    issues.append(f"repeated non-array body prop {key}")
    elif op.body_required and any(b.required for b in op.bodies):
        issues.append("spec requires a request body but none was sent")
    return Observed(op, query_keys, body_keys, ctype), issues


# ---------------------------------------------------------------------------
# Request-model enum checks
# ---------------------------------------------------------------------------


def _literal_values(annotation: Any) -> set[Any] | None:
    """Values a Literal-typed annotation accepts, or ``None`` if it is open (``str``)."""
    origin = get_origin(annotation)
    if origin is Literal:
        return set(get_args(annotation))
    if _is_union(annotation) or origin is list:
        values: set[Any] = set()
        for arg in get_args(annotation):
            if arg is type(None):
                continue
            sub = _literal_values(arg)
            if sub is None:
                return None
            values |= sub
        return values
    return None


def _prop_enum(prop: dict[str, Any]) -> set[Any] | None:
    schema = merge_schema(prop)
    if "enum" in schema:
        return set(schema["enum"])
    if base_type(schema) == "array":
        items = merge_schema(schema.get("items", {}))
        if "enum" in items:
            return set(items["enum"])
    return None


def request_model_enum_issues() -> list[str]:
    """Every request-model field that maps to a spec enum must be a ``Literal`` whose
    values are a subset of the spec's.

    A model is matched to the operations whose body declares all of its wire names.
    """
    from voiceml.models._base import _Request

    issues: list[str] = []
    models = {
        cls
        for cls in vars(voiceml.models).values()
        if isinstance(cls, type) and issubclass(cls, _Request) and cls is not _Request
    }
    for cls in sorted(models, key=lambda c: c.__name__):
        aliases = {info.alias or name: name for name, info in cls.model_fields.items()}
        candidates = [
            body
            for op in build_ops()
            for body in op.bodies
            if aliases and set(aliases) <= set(body.props)
        ]
        for alias, fname in aliases.items():
            enums = [_prop_enum(body.props[alias]) for body in candidates]
            declared = set().union(*[e for e in enums if e is not None]) if any(enums) else None
            if declared is None:
                continue
            accepted = _literal_values(cls.model_fields[fname].annotation)
            if accepted is None:
                issues.append(
                    f"{cls.__name__}.{fname} ({alias}) is open; spec enum {sorted(declared)}"
                )
            elif not accepted <= declared:
                issues.append(
                    f"{cls.__name__}.{fname} ({alias}) accepts non-spec values "
                    f"{sorted(accepted - declared)}"
                )
    return issues


# ---------------------------------------------------------------------------
# Full exercise of a client
# ---------------------------------------------------------------------------

# Methods that legitimately refuse to send a minimal call: the spec marks the fields
# optional but documents that at least one of them must be present.
CLIENT_SIDE_REQUIRED: dict[str, str] = {
    "messages.create": "Body or MediaUrl is required (spec: Body required unless MediaUrl)",
}


@dataclass
class Report:
    methods: list[str] = field(default_factory=list)
    covered: dict[str, list[str]] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    sent_keys: dict[str, set[str]] = field(default_factory=dict)
    list_products: list[tuple[str, str, str]] = field(default_factory=list)


def _drive(fn: Callable[..., Any], args: list[Any], kwargs: dict[str, Any]) -> Any:
    result = fn(*args, **kwargs)
    if inspect.iscoroutine(result):
        return asyncio.run(result)
    if inspect.isasyncgen(result):
        gen = result

        async def drain() -> list[Any]:
            return [item async for item in gen]

        return asyncio.run(drain())
    if inspect.isgenerator(result):
        return list(result)
    return result


def exercise(which: Literal["sync", "async"]) -> Report:
    """Call every public method twice (required args only, then every arg) and check
    each recorded request against the spec."""
    from voiceml.models.common import ListResponse

    recorder = Recorder()
    client, aclient = make_clients(recorder)
    root: Any = client if which == "sync" else aclient
    report = Report()
    for site in iter_methods(root):
        report.methods.append(site.label)
        for full in (False, True):
            mode = "full" if full else "minimal"
            recorder.requests.clear()
            try:
                args, kwargs = call_args(site.fn, full=full)
                result = _drive(site.fn, args, kwargs)
            except Exception as exc:
                if not full and site.label in CLIENT_SIDE_REQUIRED and not recorder.requests:
                    continue
                report.issues.append(f"{site.label} [{mode}]: raised {exc!r}"[:400])
                continue
            if len(recorder.requests) != 1:
                report.issues.append(
                    f"{site.label} [{mode}]: sent {len(recorder.requests)} requests (expected 1)"
                )
            for request in recorder.requests:
                observed, problems = check_request(request)
                report.issues += [f"{site.label} [{mode}]: {p}" for p in problems]
                if observed is None:
                    continue
                report.covered.setdefault(observed.op.op_id, []).append(site.label)
                if full:
                    report.sent_keys.setdefault(observed.op.op_id, set()).update(
                        observed.query_keys + observed.body_keys
                    )
                if isinstance(result, ListResponse):
                    report.list_products.append(
                        (site.label, type(result).product, request.url.host)
                    )
    return report


def tolerance_failures(variant: Variant) -> list[str]:
    """Feed spec-synthesized responses of ``variant`` through every sync method."""
    recorder = Recorder(variant=variant)
    client, _ = make_clients(recorder)
    failures: list[str] = []
    for site in iter_methods(client):
        try:
            args, kwargs = call_args(site.fn, full=False)
            args, kwargs = _minimal_valid(site.label, args, kwargs)
            _drive(site.fn, args, kwargs)
        except Exception as exc:
            failures.append(f"{site.label}: {exc!r}"[:300])
    return failures


def _minimal_valid(
    label: str, args: list[Any], kwargs: dict[str, Any]
) -> tuple[list[Any], dict[str, Any]]:
    if label in CLIENT_SIDE_REQUIRED:
        kwargs = {**kwargs, "body": "hello"}
    return args, kwargs
