"""Credit scoring, loan applications, loans, and repayments."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from .exceptions import InsufficientFundsError, InvalidAmountError, LoanNotApprovedError, ValidationError
from .people import Customer


@dataclass(eq=False)
class CreditScore:
    customer_id: str
    base_score: int = 600
    factors: list[tuple[str, int]] = field(default_factory=list)

    def add_factor(self, name: str, points: int) -> None:
        if not name.strip():
            raise ValidationError("Credit score factor must have a name")
        self.factors.append((name.strip(), points))

    def calculate_score(self) -> int:
        return max(300, min(850, self.base_score + sum(points for _, points in self.factors)))


@dataclass(eq=False)
class LoanProduct:
    product_id: str
    name: str
    annual_rate: Decimal
    min_term_months: int
    max_term_months: int
    max_amount: Decimal

    def estimate_monthly_payment(self, principal: Decimal, months: int) -> Decimal:
        if not self.validate_term(months) or principal <= 0 or principal > self.max_amount:
            raise ValidationError("Loan amount or term is outside product limits")
        monthly_rate = self.annual_rate / Decimal("1200")
        if monthly_rate == 0:
            return principal / Decimal(months)
        factor = (Decimal("1") + monthly_rate) ** months
        return principal * monthly_rate * factor / (factor - Decimal("1"))

    def validate_term(self, months: int) -> bool:
        return self.min_term_months <= months <= self.max_term_months


@dataclass(eq=False)
class LoanApplication:
    application_id: str
    applicant: Customer
    product: LoanProduct
    requested_amount: Decimal
    term_months: int
    credit_score: CreditScore
    status: str = "pending"
    rejection_reason: str = ""

    def approve(self) -> None:
        if self.status != "pending":
            raise ValidationError("Only pending loan applications can be approved")
        if not self.product.validate_term(self.term_months) or self.requested_amount > self.product.max_amount:
            raise LoanNotApprovedError("Requested loan does not fit product conditions")
        if self.credit_score.calculate_score() < 600:
            raise LoanNotApprovedError("Credit score is too low")
        self.status = "approved"

    def reject(self, reason: str) -> None:
        if not reason.strip():
            raise ValidationError("Rejection reason cannot be empty")
        self.status = "rejected"
        self.rejection_reason = reason.strip()


@dataclass(eq=False)
class Repayment:
    repayment_id: str
    loan_id: str
    amount: Decimal
    due_date: date
    paid_on: date | None = None
    principal_paid: Decimal = Decimal("0.00")
    interest_paid: Decimal = Decimal("0.00")

    def split_payment(self, principal_due: Decimal, interest_due: Decimal) -> tuple[Decimal, Decimal]:
        if self.amount <= 0 or principal_due < 0 or interest_due < 0:
            raise InvalidAmountError("Repayment values are invalid")
        self.interest_paid = min(self.amount, interest_due)
        remaining = self.amount - self.interest_paid
        self.principal_paid = min(remaining, principal_due)
        return self.principal_paid, self.interest_paid

    def is_late(self, as_of: date | None = None) -> bool:
        comparison_date = self.paid_on or (as_of or date.today())
        return comparison_date > self.due_date


@dataclass(eq=False)
class Loan:
    loan_id: str
    borrower: Customer
    product: LoanProduct
    principal: Decimal
    annual_rate: Decimal
    term_months: int
    outstanding_balance: Decimal
    repayments: list[Repayment] = field(default_factory=list)
    status: str = "active"

    def calculate_payment(self) -> Decimal:
        product = LoanProduct(
            self.product.product_id,
            self.product.name,
            self.annual_rate,
            self.product.min_term_months,
            self.product.max_term_months,
            self.product.max_amount,
        )
        return product.estimate_monthly_payment(self.principal, self.term_months)

    def register_repayment(self, repayment: Repayment) -> Decimal:
        if self.status != "active":
            raise ValidationError("Loan is not active")
        if repayment.loan_id != self.loan_id:
            raise ValidationError("Repayment belongs to another loan")
        principal_paid = repayment.principal_paid
        if principal_paid == 0 and repayment.interest_paid == 0:
            principal_paid = repayment.amount
        if repayment.amount <= 0 or principal_paid < 0 or principal_paid > self.outstanding_balance:
            raise InsufficientFundsError("Repayment exceeds outstanding principal or is invalid")
        self.outstanding_balance -= principal_paid
        self.repayments.append(repayment)
        if self.outstanding_balance == 0:
            self.status = "repaid"
        return self.outstanding_balance

    def mark_defaulted(self) -> None:
        if self.status != "active" or self.outstanding_balance <= 0:
            raise ValidationError("Only an active loan with outstanding balance can default")
        self.status = "defaulted"
