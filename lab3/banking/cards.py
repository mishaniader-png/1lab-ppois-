"""Bank card, merchant, and terminal models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from .accounts import Account
from .exceptions import CardBlockedError, CardExpiredError, InsufficientFundsError, InvalidAmountError, ValidationError
from .people import Address, Customer


@dataclass(eq=False)
class Merchant:
    merchant_id: str
    name: str
    category: str
    country: str
    is_blocked: bool = False

    def update_category(self, category: str) -> None:
        if not category.strip():
            raise ValidationError("Merchant category cannot be empty")
        self.category = category.strip()

    def is_high_risk(self) -> bool:
        return self.category.casefold() in {"gambling", "crypto", "adult", "unknown"}


@dataclass(eq=False)
class Card:
    card_number: str
    account: Account
    holder: Customer
    expiry_date: date
    is_blocked: bool = False
    pin_hash: str = ""

    def block(self) -> None:
        self.is_blocked = True

    def activate(self, on_date: date | None = None) -> None:
        if self.expiry_date < (on_date or date.today()):
            raise CardExpiredError("Expired card cannot be activated")
        self.is_blocked = False

    def is_usable_on(self, on_date: date | None = None) -> bool:
        return not self.is_blocked and self.expiry_date >= (on_date or date.today())


@dataclass(eq=False)
class DebitCard(Card):
    daily_limit: Decimal = Decimal("1000.00")
    daily_spent: Decimal = Decimal("0.00")

    def can_pay(self, amount: Decimal, on_date: date | None = None) -> bool:
        today = on_date or date.today()
        return (
            amount > 0
            and not self.is_blocked
            and self.expiry_date >= today
            and self.daily_spent + amount <= self.daily_limit
            and self.account.balance >= amount
        )

    def record_payment(self, amount: Decimal, on_date: date | None = None) -> Decimal:
        if self.is_blocked:
            raise CardBlockedError("Card is blocked")
        if self.expiry_date < (on_date or date.today()):
            raise CardExpiredError("Card is expired")
        if amount <= 0:
            raise InvalidAmountError("Card payment must be positive")
        if self.daily_spent + amount > self.daily_limit or self.account.balance < amount:
            raise InsufficientFundsError("Card payment exceeds available funds or daily limit")
        self.account.withdraw(amount)
        self.daily_spent += amount
        return self.daily_spent


@dataclass(eq=False)
class CreditCard(Card):
    credit_limit: Decimal = Decimal("0.00")
    outstanding_balance: Decimal = Decimal("0.00")

    def available_credit(self) -> Decimal:
        return self.credit_limit - self.outstanding_balance

    def record_credit_purchase(self, amount: Decimal, on_date: date | None = None) -> Decimal:
        if self.is_blocked:
            raise CardBlockedError("Card is blocked")
        if self.expiry_date < (on_date or date.today()):
            raise CardExpiredError("Card is expired")
        if amount <= 0:
            raise InvalidAmountError("Credit purchase must be positive")
        if amount > self.available_credit():
            raise InsufficientFundsError("Credit limit exceeded")
        self.outstanding_balance += amount
        return self.outstanding_balance


@dataclass(eq=False)
class CardTransaction:
    transaction_id: str
    card: Card
    merchant: Merchant
    amount: Decimal
    timestamp: datetime
    status: str = "pending"

    def approve(self) -> None:
        if self.status != "pending":
            raise ValidationError("Only pending transactions can be approved")
        if self.merchant.is_blocked:
            raise ValidationError("Merchant is blocked")
        if isinstance(self.card, DebitCard):
            self.card.record_payment(self.amount, self.timestamp.date())
        elif isinstance(self.card, CreditCard):
            self.card.record_credit_purchase(self.amount, self.timestamp.date())
        else:
            if self.card.is_blocked:
                raise CardBlockedError("Card is blocked")
            if self.card.expiry_date < self.timestamp.date():
                raise CardExpiredError("Card is expired")
            self.card.account.withdraw(self.amount)
        self.status = "approved"

    def reverse(self) -> None:
        if self.status != "approved":
            raise ValidationError("Only approved transactions can be reversed")
        if isinstance(self.card, CreditCard):
            self.card.outstanding_balance -= self.amount
        else:
            self.card.account.deposit(self.amount)
        self.status = "reversed"


@dataclass(eq=False)
class PaymentTerminal:
    terminal_id: str
    merchant: Merchant
    address: Address
    is_connected: bool = False
    processed_count: int = 0

    def connect(self) -> None:
        self.is_connected = True

    def process_payment(self, card: Card, amount: Decimal) -> CardTransaction:
        if not self.is_connected:
            raise ValidationError("Payment terminal is not connected")
        transaction = CardTransaction(
            transaction_id=f"{self.terminal_id}-{self.processed_count + 1}",
            card=card,
            merchant=self.merchant,
            amount=amount,
            timestamp=datetime.now(),
        )
        transaction.approve()
        self.processed_count += 1
        return transaction
