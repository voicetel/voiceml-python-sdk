"""Account (self) and Balance resources."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base, _Request

AccountStatus = Literal["active", "suspended", "closed"]
AccountType = Literal["Trial", "Full"]
HttpMethod = Literal["GET", "POST"]


class Account(_Base):
    """The authenticated account (``GET /2010-04-01/Accounts/{Sid}.json``)."""

    sid: str | None = None
    friendly_name: str | None = None
    status: AccountStatus | str | None = None
    type: AccountType | str | None = None
    owner_account_sid: str | None = None
    date_created: str | None = None
    date_updated: str | None = None
    uri: str | None = None
    subresource_uris: dict[str, str] | None = None


class UpdateAccountRequest(_Request):
    """Body for ``POST /2010-04-01/Accounts/{Sid}.json`` — partial self-update.

    Only set fields are sent. ``allow_cidr`` is sent as repeated ``AllowCidr`` keys; an
    empty list sends a single empty ``AllowCidr=`` value, which clears the allow-list.
    The token / secret fields are excluded from ``repr()``. A concurrent modification
    raises :class:`voiceml.ConflictError` (code 20409): refetch and retry.
    """

    friendly_name: str | None = Field(default=None, alias="FriendlyName")
    voice_url: str | None = Field(default=None, alias="VoiceUrl")
    voice_method: HttpMethod | None = Field(default=None, alias="VoiceMethod")
    voice_fallback_url: str | None = Field(default=None, alias="VoiceFallbackUrl")
    voice_fallback_method: HttpMethod | None = Field(default=None, alias="VoiceFallbackMethod")
    stt_fs_vendor: str | None = Field(default=None, alias="SttFsVendor")
    stt_http_url: str | None = Field(default=None, alias="SttHttpUrl")
    stt_http_token: str | None = Field(default=None, alias="SttHttpToken", repr=False)
    tts_http_url: str | None = Field(default=None, alias="TtsHttpUrl")
    tts_http_token: str | None = Field(default=None, alias="TtsHttpToken", repr=False)
    tts_engine_name: str | None = Field(default=None, alias="TtsEngineName")
    tts_default_voice: str | None = Field(default=None, alias="TtsDefaultVoice")
    tts_default_language: str | None = Field(default=None, alias="TtsDefaultLanguage")
    aws_bucket: str | None = Field(default=None, alias="AwsBucket")
    aws_region: str | None = Field(default=None, alias="AwsRegion")
    aws_prefix: str | None = Field(default=None, alias="AwsPrefix")
    aws_access_key_id: str | None = Field(default=None, alias="AwsAccessKeyId")
    aws_secret_access_key: str | None = Field(default=None, alias="AwsSecretAccessKey", repr=False)
    aws_kms_key_id: str | None = Field(default=None, alias="AwsKmsKeyId")
    allow_cidr: list[str] | None = Field(default=None, alias="AllowCidr")

    def to_form(self) -> dict[str, object]:
        form = super().to_form()
        if form.get("AllowCidr") == []:
            form["AllowCidr"] = ""
        return form


class AccountWithKey(_Base):
    """The account view returned by ``POST /2010-04-01/Accounts/{Sid}/RotateKey.json``.

    VoiceML extension: ``api_key`` is the freshly generated key. No read endpoint
    exposes it, so store it right away — the previous key stops working
    immediately. ``api_key`` is excluded from ``repr()`` so it never leaks into
    logs or debug output; access it explicitly via ``account.api_key``.
    """

    sid: str
    api_key: str = Field(repr=False)
    sip_username: str
    phone_regions: list[str]
    allow_cidr: list[str]
    disabled: bool
    stt_http_token_set: bool
    tts_http_token_set: bool
    stripe_secret_key_set: bool
    pay_enabled: bool
    sms_allowed_providers: list[str]
    stt_allowed_providers: list[str]
    aws_secret_access_key_set: bool
    created_at: str
    updated_at: str
    name: str | None = None
    stt_fs_vendor: str | None = None
    stt_http_url: str | None = None
    tts_http_url: str | None = None
    tts_engine_name: str | None = None
    tts_default_voice: str | None = None
    tts_default_language: str | None = None
    sms_provider: str | None = None
    stt_provider: str | None = None
    voice_url: str | None = None
    voice_method: str | None = None
    voice_fallback_url: str | None = None
    voice_fallback_method: str | None = None
    aws_bucket: str | None = None
    aws_region: str | None = None
    aws_prefix: str | None = None
    aws_access_key_id: str | None = None
    aws_kms_key_id: str | None = None


class Balance(_Base):
    """``GET /Balance.json`` — VoiceML reports a static zero balance."""

    account_sid: str | None = None
    balance: str | None = None
    currency: str | None = None
