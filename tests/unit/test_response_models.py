"""Response models tolerate nulls, unknown enum values and new fields."""

from __future__ import annotations

from voiceml.models import (
    Application,
    Call,
    HealthStatus,
    IncomingPhoneNumber,
    MessagingService,
    Participant,
    Recording,
)


def test_spec_nullable_fields_accept_null() -> None:
    call = Call.model_validate(
        {
            "sid": None,
            "account_sid": None,
            "api_version": None,
            "direction": None,
            "status": "completed",
            "date_created": None,
            "date_updated": None,
            "uri": None,
        }
    )
    assert call.sid is None and call.direction is None
    participant = Participant.model_validate(
        {"status": "connected", "muted": None, "hold": None, "coaching": None}
    )
    assert participant.muted is None


def test_unknown_enum_values_are_kept_as_strings() -> None:
    call = Call.model_validate(
        {"status": "zz-new-status", "direction": "outbound-new", "answered_by": "robot"}
    )
    assert (call.status, call.direction, call.answered_by) == (
        "zz-new-status",
        "outbound-new",
        "robot",
    )
    assert Recording.model_validate({"status": "archived", "source": "NewAPI"}).source == "NewAPI"
    assert Application.model_validate({"voice_method": "PUT"}).voice_method == "PUT"


def test_unknown_fields_are_ignored_but_kept_in_model_extra() -> None:
    call = Call.model_validate({"status": "queued", "brand_new": {"x": 1}})
    assert call.model_extra == {"brand_new": {"x": 1}}


def test_false_round_trips() -> None:
    participant = Participant.model_validate(
        {"status": "connected", "muted": False, "hold": False, "end_conference_on_exit": False}
    )
    assert participant.muted is False
    assert participant.model_dump()["hold"] is False


def test_new_response_fields_are_typed() -> None:
    number = IncomingPhoneNumber.model_validate(
        {
            "sms_url": "https://example.com/sms",
            "sms_method": "POST",
            "subresource_uris": {"assigned_add_ons": "/x"},
            "status": "in-use",
            "origin": "hosted",
            "emergency_status": "Inactive",
        }
    )
    assert number.sms_url == "https://example.com/sms"
    assert number.subresource_uris == {"assigned_add_ons": "/x"}
    app = Application.model_validate(
        {"message_status_callback": "https://m", "sms_status_callback": "https://s"}
    )
    assert (app.message_status_callback, app.sms_status_callback) == ("https://m", "https://s")
    assert Recording.model_validate({"status": "completed", "track": "both"}).track == "both"
    assert MessagingService.model_validate({"advanced_opt_out": True}).advanced_opt_out is True


def test_health_lists_are_optional() -> None:
    assert HealthStatus.model_validate({"ok": True}).warnings == []
    assert HealthStatus.model_validate({"ok": True, "warnings": None}).failures == []
