"""Bank account models and account statements."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from .exceptions import AccountClosedError, InsufficientFundsError, InvalidAmountError, ValidationError
from .people import Customer


@dataclass(eq=False)
class Account:
    account_number: str
    owner: Customer
    balance: Decimal = Decimal("0.00")
    currency: str = "BYN"
    is_active: bool = True
    opened_at: date = field(default_factory=date.today)

    def deposit(self, amount: Decimal) -> Decimal:
        if not self.is_active:
            raise AccountClosedError("Cannot deposit to a closed account")
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: Decimal) -> Decimal:
        if not self.is_active:
            raise AccountClosedError("Cannot withdraw from a closed account")
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise InsufficientFundsError("Insufficient account balance")
        self.balance -= amount
        return self.balance

    def close(self) -> None:
        if self.balance != 0:
            raise ValidationError("Account must have a zero balance before closing")
        self.is_active = False

    def has_sufficient_funds(self, amount: Decimal) -> bool:
        return self.is_active and amount > 0 and self.balance >= amount


@dataclass(eq=False)
class CurrentAccount(Account):
    monthly_fee: Decimal = Decimal("0.00")
    overdraft_limit: Decimal = Decimal("0.00")

    def charge_monthly_fee(self) -> Decimal:
        if self.monthly_fee < 0 or self.balance - self.monthly_fee < -self.overdraft_limit:
            raise InsufficientFundsError("Monthly fee exceeds available balance")
        self.balance -= self.monthly_fee
        return self.monthly_fee

    def available_balance(self) -> Decimal:
        return self.balance + self.overdraft_limit


@dataclass(eq=False)
class SavingsAccount(Account):
    annual_interest_rate: Decimal = Decimal("0.00")
    minimum_balance: Decimal = Decimal("0.00")

    def calculate_interest(self, days: int = 365) -> Decimal:
        if days < 0:
            raise ValidationError("Days cannot be negative")
        eligible_balance = max(self.balance - self.minimum_balance, Decimal("0.00"))
        return eligible_balance * self.annual_interest_rate / Decimal("100") * Decimal(days) / Decimal("365")

    def capitalize_interest(self, days: int = 365) -> Decimal:
        interest = self.calculate_interest(days)
        self.balance += interest
        return interest


@dataclass(eq=False)
class BusinessAccount(Account):
    overdraft_limit: Decimal = Decimal("0.00")
    company_name: str = ""

    def set_overdraft_limit(self, limit: Decimal) -> None:
        if limit < 0:
            raise ValidationError("Overdraft limit cannot be negative")
        self.overdraft_limit = limit

    def available_balance(self) -> Decimal:
        return self.balance + self.overdraft_limit


@dataclass(eq=False)
class JointAccount(Account):
    holders: list[Customer] = field(default_factory=list)
    max_holders: int = 4

    def add_holder(self, customer: Customer) -> None:
        if any(holder.customer_id == customer.customer_id for holder in self.holders):
            raise ValidationError("Customer is already an account holder")
        if len(self.holders) >= self.max_holders:
            raise ValidationError("Maximum number of account holders reached")
        self.holders.append(customer)

    def remove_holder(self, customer_id: str) -> None:
        for holder in self.holders:
            if holder.customer_id == customer_id:
                self.holders.remove(holder)
                return
        raise ValidationError("Account holder was not found")


@dataclass(eq=False)
class StatementEntry:
    entry_id: str
    timestamp: datetime
    description: str
    amount: Decimal
    direction: str
    reference: str = ""

    def is_debit(self) -> bool:
        return self.direction == "debit"

    def formatted_line(self) -> str:
        sign = "-" if self.is_debit() else "+"
        return f"{self.timestamp.isoformat()} {sign}{self.amount} {self.description}"


@dataclass(eq=False)
class AccountStatement:
    account_number: str
    period_start: date
    period_end: date
    opening_balance: Decimal
    entries: list[StatementEntry] = field(default_factory=list)

    def add_entry(self, entry: StatementEntry) -> None:
        entry_date = entry.timestamp.date()
        if not self.period_start <= entry_date <= self.period_end:
            raise ValidationError("Statement entry is outside the statement period")
        if entry.direction not in {"credit", "debit"}:
            raise ValidationError("Statement direction must be credit or debit")
        self.entries.append(entry)
        self.entries.sort(key=lambda item: item.timestamp)

    def calculate_closing_balance(self) -> Decimal:
        balance = self.opening_balance
        for entry in self.entries:
            if entry.direction == "credit":
                balance += entry.amount
            else:
                balance -= entry.amount
        return balance

    def total_debits(self) -> Decimal:
        return sum((entry.amount for entry in self.entries if entry.direction == "debit"), Decimal("0.00"))
