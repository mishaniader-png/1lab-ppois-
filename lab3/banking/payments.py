"""Transfers, payments, and scheduled debits."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from .accounts import Account
from .exceptions import InvalidAmountError, TransferRejectedError, ValidationError


@dataclass(eq=False)
class Transfer:
    transfer_id: str
    source: Account
    destination: Account
    amount: Decimal
    status: str = "pending"
    reference: str = ""

    def validate(self) -> bool:
        if self.source is self.destination:
            raise TransferRejectedError("Source and destination accounts must differ")
        if self.source.currency != self.destination.currency:
            raise TransferRejectedError("Currency conversion is required for this transfer")
        if not self.source.is_active or not self.destination.is_active:
            raise TransferRejectedError("Both accounts must be active")
        if self.amount <= 0:
            raise InvalidAmountError("Transfer amount must be positive")
        return True

    def execute(self) -> str:
        if self.status != "pending":
            raise TransferRejectedError("Transfer is not pending")
        self.validate()
        self.source.withdraw(self.amount)
        self.destination.deposit(self.amount)
        self.status = "completed"
        return self.status

    def cancel(self) -> None:
        if self.status != "pending":
            raise TransferRejectedError("Only pending transfers can be cancelled")
        self.status = "cancelled"


@dataclass(eq=False)
class DomesticTransfer(Transfer):
    bank_code: str = ""
    fee_rate: Decimal = Decimal("0.00")

    def calculate_fee(self) -> Decimal:
        return self.amount * self.fee_rate / Decimal("100")

    def execute_domestic(self) -> str:
        if self.status != "pending":
            raise TransferRejectedError("Transfer is not pending")
        self.validate()
        self.source.withdraw(self.amount + self.calculate_fee())
        self.destination.deposit(self.amount)
        self.status = "completed"
        return self.status


@dataclass(eq=False)
class InternationalTransfer(Transfer):
    destination_country: str = ""
    swift_code: str = ""
    exchange_rate: Decimal = Decimal("1.00")

    def calculate_fee(self) -> Decimal:
        return Decimal("10.00") + self.amount * Decimal("0.02")

    def converted_amount(self) -> Decimal:
        if self.exchange_rate <= 0:
            raise ValidationError("Exchange rate must be positive")
        return self.amount * self.exchange_rate


@dataclass(eq=False)
class Payment:
    payment_id: str
    payer: Account
    payee_name: str
    amount: Decimal
    status: str = "pending"
    reference: str = ""

    def mark_paid(self) -> None:
        if self.status != "pending":
            raise TransferRejectedError("Only pending payments can be paid")
        self.payer.withdraw(self.amount)
        self.status = "paid"

    def cancel(self) -> None:
        if self.status != "pending":
            raise TransferRejectedError("Only pending payments can be cancelled")
        self.status = "cancelled"


@dataclass(eq=False)
class StandingOrder:
    order_id: str
    source: Account
    beneficiary: Account
    amount: Decimal
    interval_days: int
    next_execution: date
    is_active: bool = True

    def should_execute(self, on_date: date | None = None) -> bool:
        return self.is_active and (on_date or date.today()) >= self.next_execution

    def record_execution(self, on_date: date | None = None) -> str:
        execution_date = on_date or date.today()
        if not self.should_execute(execution_date):
            raise ValidationError("Standing order is not due")
        if self.interval_days <= 0:
            raise ValidationError("Standing order interval must be positive")
        transfer = Transfer(self.order_id, self.source, self.beneficiary, self.amount)
        status = transfer.execute()
        self.next_execution += timedelta(days=self.interval_days)
        return status


@dataclass(eq=False)
class DirectDebit:
    mandate_id: str
    account: Account
    creditor_name: str
    max_amount: Decimal
    is_authorized: bool = False

    def authorize(self) -> None:
        self.is_authorized = True

    def collect(self, amount: Decimal) -> Decimal:
        if not self.is_authorized:
            raise TransferRejectedError("Direct debit mandate is not authorized")
        if amount <= 0 or amount > self.max_amount:
            raise InvalidAmountError("Direct debit amount is outside the mandate limit")
        return self.account.withdraw(amount)
