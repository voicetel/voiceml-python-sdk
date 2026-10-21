"""Call resource — the Twilio-compatible Calls API surface."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request
from .common import Page

CallStatus = Literal[
    "queued", "ringing", "in-progress", "completed", "busy", "no-answer", "canceled", "failed"
]
CallDirection = Literal["inbound", "outbound-api", "outbound-dial"]
AnsweredBy = Literal[
    "human",
    "machine_start",
    "machine_end_beep",
    "machine_end_silence",
    "machine_end_other",
    "fax",
    "unknown",
    "",
]
HttpMethod = Literal["GET", "POST"]
RecordingChannelsLayout = Literal["mono", "dual"]
RecordingTrack = Literal["inbound", "outbound", "both"]
TrimMode = Literal["trim-silence", "do-not-trim"]
MachineDetectionMode = Literal["Enable", "DetectMessageEnd"]
CallStatusCallbackEvent = Literal["initiated", "ringing", "answered", "completed"]
RecordingStatusCallbackEvent = Literal["in-progress", "completed", "absent"]
UpdateCallStatus = Literal["completed", "canceled"]


class Call(_Base):
    """A Twilio-compatible Call resource."""

    sid: str | None = None
    account_sid: str | None = None
    api_version: str | None = None
    to: str | None = Field(default=None, alias="to")
    to_formatted: str | None = None
    from_: str | None = Field(default=None, alias="from")
    from_formatted: str | None = None
    parent_call_sid: str | None = None
    caller_name: str | None = None
    forwarded_from: str | None = None
    status: CallStatus | str
    direction: CallDirection | str | None = None
    answered_by: AnsweredBy | str | None = None
    start_time: str | None = None
    end_time: str | None = None
    duration: str | None = None
    price: str | None = None
    price_unit: str | None = None
    phone_number_sid: str | None = None
    annotation: str | None = None
    group_sid: str | None = None
    queue_time: str | None = None
    trunk_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None
    subresource_uris: dict[str, str] | None = None


class CallList(Page[Call]):
    calls: list[Call] = Field(default_factory=list)


class CreateCallRequest(_Request):
    """Body for ``POST /Calls``. Sent form-encoded.

    Set at most one of ``url`` / ``twiml`` / ``application_sid`` (Twiml wins if multiple
    are set — Twilio-compatible precedence).
    """

    to: str = Field(alias="To")
    from_: str = Field(alias="From")
    url: str | None = Field(default=None, alias="Url")
    method: HttpMethod | None = Field(default=None, alias="Method")
    twiml: str | None = Field(default=None, alias="Twiml")
    application_sid: str | None = Field(default=None, alias="ApplicationSid")
    fallback_url: str | None = Field(default=None, alias="FallbackUrl")
    fallback_method: HttpMethod | None = Field(default=None, alias="FallbackMethod")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: str | None = Field(default=None, alias="StatusCallbackMethod")
    status_callback_event: list[CallStatusCallbackEvent] | None = Field(
        default=None, alias="StatusCallbackEvent"
    )
    machine_detection: MachineDetectionMode | None = Field(default=None, alias="MachineDetection")
    machine_detection_timeout: int | None = Field(default=None, alias="MachineDetectionTimeout")
    machine_detection_speech_threshold: int | None = Field(
        default=None, alias="MachineDetectionSpeechThreshold"
    )
    machine_detection_speech_end_threshold: int | None = Field(
        default=None, alias="MachineDetectionSpeechEndThreshold"
    )
    machine_detection_silence_timeout: int | None = Field(
        default=None, alias="MachineDetectionSilenceTimeout"
    )
    async_amd_status_callback: str | None = Field(default=None, alias="AsyncAmdStatusCallback")
    async_amd_status_callback_method: str | None = Field(
        default=None, alias="AsyncAmdStatusCallbackMethod"
    )
    record: bool | None = Field(default=None, alias="Record")
    recording_status_callback: str | None = Field(default=None, alias="RecordingStatusCallback")
    recording_status_callback_method: str | None = Field(
        default=None, alias="RecordingStatusCallbackMethod"
    )
    recording_status_callback_event: list[RecordingStatusCallbackEvent] | None = Field(
        default=None, alias="RecordingStatusCallbackEvent"
    )
    recording_channels: RecordingChannelsLayout | None = Field(
        default=None, alias="RecordingChannels"
    )
    recording_track: RecordingTrack | None = Field(default=None, alias="RecordingTrack")
    trim: TrimMode | None = Field(default=None, alias="Trim")
    timeout: int | None = Field(default=None, alias="Timeout")
    time_limit: int | None = Field(default=None, alias="TimeLimit")
    send_digits: str | None = Field(default=None, alias="SendDigits")
    caller_id: str | None = Field(default=None, alias="CallerId")
    call_reason: str | None = Field(default=None, alias="CallReason")
    sip_auth_username: str | None = Field(default=None, alias="SipAuthUsername")
    sip_auth_password: str | None = Field(default=None, alias="SipAuthPassword")
    byoc: str | None = Field(default=None, alias="Byoc")
    async_amd: bool | None = Field(default=None, alias="AsyncAmd")
    call_token: str | None = Field(default=None, alias="CallToken")


class UpdateCallRequest(_Request):
    """Body for ``POST /Calls/{sid}``.

    Three flows on the same endpoint (Twilio-compatible):
      * ``status="completed"|"canceled"`` — terminate the call. Wins over any TwiML source.
      * ``twiml=<inline>`` — execute inline TwiML on the live call (wins over ``url``).
      * ``url=…`` — fetch new TwiML and execute it on the live call.

    StatusCallback fields apply independently — including on the terminate path.
    """

    status: UpdateCallStatus | None = Field(default=None, alias="Status")
    twiml: str | None = Field(default=None, alias="Twiml")
    url: str | None = Field(default=None, alias="Url")
    method: HttpMethod | None = Field(default=None, alias="Method")
    fallback_url: str | None = Field(default=None, alias="FallbackUrl")
    fallback_method: HttpMethod | None = Field(default=None, alias="FallbackMethod")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    status_callback_method: str | None = Field(default=None, alias="StatusCallbackMethod")
    status_callback_event: list[CallStatusCallbackEvent] | None = Field(
        default=None, alias="StatusCallbackEvent"
    )
