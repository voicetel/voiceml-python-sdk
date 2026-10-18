"""The authenticated account (``/2010-04-01/Accounts/{Sid}.json``) and its balance.

The HTTP Basic username must equal the account in the path, so these resources only
ever address the client's own account.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..models import Account, AccountWithKey, Balance, UpdateAccountRequest
from ..models.accounts import HttpMethod
from ._base import AsyncResource, Resource, path


def _update_form(
    *,
    friendly_name: str | None,
    voice_url: str | None,
    voice_method: HttpMethod | None,
    voice_fallback_url: str | None,
    voice_fallback_method: HttpMethod | None,
    stt_fs_vendor: str | None,
    stt_http_url: str | None,
    stt_http_token: str | None,
    tts_http_url: str | None,
    tts_http_token: str | None,
    tts_engine_name: str | None,
    tts_default_voice: str | None,
    tts_default_language: str | None,
    aws_bucket: str | None,
    aws_region: str | None,
    aws_prefix: str | None,
    aws_access_key_id: str | None,
    aws_secret_access_key: str | None,
    aws_kms_key_id: str | None,
    allow_cidr: Sequence[str] | None,
) -> dict[str, object]:
    return UpdateAccountRequest(
        friendly_name=friendly_name,
        voice_url=voice_url,
        voice_method=voice_method,
        voice_fallback_url=voice_fallback_url,
        voice_fallback_method=voice_fallback_method,
        stt_fs_vendor=stt_fs_vendor,
        stt_http_url=stt_http_url,
        stt_http_token=stt_http_token,
        tts_http_url=tts_http_url,
        tts_http_token=tts_http_token,
        tts_engine_name=tts_engine_name,
        tts_default_voice=tts_default_voice,
        tts_default_language=tts_default_language,
        aws_bucket=aws_bucket,
        aws_region=aws_region,
        aws_prefix=aws_prefix,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_kms_key_id=aws_kms_key_id,
        allow_cidr=list(allow_cidr) if allow_cidr is not None else None,
    ).to_form()


class AccountsResource(Resource):
    """``client.accounts`` — fetch / update the authenticated account, rotate its key."""

    def _self_path(self) -> str:
        return path("2010-04-01", "Accounts", self._acct) + ".json"

    def fetch(self) -> Account:
        """Fetch the authenticated account."""
        return Account.model_validate(self._t.request("GET", self._self_path()))

    def rotate_key(self) -> AccountWithKey:
        """Rotate the account's API key (``POST …/RotateKey.json``).

        Generates a new API key; the previous key stops working immediately.
        The new key is returned in the response (``AccountWithKey.api_key``) —
        no read endpoint exposes it, so store it right away. Raises
        :class:`voiceml.ConflictError` (code 20040) when an
        ``Idempotency-Key`` header is replayed with a different body (the SDK
        does not send one).
        """
        return AccountWithKey.model_validate(self._t.request("POST", self._path("RotateKey")))

    def update(
        self,
        *,
        friendly_name: str | None = None,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: HttpMethod | None = None,
        stt_fs_vendor: str | None = None,
        stt_http_url: str | None = None,
        stt_http_token: str | None = None,
        tts_http_url: str | None = None,
        tts_http_token: str | None = None,
        tts_engine_name: str | None = None,
        tts_default_voice: str | None = None,
        tts_default_language: str | None = None,
        aws_bucket: str | None = None,
        aws_region: str | None = None,
        aws_prefix: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_kms_key_id: str | None = None,
        allow_cidr: Sequence[str] | None = None,
    ) -> Account:
        """Update account settings; only the arguments you pass are sent.

        ``allow_cidr=[]`` clears the IP allow-list. Raises
        :class:`voiceml.ConflictError` (code 20409) when another request modified the
        account concurrently — refetch and retry.
        """
        return Account.model_validate(
            self._t.request(
                "POST",
                self._self_path(),
                data=_update_form(
                    friendly_name=friendly_name,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    stt_fs_vendor=stt_fs_vendor,
                    stt_http_url=stt_http_url,
                    stt_http_token=stt_http_token,
                    tts_http_url=tts_http_url,
                    tts_http_token=tts_http_token,
                    tts_engine_name=tts_engine_name,
                    tts_default_voice=tts_default_voice,
                    tts_default_language=tts_default_language,
                    aws_bucket=aws_bucket,
                    aws_region=aws_region,
                    aws_prefix=aws_prefix,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_kms_key_id=aws_kms_key_id,
                    allow_cidr=allow_cidr,
                ),
            )
        )


class BalanceResource(Resource):
    """``client.balance`` — ``GET /Balance.json``."""

    def fetch(self) -> Balance:
        return Balance.model_validate(self._t.request("GET", self._path("Balance")))


class AccountsAsyncResource(AsyncResource):
    """Async counterpart to :class:`AccountsResource`."""

    def _self_path(self) -> str:
        return path("2010-04-01", "Accounts", self._acct) + ".json"

    async def fetch(self) -> Account:
        return Account.model_validate(await self._t.request("GET", self._self_path()))

    async def rotate_key(self) -> AccountWithKey:
        """Rotate the account's API key (see the sync counterpart)."""
        return AccountWithKey.model_validate(await self._t.request("POST", self._path("RotateKey")))

    async def update(
        self,
        *,
        friendly_name: str | None = None,
        voice_url: str | None = None,
        voice_method: HttpMethod | None = None,
        voice_fallback_url: str | None = None,
        voice_fallback_method: HttpMethod | None = None,
        stt_fs_vendor: str | None = None,
        stt_http_url: str | None = None,
        stt_http_token: str | None = None,
        tts_http_url: str | None = None,
        tts_http_token: str | None = None,
        tts_engine_name: str | None = None,
        tts_default_voice: str | None = None,
        tts_default_language: str | None = None,
        aws_bucket: str | None = None,
        aws_region: str | None = None,
        aws_prefix: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_kms_key_id: str | None = None,
        allow_cidr: Sequence[str] | None = None,
    ) -> Account:
        return Account.model_validate(
            await self._t.request(
                "POST",
                self._self_path(),
                data=_update_form(
                    friendly_name=friendly_name,
                    voice_url=voice_url,
                    voice_method=voice_method,
                    voice_fallback_url=voice_fallback_url,
                    voice_fallback_method=voice_fallback_method,
                    stt_fs_vendor=stt_fs_vendor,
                    stt_http_url=stt_http_url,
                    stt_http_token=stt_http_token,
                    tts_http_url=tts_http_url,
                    tts_http_token=tts_http_token,
                    tts_engine_name=tts_engine_name,
                    tts_default_voice=tts_default_voice,
                    tts_default_language=tts_default_language,
                    aws_bucket=aws_bucket,
                    aws_region=aws_region,
                    aws_prefix=aws_prefix,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_kms_key_id=aws_kms_key_id,
                    allow_cidr=allow_cidr,
                ),
            )
        )


class BalanceAsyncResource(AsyncResource):
    """Async counterpart to :class:`BalanceResource`."""

    async def fetch(self) -> Balance:
        return Balance.model_validate(await self._t.request("GET", self._path("Balance")))
