"""Every Python code block in README.md runs against a mocked transport.

Responses are synthesized from the vendored OpenAPI document, so the examples
exercise real request building and response decoding without touching the network.
"""

from __future__ import annotations

import re
from pathlib import Path

import httpx
import pytest

import voiceml._http as http_mod

from .contract import _harness as H

README = Path(__file__).resolve().parent.parent / "README.md"
BLOCKS = re.findall(r"```python\n(.*?)```", README.read_text(encoding="utf-8"), re.S)


def test_readme_has_python_examples() -> None:
    assert len(BLOCKS) >= 10


@pytest.mark.parametrize("source", BLOCKS, ids=[f"block{i}" for i in range(len(BLOCKS))])
def test_readme_block_runs(source: str, monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = H.Recorder()
    monkeypatch.setattr(
        http_mod,
        "_default_http_client",
        lambda timeout: httpx.Client(transport=httpx.MockTransport(recorder.handler)),
    )
    monkeypatch.setattr(
        http_mod,
        "_default_async_http_client",
        lambda timeout: httpx.AsyncClient(transport=httpx.MockTransport(recorder.handler)),
    )
    code = compile(source, str(README), "exec")
    exec(code, {"__name__": "readme_example"})
    for request in recorder.requests:
        _, problems = H.check_request(request)
        assert problems == [], problems
