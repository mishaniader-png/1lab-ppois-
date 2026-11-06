from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from banking import (
    Card,
    CardBlockedError,
    CardExpiredError,
    CardTransaction,
    CreditCard,
    DebitCard,
    InsufficientFundsError,
    InvalidAmountError,
    Merchant,
    PaymentTerminal,
    ValidationError,
    Address,
)


def test_merchant_category_and_risk():
    merchant = Merchant("M-1", "Lucky", "retail", "BY")
    assert merchant.is_high_risk() is False
    merchant.update_category("gambling")
    assert merchant.is_high_risk() is True
    with pytest.raises(ValidationError):
        merchant.update_category(" ")


def test_card_block_and_activation(account):
    card = Card("4111", account, account.owner, date.today() + timedelta(days=30))
    card.block()
    assert card.is_blocked is True
    card.activate()
    assert card.is_blocked is False
    expired = Card("4222", account, account.owner, date.today() - timedelta(days=1))
    with pytest.raises(CardExpiredError):
        expired.activate()


def test_debit_card_payment_and_limits(account):
    card = DebitCard("4111", account, account.owner, date.today() + timedelta(days=30), daily_limit=Decimal("200"))
    assert card.can_pay(Decimal("100")) is True
    assert card.record_payment(Decimal("100")) == Decimal("100")
    assert card.can_pay(Decimal("150")) is False
    with pytest.raises(InsufficientFundsError):
        card.record_payment(Decimal("150"))
    card.block()
    with pytest.raises(CardBlockedError):
        card.record_payment(Decimal("10"))
    card.activate()
    with pytest.raises(InvalidAmountError):
        card.record_payment(Decimal("0"))
    expired = DebitCard("4333", account, account.owner, date.today() - timedelta(days=1))
    with pytest.raises(CardExpiredError):
        expired.record_payment(Decimal("1"))
    assert expired.can_pay(Decimal("1")) is False


def test_credit_card_purchase_and_available_credit(account):
    card = CreditCard("5555", account, account.owner, date.today() + timedelta(days=30), credit_limit=Decimal("500"))
    assert card.available_credit() == Decimal("500")
    assert card.record_credit_purchase(Decimal("100")) == Decimal("100")
    assert card.available_credit() == Decimal("400")
    with pytest.raises(InsufficientFundsError):
        card.record_credit_purchase(Decimal("500"))
    with pytest.raises(InvalidAmountError):
        card.record_credit_purchase(Decimal("0"))
    card.block()
    with pytest.raises(CardBlockedError):
        card.record_credit_purchase(Decimal("1"))
    card.activate()
    expired = CreditCard("5666", account, account.owner, date.today() - timedelta(days=1), credit_limit=Decimal("100"))
    with pytest.raises(CardExpiredError):
        expired.record_credit_purchase(Decimal("1"))


def test_card_transaction_approve_and_reverse(account):
    merchant = Merchant("M-1", "Shop", "retail", "BY")
    debit = DebitCard("4111", account, account.owner, date.today() + timedelta(days=30))
    transaction = CardTransaction("TX-1", debit, merchant, Decimal("25"), datetime.now())
    transaction.approve()
    assert transaction.status == "approved"
    assert account.balance == Decimal("975")
    transaction.reverse()
    assert transaction.status == "reversed"
    assert account.balance == Decimal("1000")
    with pytest.raises(ValidationError):
        transaction.reverse()
    credit = CreditCard("5555", account, account.owner, date.today() + timedelta(days=30), credit_limit=Decimal("100"))
    credit_tx = CardTransaction("TX-2", credit, merchant, Decimal("30"), datetime.now())
    credit_tx.approve()
    credit_tx.reverse()
    assert credit.outstanding_balance == Decimal("0")
    merchant.is_blocked = True
    blocked_merchant_tx = CardTransaction("TX-3", debit, merchant, Decimal("1"), datetime.now())
    with pytest.raises(ValidationError):
        blocked_merchant_tx.approve()
    with pytest.raises(ValidationError):
        blocked_merchant_tx.approve()


def test_card_transaction_base_card_and_invalid_status(account):
    merchant = Merchant("M-1", "Shop", "retail", "BY")
    card = Card("4000", account, account.owner, date.today() + timedelta(days=10))
    transaction = CardTransaction("TX-1", card, merchant, Decimal("10"), datetime.now())
    transaction.approve()
    assert account.balance == Decimal("990")
    pending = CardTransaction("TX-2", card, merchant, Decimal("10"), datetime.now(), status="declined")
    with pytest.raises(ValidationError):
        pending.approve()


def test_payment_terminal_connection_and_processing(account):
    merchant = Merchant("M-1", "Shop", "retail", "BY")
    terminal = PaymentTerminal("POS-1", merchant, Address("Main 1", "Minsk", "220000"))
    card = DebitCard("4111", account, account.owner, date.today() + timedelta(days=30))
    with pytest.raises(ValidationError):
        terminal.process_payment(card, Decimal("10"))
    terminal.connect()
    transaction = terminal.process_payment(card, Decimal("10"))
    assert transaction.status == "approved"
    assert terminal.processed_count == 1


def test_card_usability_check(account):
    valid = Card("4111", account, account.owner, date.today() + timedelta(days=1))
    assert valid.is_usable_on() is True
    assert valid.is_usable_on(date.today() + timedelta(days=2)) is False
    valid.block()
    assert valid.is_usable_on() is False


def test_base_card_transaction_blocked_and_expired_paths(account):
    merchant = Merchant("M-1", "Shop", "retail", "BY")
    blocked = Card("4000", account, account.owner, date.today() + timedelta(days=10), is_blocked=True)
    with pytest.raises(CardBlockedError):
        CardTransaction("TX-B", blocked, merchant, Decimal("1"), datetime.now()).approve()
    expired = Card("4001", account, account.owner, date.today() - timedelta(days=1))
    with pytest.raises(CardExpiredError):
        CardTransaction("TX-E", expired, merchant, Decimal("1"), datetime.now()).approve()
