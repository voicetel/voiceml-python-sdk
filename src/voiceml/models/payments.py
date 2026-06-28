"""CallPayment resource — the REST companion to the ``<Pay>`` TwiML verb.

The response shape mirrors Twilio's deliberately-minimal payload — runtime
config (ChargeAmount, PaymentConnector, ValidCardTypes, etc.) is captured
server-side and not echoed back. Tenant-side BYO is binding: the account
must have ``pay_enabled = true`` AND a ``stripe_secret_key`` set, or the
call fails 403.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import _Base

PaymentBankAccountType = Literal[
    "consumer-checking",
    "consumer-savings",
    "commercial-checking",
]
PaymentInput = Literal["dtmf"]
PaymentMethod = Literal["credit-card", "ach-debit"]
PaymentTokenType = Literal["one-time", "reusable", "payment-method"]
PaymentCapture = Literal[
    "payment-card-number",
    "expiration-date",
    "security-code",
    "postal-code",
    "bank-routing-number",
    "bank-account-number",
    "payment-card-number-matcher",
    "expiration-date-matcher",
    "security-code-matcher",
    "postal-code-matcher",
]
PaymentSessionStatus = Literal["complete", "cancel"]


class CallPayment(_Base):
    """A Twilio-compatible CallPayment resource."""

    sid: str
    account_sid: str
    call_sid: str
    api_version: str | None = None
    date_created: str
    date_updated: str
    uri: str


class StartPaymentRequest(_Base):
    """Body for ``POST /Calls/{call_sid}/Payments``. Sent form-encoded.

    Every attribute the ``<Pay>`` TwiML verb accepts has a counterpart
    here. ``IdempotencyKey`` is accepted and persisted for diagnostic
    visibility but replay-dedup is NOT enforced today.
    """

    idempotency_key: str | None = Field(default=None, alias="IdempotencyKey")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    bank_account_type: PaymentBankAccountType | None = Field(
        default=None, alias="BankAccountType"
    )
    charge_amount: str | None = Field(default=None, alias="ChargeAmount")
    currency: str | None = Field(default=None, alias="Currency")
    description: str | None = Field(default=None, alias="Description")
    input: PaymentInput | None = Field(default=None, alias="Input")
    min_postal_code_length: int | None = Field(
        default=None, alias="MinPostalCodeLength"
    )
    parameter: str | None = Field(default=None, alias="Parameter")
    payment_connector: str | None = Field(default=None, alias="PaymentConnector")
    payment_method: PaymentMethod | None = Field(default=None, alias="PaymentMethod")
    postal_code: bool | None = Field(default=None, alias="PostalCode")
    security_code: bool | None = Field(default=None, alias="SecurityCode")
    timeout: int | None = Field(default=None, alias="Timeout")
    token_type: PaymentTokenType | None = Field(default=None, alias="TokenType")
    valid_card_types: str | None = Field(default=None, alias="ValidCardTypes")
    require_matching_inputs: str | None = Field(
        default=None, alias="RequireMatchingInputs"
    )
    confirmation: bool | None = Field(default=None, alias="Confirmation")


class UpdatePaymentRequest(_Base):
    """Body for ``POST /Calls/{call_sid}/Payments/{payment_sid}``.

    Either advance the session (``Capture=...``) or terminate it
    (``Status=complete`` / ``Status=cancel``).
    """

    idempotency_key: str | None = Field(default=None, alias="IdempotencyKey")
    status_callback: str | None = Field(default=None, alias="StatusCallback")
    capture: PaymentCapture | None = Field(default=None, alias="Capture")
    status: PaymentSessionStatus | None = Field(default=None, alias="Status")
