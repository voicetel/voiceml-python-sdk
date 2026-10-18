"""Webhook signature validation against the shared cross-SDK vectors."""

from __future__ import annotations

import pytest

from voiceml import RequestValidator, validate_request
from voiceml.webhooks import SIGNATURE_HEADER, compute_signature

KEY = "test-api-key-0123456789"

V1_URL = "https://example.com/voice/answer?case=1"
V1_URL_443 = "https://example.com:443/voice/answer?case=1"
V1_PARAMS = {
    "CallSid": "CA0123456789abcdef0123456789abcdef",
    "From": "+14155550100",
    "To": "+14155550101",
    "Digits": "1234",
    "AccountSid": "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
}
V1_SIG = "pk/0TPPT+p98NEZykeWQLqRXyGU="
V1_SIG_443 = "/Bw0s+u5vlGd6zLAOTz/eMg33pk="

V3_URL = "https://example.com/hook"
V3_PAIRS = [("To", "+14155550101"), ("Event", "answered"), ("Event", "initiated")]
V3_SIG = "jCnpBgyg45aZYwUie5fmq4EYUic="

V4_URL = (
    "https://example.com/voice/answer?CallSid=CA0123456789abcdef0123456789abcdef"
    "&From=%2B14155550100"
)
V4_SIG = "9I4odWBHhF7TMIkIrNtPEPjD9fU="


def test_header_name() -> None:
    assert SIGNATURE_HEADER == "X-Twilio-Signature"


def test_v1_post_signature() -> None:
    assert compute_signature(KEY, V1_URL, V1_PARAMS) == V1_SIG
    assert validate_request(KEY, V1_URL, V1_PARAMS, V1_SIG)


def test_v1_default_port_normalisation() -> None:
    # Signed without the port, delivered with it.
    assert validate_request(KEY, V1_URL_443, V1_PARAMS, V1_SIG)
    # Signed with the port, delivered without it.
    assert compute_signature(KEY, V1_URL_443, V1_PARAMS) == V1_SIG_443
    assert validate_request(KEY, V1_URL, V1_PARAMS, V1_SIG_443)


def test_v1_fragment_is_ignored() -> None:
    assert validate_request(KEY, V1_URL + "#frag", V1_PARAMS, V1_SIG)


def test_v3_repeated_keys_keep_received_order() -> None:
    assert compute_signature(KEY, V3_URL, V3_PAIRS) == V3_SIG
    assert validate_request(KEY, V3_URL, V3_PAIRS, V3_SIG)
    # The same values as a dict of lists.
    as_lists = {"To": ["+14155550101"], "Event": ["answered", "initiated"]}
    assert validate_request(KEY, V3_URL, as_lists, V3_SIG)
    # Swapping the repeated values changes the signature.
    swapped = [("To", "+14155550101"), ("Event", "initiated"), ("Event", "answered")]
    assert not validate_request(KEY, V3_URL, swapped, V3_SIG)


def test_v3_accepts_multidict_like_objects() -> None:
    class MultiDict(dict[str, str]):
        def getlist(self, key: str) -> list[str]:
            return {"To": ["+14155550101"], "Event": ["answered", "initiated"]}[key]

    form = MultiDict(To="+14155550101", Event="answered")
    assert validate_request(KEY, V3_URL, form, V3_SIG)


def test_v4_get_signs_url_only() -> None:
    assert compute_signature(KEY, V4_URL) == V4_SIG
    assert validate_request(KEY, V4_URL, None, V4_SIG)
    assert validate_request(KEY, V4_URL, {}, V4_SIG)


@pytest.mark.parametrize(
    ("url", "params", "signature"),
    [
        (V1_URL, {**V1_PARAMS, "Digits": "9999"}, V1_SIG),  # tampered value
        (V1_URL, {**V1_PARAMS, "Extra": "1"}, V1_SIG),  # added param
        (V1_URL.replace("case=1", "case=2"), V1_PARAMS, V1_SIG),  # tampered URL
        ("https://example.com:8443/voice/answer?case=1", V1_PARAMS, V1_SIG),  # non-default port
        ("http://example.com/voice/answer?case=1", V1_PARAMS, V1_SIG),  # scheme change
        (V4_URL, None, ""),  # missing signature
    ],
)
def test_negative_cases(url: str, params: dict[str, str] | None, signature: str) -> None:
    assert not validate_request(KEY, url, params, signature)


def test_wrong_key_is_rejected() -> None:
    assert not validate_request("not-the-key", V1_URL, V1_PARAMS, V1_SIG)
    assert not validate_request("", V1_URL, V1_PARAMS, V1_SIG)


def test_request_validator_object() -> None:
    validator = RequestValidator(KEY)
    assert validator.compute_signature(V3_URL, V3_PAIRS) == V3_SIG
    assert validator.validate(V1_URL_443, V1_PARAMS, V1_SIG)
    assert KEY not in repr(validator)
