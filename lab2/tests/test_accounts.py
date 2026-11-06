from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from banking import (
    Account,
    AccountClosedError,
    AccountStatement,
    BusinessAccount,
    CurrentAccount,
    InsufficientFundsError,
    InvalidAmountError,
    JointAccount,
    SavingsAccount,
    StatementEntry,
    ValidationError,
)


def test_account_deposit_withdraw_and_close(account):
    assert account.deposit(Decimal("100")) == Decimal("1100")
    assert account.withdraw(Decimal("100")) == Decimal("1000")
    with pytest.raises(InvalidAmountError):
        account.deposit(Decimal("0"))
    with pytest.raises(InvalidAmountError):
        account.withdraw(Decimal("-1"))
    with pytest.raises(InsufficientFundsError):
        account.withdraw(Decimal("2000"))
    with pytest.raises(ValidationError):
        account.close()
    account.withdraw(Decimal("1000"))
    account.close()
    with pytest.raises(AccountClosedError):
        account.deposit(Decimal("10"))
    with pytest.raises(AccountClosedError):
        account.withdraw(Decimal("10"))


def test_current_account_fee_and_available_balance(account):
    current = CurrentAccount("CA-1", account.owner, Decimal("100"), monthly_fee=Decimal("10"), overdraft_limit=Decimal("50"))
    assert current.available_balance() == Decimal("150")
    assert current.charge_monthly_fee() == Decimal("10")
    assert current.balance == Decimal("90")
    current.monthly_fee = Decimal("200")
    with pytest.raises(InsufficientFundsError):
        current.charge_monthly_fee()


def test_savings_account_interest(account):
    savings = SavingsAccount("SA-1", account.owner, Decimal("1000"), annual_interest_rate=Decimal("12"), minimum_balance=Decimal("100"))
    assert savings.calculate_interest(365) == Decimal("108.00")
    assert savings.calculate_interest(30) == Decimal("8.876712328767123287671232877")
    assert savings.capitalize_interest(365) == Decimal("108.00")
    assert savings.balance == Decimal("1108.00")
    with pytest.raises(ValidationError):
        savings.calculate_interest(-1)
    savings.minimum_balance = Decimal("2000")
    assert savings.calculate_interest() == Decimal("0.00")


def test_business_account_overdraft(account):
    business = BusinessAccount("BA-1", account.owner, Decimal("500"), overdraft_limit=Decimal("100"), company_name="ACME")
    assert business.available_balance() == Decimal("600")
    business.set_overdraft_limit(Decimal("250"))
    assert business.available_balance() == Decimal("750")
    with pytest.raises(ValidationError):
        business.set_overdraft_limit(Decimal("-1"))


def test_joint_account_holders(customer):
    second = type(customer)("C-2", "Bob", customer.contact)
    joint = JointAccount("JA-1", customer, holders=[customer], max_holders=2)
    joint.add_holder(second)
    assert len(joint.holders) == 2
    with pytest.raises(ValidationError):
        joint.add_holder(second)
    with pytest.raises(ValidationError):
        joint.add_holder(type(customer)("C-3", "Eve", customer.contact))
    joint.remove_holder("C-2")
    assert len(joint.holders) == 1
    with pytest.raises(ValidationError):
        joint.remove_holder("missing")


def test_statement_entry_format_and_direction():
    entry = StatementEntry("E-1", datetime(2026, 1, 2, 10, 0), "Coffee", Decimal("5"), "debit")
    assert entry.is_debit() is True
    assert "-5" in entry.formatted_line()
    credit = StatementEntry("E-2", datetime(2026, 1, 3), "Salary", Decimal("100"), "credit")
    assert credit.is_debit() is False
    assert "+100" in credit.formatted_line()


def test_account_statement_entries_and_balance():
    statement = AccountStatement("A-1", date(2026, 1, 1), date(2026, 1, 31), Decimal("100"))
    credit = StatementEntry("E-1", datetime(2026, 1, 5), "Salary", Decimal("50"), "credit")
    debit = StatementEntry("E-2", datetime(2026, 1, 6), "Food", Decimal("20"), "debit")
    statement.add_entry(debit)
    statement.add_entry(credit)
    assert statement.entries[0] is credit
    assert statement.calculate_closing_balance() == Decimal("130")
    outside = StatementEntry("E-3", datetime(2026, 2, 1), "Outside", Decimal("1"), "credit")
    with pytest.raises(ValidationError):
        statement.add_entry(outside)
    invalid = StatementEntry("E-4", datetime(2026, 1, 10), "Bad", Decimal("1"), "other")
    with pytest.raises(ValidationError):
        statement.add_entry(invalid)


def test_account_sufficient_funds_check(account):
    assert account.has_sufficient_funds(Decimal("500")) is True
    assert account.has_sufficient_funds(Decimal("1500")) is False
    assert account.has_sufficient_funds(Decimal("0")) is False
    account.is_active = False
    assert account.has_sufficient_funds(Decimal("1")) is False


def test_account_statement_total_debits():
    statement = AccountStatement("A-1", date(2026, 1, 1), date(2026, 1, 31), Decimal("0"))
    statement.add_entry(StatementEntry("E-1", datetime(2026, 1, 2), "Rent", Decimal("100"), "debit"))
    statement.add_entry(StatementEntry("E-2", datetime(2026, 1, 3), "Salary", Decimal("500"), "credit"))
    statement.add_entry(StatementEntry("E-3", datetime(2026, 1, 4), "Food", Decimal("25"), "debit"))
    assert statement.total_debits() == Decimal("125")
