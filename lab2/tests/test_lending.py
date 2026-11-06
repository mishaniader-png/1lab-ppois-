from datetime import date, timedelta
from decimal import Decimal

import pytest

from banking import (
    CreditScore,
    Loan,
    LoanApplication,
    LoanNotApprovedError,
    LoanProduct,
    Repayment,
    ValidationError,
    InvalidAmountError,
    InsufficientFundsError,
)


def test_credit_score_factors_and_bounds():
    score = CreditScore("C-1", 600)
    score.add_factor("stable income", 50)
    assert score.calculate_score() == 650
    score.add_factor("missed payments", -500)
    assert score.calculate_score() == 300
    score.base_score = 900
    score.factors.clear()
    assert score.calculate_score() == 850
    with pytest.raises(ValidationError):
        score.add_factor(" ", 10)


def test_loan_product_terms_and_payment_estimate():
    product = LoanProduct("LP-1", "Consumer loan", Decimal("12"), 6, 60, Decimal("10000"))
    assert product.validate_term(12) is True
    assert product.validate_term(2) is False
    assert product.estimate_monthly_payment(Decimal("1200"), 12) > 100
    zero_rate = LoanProduct("LP-2", "Zero", Decimal("0"), 1, 12, Decimal("1000"))
    assert zero_rate.estimate_monthly_payment(Decimal("120"), 12) == Decimal("10")
    with pytest.raises(ValidationError):
        product.estimate_monthly_payment(Decimal("20000"), 12)
    with pytest.raises(ValidationError):
        product.estimate_monthly_payment(Decimal("100"), 2)


def test_loan_application_approval_and_rejection(customer):
    product = LoanProduct("LP-1", "Consumer loan", Decimal("12"), 6, 60, Decimal("10000"))
    score = CreditScore(customer.customer_id, 700)
    application = LoanApplication("LA-1", customer, product, Decimal("5000"), 12, score)
    application.approve()
    assert application.status == "approved"
    with pytest.raises(ValidationError):
        application.approve()
    low_score = LoanApplication("LA-2", customer, product, Decimal("5000"), 12, CreditScore(customer.customer_id, 500))
    with pytest.raises(LoanNotApprovedError):
        low_score.approve()
    too_large = LoanApplication("LA-3", customer, product, Decimal("20000"), 12, score)
    with pytest.raises(LoanNotApprovedError):
        too_large.approve()
    rejected = LoanApplication("LA-4", customer, product, Decimal("100"), 12, score)
    rejected.reject("Incomplete documents")
    assert rejected.status == "rejected"
    with pytest.raises(ValidationError):
        rejected.reject(" ")


def test_repayment_split_and_lateness():
    due = date(2026, 5, 1)
    repayment = Repayment("R-1", "L-1", Decimal("120"), due)
    assert repayment.split_payment(Decimal("100"), Decimal("20")) == (Decimal("100"), Decimal("20"))
    assert repayment.is_late(date(2026, 5, 2)) is True
    repayment.paid_on = date(2026, 5, 1)
    assert repayment.is_late(date(2026, 6, 1)) is False
    with pytest.raises(InvalidAmountError):
        Repayment("R-2", "L-1", Decimal("0"), due).split_payment(Decimal("10"), Decimal("1"))
    with pytest.raises(InvalidAmountError):
        repayment.split_payment(Decimal("-1"), Decimal("1"))


def test_loan_payment_and_repayment_registration(customer):
    product = LoanProduct("LP-1", "Consumer loan", Decimal("0"), 1, 24, Decimal("10000"))
    loan = Loan("L-1", customer, product, Decimal("1200"), Decimal("0"), 12, Decimal("1200"))
    assert loan.calculate_payment() == Decimal("100")
    repayment = Repayment("R-1", "L-1", Decimal("300"), date.today(), principal_paid=Decimal("300"))
    assert loan.register_repayment(repayment) == Decimal("900")
    assert loan.repayments == [repayment]
    wrong = Repayment("R-2", "OTHER", Decimal("100"), date.today())
    with pytest.raises(ValidationError):
        loan.register_repayment(wrong)
    too_large = Repayment("R-3", "L-1", Decimal("1000"), date.today(), principal_paid=Decimal("1000"))
    with pytest.raises(InsufficientFundsError):
        loan.register_repayment(too_large)
    loan.register_repayment(Repayment("R-4", "L-1", Decimal("900"), date.today(), principal_paid=Decimal("900")))
    assert loan.status == "repaid"
    with pytest.raises(ValidationError):
        loan.register_repayment(Repayment("R-5", "L-1", Decimal("1"), date.today()))


def test_loan_can_be_marked_defaulted(customer):
    product = LoanProduct("LP-1", "Consumer", Decimal("0"), 1, 24, Decimal("10000"))
    loan = Loan("L-DEFAULT", customer, product, Decimal("500"), Decimal("0"), 12, Decimal("500"))
    loan.mark_defaulted()
    assert loan.status == "defaulted"
    with pytest.raises(ValidationError):
        loan.mark_defaulted()
    repaid = Loan("L-REPAID", customer, product, Decimal("500"), Decimal("0"), 12, Decimal("0"), status="repaid")
    with pytest.raises(ValidationError):
        repaid.mark_defaulted()


def test_loan_repayment_defaults_to_principal_when_not_split(customer):
    product = LoanProduct("LP-1", "Consumer", Decimal("0"), 1, 24, Decimal("10000"))
    loan = Loan("L-DEFAULT-REPAY", customer, product, Decimal("500"), Decimal("0"), 12, Decimal("500"))
    repayment = Repayment("R-1", loan.loan_id, Decimal("100"), date.today())
    assert loan.register_repayment(repayment) == Decimal("400")
