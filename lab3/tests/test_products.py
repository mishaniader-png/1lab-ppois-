from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from banking import (
    CurrencyExchange,
    CurrencyRateNotFoundError,
    Deposit,
    DepositProduct,
    ExchangeRate,
    Fee,
    InterestRate,
    InvalidAmountError,
    ValidationError,
)


def test_interest_rate_calculations():
    rate = InterestRate("BYN", Decimal("12"), date(2026, 1, 1))
    assert rate.annual_to_monthly() == Decimal("1")
    assert rate.apply_to(Decimal("1000"), 365) == Decimal("120.00")
    with pytest.raises(ValidationError):
        rate.apply_to(Decimal("-1"), 30)
    with pytest.raises(ValidationError):
        rate.apply_to(Decimal("100"), -1)


def test_deposit_product_estimation():
    rate = InterestRate("BYN", Decimal("10"), date(2026, 1, 1))
    product = DepositProduct("DP-1", "One year", Decimal("100"), rate, 365)
    assert product.estimate_return(Decimal("1000")) == Decimal("1100.0")
    assert product.is_available_for(Decimal("100")) is True
    assert product.is_available_for(Decimal("50")) is False
    with pytest.raises(ValidationError):
        product.estimate_return(Decimal("50"))
    product.term_days = 0
    assert product.is_available_for(Decimal("100")) is False


def test_deposit_accrual_and_closing(customer):
    from banking import Account

    account = Account("A-1", customer, Decimal("2000"), "BYN")
    rate = InterestRate("BYN", Decimal("10"), date(2026, 1, 1))
    product = DepositProduct("DP-1", "One year", Decimal("100"), rate, 365)
    deposit = Deposit("D-1", account, product, Decimal("1000"), date(2026, 1, 1), date(2026, 12, 31))
    with pytest.raises(ValidationError):
        deposit.accrue_interest(date(2026, 7, 1))
    assert deposit.fund() == Decimal("1000")
    assert account.balance == Decimal("1000")
    with pytest.raises(ValidationError):
        deposit.fund()
    assert deposit.accrue_interest(date(2026, 7, 1)) > 0
    with pytest.raises(ValidationError):
        deposit.accrue_interest(date(2025, 12, 31))
    with pytest.raises(ValidationError):
        deposit.close(date(2026, 6, 1))
    payout = deposit.close(date(2027, 1, 1))
    assert payout == Decimal("1100.0")
    assert account.balance == Decimal("2100.0")
    with pytest.raises(ValidationError):
        deposit.close(date(2027, 1, 2))


def test_fee_calculation_and_waiver():
    fee = Fee("F-1", "Transfer fee", Decimal("1"), Decimal("2"))
    assert fee.calculate(Decimal("100")) == Decimal("3")
    fee.waive()
    assert fee.calculate(Decimal("100")) == Decimal("0.00")
    with pytest.raises(InvalidAmountError):
        fee.calculate(Decimal("-1"))


def test_exchange_rate_conversion_and_inversion():
    rate = ExchangeRate("EUR", "BYN", Decimal("3.5"), datetime.now())
    assert rate.convert(Decimal("10")) == Decimal("35.0")
    inverse = rate.invert()
    assert inverse.base_currency == "BYN"
    assert inverse.quote_currency == "EUR"
    assert inverse.rate == Decimal("1") / Decimal("3.5")
    with pytest.raises(InvalidAmountError):
        rate.convert(Decimal("0"))
    rate.rate = Decimal("0")
    with pytest.raises(CurrencyRateNotFoundError):
        rate.convert(Decimal("1"))
    with pytest.raises(CurrencyRateNotFoundError):
        rate.invert()


def test_currency_exchange_execution(customer):
    from banking import Account

    source = Account("A-1", customer, Decimal("100"), "EUR")
    target = Account("A-2", customer, Decimal("0"), "BYN")
    rate = ExchangeRate("EUR", "BYN", Decimal("3.5"), datetime.now())
    exchange = CurrencyExchange("FX-1", source, target, Decimal("10"), rate)
    assert exchange.quote() == Decimal("35.0")
    assert exchange.execute() == Decimal("35.0")
    assert source.balance == Decimal("90")
    assert target.balance == Decimal("35.0")
    with pytest.raises(ValidationError):
        exchange.execute()
    bad_target = Account("A-3", customer, Decimal("0"), "USD")
    bad_exchange = CurrencyExchange("FX-2", source, bad_target, Decimal("1"), rate)
    with pytest.raises(ValidationError):
        bad_exchange.execute()


def test_currency_exchange_rejects_wrong_source_currency(customer):
    from banking import Account

    source = Account("A-1", customer, Decimal("100"), "USD")
    target = Account("A-2", customer, Decimal("0"), "BYN")
    rate = ExchangeRate("EUR", "BYN", Decimal("3.5"), datetime.now())
    exchange = CurrencyExchange("FX-3", source, target, Decimal("10"), rate)
    with pytest.raises(ValidationError):
        exchange.execute()


def test_deposit_requires_positive_principal_and_funding(customer):
    from banking import Account

    account = Account("A-1", customer, Decimal("100"), "BYN")
    rate = InterestRate("BYN", Decimal("5"), date(2026, 1, 1))
    product = DepositProduct("DP-1", "Short", Decimal("1"), rate, 30)
    zero_principal = Deposit("D-ZERO", account, product, Decimal("0"), date(2026, 1, 1), date(2026, 1, 31))
    with pytest.raises(InvalidAmountError):
        zero_principal.fund()
    unfunded = Deposit("D-UNFUNDED", account, product, Decimal("10"), date(2026, 1, 1), date(2026, 1, 31))
    with pytest.raises(ValidationError):
        unfunded.close(date(2026, 2, 1))
