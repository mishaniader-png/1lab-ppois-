"""Deposit products, fees, and currency exchange models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from .accounts import Account
from .exceptions import CurrencyRateNotFoundError, InvalidAmountError, ValidationError


@dataclass(eq=False)
class InterestRate:
    currency: str
    annual_rate: Decimal
    effective_from: date

    def annual_to_monthly(self) -> Decimal:
        return self.annual_rate / Decimal("12")

    def apply_to(self, principal: Decimal, days: int) -> Decimal:
        if principal < 0 or days < 0:
            raise ValidationError("Principal and days cannot be negative")
        return principal * self.annual_rate / Decimal("100") * Decimal(days) / Decimal("365")


@dataclass(eq=False)
class DepositProduct:
    product_id: str
    name: str
    min_amount: Decimal
    interest_rate: InterestRate
    term_days: int

    def estimate_return(self, amount: Decimal) -> Decimal:
        if amount < self.min_amount or self.term_days <= 0:
            raise ValidationError("Deposit amount or term does not meet product requirements")
        return amount + self.interest_rate.apply_to(amount, self.term_days)

    def is_available_for(self, amount: Decimal) -> bool:
        return amount >= self.min_amount and self.term_days > 0


@dataclass(eq=False)
class Deposit:
    deposit_id: str
    account: Account
    product: DepositProduct
    principal: Decimal
    opened_on: date
    maturity_date: date
    is_closed: bool = False
    is_funded: bool = False

    def fund(self) -> Decimal:
        if self.is_closed or self.is_funded:
            raise ValidationError("Deposit cannot be funded in its current state")
        if self.principal <= 0:
            raise InvalidAmountError("Deposit principal must be positive")
        balance = self.account.withdraw(self.principal)
        self.is_funded = True
        return balance

    def accrue_interest(self, as_of: date | None = None) -> Decimal:
        current_date = as_of or date.today()
        if not self.is_funded:
            raise ValidationError("Deposit must be funded before interest accrues")
        if current_date < self.opened_on:
            raise ValidationError("Interest date precedes deposit opening")
        days = min((current_date - self.opened_on).days, self.product.term_days)
        return self.product.interest_rate.apply_to(self.principal, days)

    def close(self, as_of: date | None = None) -> Decimal:
        current_date = as_of or date.today()
        if self.is_closed:
            raise ValidationError("Deposit is already closed")
        if not self.is_funded:
            raise ValidationError("Deposit must be funded before closing")
        if current_date < self.maturity_date:
            raise ValidationError("Deposit has not reached maturity")
        payout = self.principal + self.accrue_interest(current_date)
        self.account.deposit(payout)
        self.is_closed = True
        return payout


@dataclass(eq=False)
class Fee:
    fee_code: str
    name: str
    fixed_amount: Decimal
    percentage_rate: Decimal = Decimal("0.00")
    is_waived: bool = False

    def calculate(self, base_amount: Decimal) -> Decimal:
        if base_amount < 0:
            raise InvalidAmountError("Fee base amount cannot be negative")
        if self.is_waived:
            return Decimal("0.00")
        return self.fixed_amount + base_amount * self.percentage_rate / Decimal("100")

    def waive(self) -> None:
        self.is_waived = True


@dataclass(eq=False)
class ExchangeRate:
    base_currency: str
    quote_currency: str
    rate: Decimal
    updated_at: datetime

    def convert(self, amount: Decimal) -> Decimal:
        if amount <= 0:
            raise InvalidAmountError("Exchange amount must be positive")
        if self.rate <= 0:
            raise CurrencyRateNotFoundError("Exchange rate must be positive")
        return amount * self.rate

    def invert(self) -> ExchangeRate:
        if self.rate <= 0:
            raise CurrencyRateNotFoundError("Cannot invert a non-positive exchange rate")
        return ExchangeRate(self.quote_currency, self.base_currency, Decimal("1") / self.rate, self.updated_at)


@dataclass(eq=False)
class CurrencyExchange:
    exchange_id: str
    source_account: Account
    target_account: Account
    amount: Decimal
    rate: ExchangeRate
    is_executed: bool = False

    def quote(self) -> Decimal:
        return self.rate.convert(self.amount)

    def execute(self) -> Decimal:
        if self.is_executed:
            raise ValidationError("Currency exchange has already been executed")
        if self.source_account.currency != self.rate.base_currency:
            raise ValidationError("Source account currency does not match exchange rate")
        if self.target_account.currency != self.rate.quote_currency:
            raise ValidationError("Target account currency does not match exchange rate")
        converted = self.quote()
        self.source_account.withdraw(self.amount)
        self.target_account.deposit(converted)
        self.is_executed = True
        return converted
