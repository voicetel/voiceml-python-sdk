"""Response models are tolerant readers.

Every sync method decodes spec-synthesized responses in five shapes: fully
populated, every spec-nullable field ``null``, only required fields, every string
enum set to an unknown value, and an unknown extra field on every object.
"""

from __future__ import annotations

import pytest

from . import _harness as H


@pytest.mark.parametrize("variant", ["full", "nulls", "minimal", "unknown-enum", "extra"])
def test_every_method_decodes_spec_payloads(variant: H.Variant) -> None:
    assert H.tolerance_failures(variant) == []
