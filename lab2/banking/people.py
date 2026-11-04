"""Customer and identity-related banking models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from .exceptions import InvalidAmountError, ValidationError


@dataclass(eq=False)
class Address:
    street: str
    city: str
    postal_code: str
    country: str = "Belarus"

    def format(self) -> str:
        return f"{self.street}, {self.city}, {self.postal_code}, {self.country}"

    def is_in_city(self, city: str) -> bool:
        return self.city.casefold() == city.strip().casefold()


@dataclass(eq=False)
class ContactInfo:
    email: str
    phone: str
    preferred_channel: str = "email"

    def is_valid(self) -> bool:
        digits = "".join(char for char in self.phone if char.isdigit())
        return "@" in self.email and "." in self.email.split("@")[-1] and len(digits) >= 7

    def choose_channel(self, channel: str) -> None:
        if channel not in {"email", "sms", "phone"}:
            raise ValidationError("Unsupported contact channel")
        self.preferred_channel = channel


@dataclass(eq=False)
class Customer:
    customer_id: str
    full_name: str
    contact: ContactInfo
    is_active: bool = True

    def update_contact(self, contact: ContactInfo) -> None:
        if not contact.is_valid():
            raise ValidationError("Contact information is invalid")
        self.contact = contact

    def deactivate(self) -> None:
        self.is_active = False

    def can_use_digital_services(self) -> bool:
        return self.is_active and self.contact.is_valid()


@dataclass(eq=False)
class IndividualCustomer(Customer):
    birth_date: date = date(2000, 1, 1)
    tax_id: str = ""
    risk_level: str = "standard"

    def is_adult(self, on_date: date | None = None) -> bool:
        today = on_date or date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age >= 18

    def update_tax_id(self, tax_id: str) -> None:
        if not tax_id.strip():
            raise ValidationError("Tax ID cannot be empty")
        self.tax_id = tax_id.strip()


@dataclass(eq=False)
class BusinessCustomer(Customer):
    company_name: str = ""
    registration_number: str = ""
    industry: str = "other"

    def update_industry(self, industry: str) -> None:
        if not industry.strip():
            raise ValidationError("Industry cannot be empty")
        self.industry = industry.strip()

    def is_registered(self) -> bool:
        return bool(self.company_name.strip() and self.registration_number.strip())


@dataclass(eq=False)
class IdentificationDocument:
    document_type: str
    number: str
    expires_on: date
    issuer: str

    def is_expired(self, on_date: date | None = None) -> bool:
        return self.expires_on < (on_date or date.today())

    def renew(self, new_expiry: date, issuer: str | None = None) -> None:
        if new_expiry <= date.today():
            raise ValidationError("New document expiry date must be in the future")
        self.expires_on = new_expiry
        if issuer is not None:
            if not issuer.strip():
                raise ValidationError("Issuer cannot be empty")
            self.issuer = issuer.strip()


@dataclass(eq=False)
class IdentityVerification:
    customer_id: str
    document: IdentificationDocument
    verified: bool = False
    checked_at: datetime | None = None

    def approve(self, checked_at: datetime | None = None) -> None:
        if self.document.is_expired((checked_at or datetime.now()).date()):
            raise ValidationError("Expired document cannot be approved")
        self.verified = True
        self.checked_at = checked_at or datetime.now()

    def reject(self, checked_at: datetime | None = None) -> None:
        self.verified = False
        self.checked_at = checked_at or datetime.now()


@dataclass(eq=False)
class CustomerProfile:
    customer: Customer
    segment: CustomerSegment | None = None
    notes: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_note(self, note: str) -> None:
        if not note.strip():
            raise ValidationError("Profile note cannot be empty")
        self.notes.append(note.strip())

    def assign_segment(self, segment: CustomerSegment) -> None:
        self.segment = segment


@dataclass(eq=False)
class CustomerSegment:
    name: str
    min_balance: Decimal
    cashback_rate: Decimal
    description: str

    def qualifies(self, balance: Decimal) -> bool:
        return balance >= self.min_balance

    def cashback_for(self, purchase_amount: Decimal) -> Decimal:
        if purchase_amount <= 0:
            raise InvalidAmountError("Purchase amount must be positive")
        return purchase_amount * self.cashback_rate / Decimal("100")


@dataclass(eq=False)
class LoyaltyAccount:
    customer_id: str
    points: int = 0
    tier: str = "basic"
    last_updated: date = field(default_factory=date.today)

    def earn_points(self, purchase_amount: Decimal) -> int:
        if purchase_amount <= 0:
            raise InvalidAmountError("Purchase amount must be positive")
        earned = int(purchase_amount // Decimal("10"))
        self.points += earned
        self.last_updated = date.today()
        return earned

    def redeem_points(self, points: int) -> None:
        if points <= 0 or points > self.points:
            raise ValidationError("Requested loyalty points are unavailable")
        self.points -= points
        self.last_updated = date.today()
