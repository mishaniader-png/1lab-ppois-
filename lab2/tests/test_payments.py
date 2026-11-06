from datetime import date, timedelta
from decimal import Decimal

import pytest

from banking import (
    DirectDebit,
    DomesticTransfer,
    InternationalTransfer,
    Payment,
    StandingOrder,
    Transfer,
    TransferRejectedError,
    ValidationError,
    InvalidAmountError,
)


def test_transfer_validation_and_execution(customer):
    from banking import Account

    source = Account("A-1", customer, Decimal("500"), "BYN")
    destination = Account("A-2", customer, Decimal("100"), "BYN")
    transfer = Transfer("TR-1", source, destination, Decimal("100"))
    assert transfer.validate() is True
    assert transfer.execute() == "completed"
    assert source.balance == Decimal("400")
    assert destination.balance == Decimal("200")
    with pytest.raises(TransferRejectedError):
        transfer.execute()
    with pytest.raises(TransferRejectedError):
        Transfer("TR-2", source, source, Decimal("1")).validate()
    with pytest.raises(TransferRejectedError):
        Transfer("TR-3", source, Account("A-3", customer, currency="USD"), Decimal("1")).validate()
    closed = Account("A-4", customer, Decimal("0"), "BYN", False)
    with pytest.raises(TransferRejectedError):
        Transfer("TR-4", source, closed, Decimal("1")).validate()
    with pytest.raises(InvalidAmountError):
        Transfer("TR-5", source, destination, Decimal("0")).validate()


def test_domestic_transfer_fee_and_execution(customer):
    from banking import Account

    source = Account("A-1", customer, Decimal("500"), "BYN")
    destination = Account("A-2", customer, Decimal("0"), "BYN")
    transfer = DomesticTransfer("D-1", source, destination, Decimal("100"), fee_rate=Decimal("2"))
    assert transfer.calculate_fee() == Decimal("2")
    assert transfer.execute_domestic() == "completed"
    assert source.balance == Decimal("398")
    assert destination.balance == Decimal("100")
    expensive = DomesticTransfer("D-2", source, destination, Decimal("500"), fee_rate=Decimal("10"))
    with pytest.raises(Exception):
        expensive.execute_domestic()


def test_international_transfer_fee_and_conversion(customer):
    from banking import Account

    source = Account("A-1", customer, Decimal("1000"), "BYN")
    destination = Account("A-2", customer, Decimal("0"), "EUR")
    transfer = InternationalTransfer(
        "I-1",
        source,
        destination,
        Decimal("100"),
        destination_country="DE",
        swift_code="SWIFT",
        exchange_rate=Decimal("3.2"),
    )
    assert transfer.calculate_fee() == Decimal("12.00")
    assert transfer.converted_amount() == Decimal("320.0")
    transfer.exchange_rate = Decimal("0")
    with pytest.raises(ValidationError):
        transfer.converted_amount()


def test_payment_lifecycle(account):
    payment = Payment("P-1", account, "Utility company", Decimal("100"))
    payment.mark_paid()
    assert payment.status == "paid"
    assert account.balance == Decimal("900")
    with pytest.raises(TransferRejectedError):
        payment.cancel()
    cancelled = Payment("P-2", account, "Phone", Decimal("10"))
    cancelled.cancel()
    assert cancelled.status == "cancelled"
    with pytest.raises(TransferRejectedError):
        cancelled.mark_paid()


def test_standing_order_schedule(customer):
    from banking import Account

    source = Account("A-1", customer, Decimal("500"), "BYN")
    destination = Account("A-2", customer, Decimal("0"), "BYN")
    due_date = date(2026, 1, 10)
    order = StandingOrder("SO-1", source, destination, Decimal("50"), 30, due_date)
    assert order.should_execute(date(2026, 1, 9)) is False
    assert order.record_execution(due_date) == "completed"
    assert order.next_execution == date(2026, 2, 9)
    with pytest.raises(ValidationError):
        order.record_execution(date(2026, 1, 20))
    order.interval_days = 0
    order.next_execution = date(2026, 1, 1)
    with pytest.raises(ValidationError):
        order.record_execution(date(2026, 1, 10))
    order.is_active = False
    assert order.should_execute(date(2027, 1, 1)) is False


def test_direct_debit_authorization_and_collection(account):
    mandate = DirectDebit("DD-1", account, "Utility company", Decimal("200"))
    with pytest.raises(TransferRejectedError):
        mandate.collect(Decimal("20"))
    mandate.authorize()
    assert mandate.collect(Decimal("50")) == Decimal("950")
    with pytest.raises(InvalidAmountError):
        mandate.collect(Decimal("300"))
    with pytest.raises(InvalidAmountError):
        mandate.collect(Decimal("0"))


def test_transfer_cancellation(customer):
    from banking import Account

    source = Account("A-1", customer, Decimal("100"), "BYN")
    destination = Account("A-2", customer, Decimal("0"), "BYN")
    transfer = Transfer("TR-C", source, destination, Decimal("10"))
    transfer.cancel()
    assert transfer.status == "cancelled"
    with pytest.raises(TransferRejectedError):
        transfer.cancel()


def test_domestic_transfer_cannot_execute_twice(customer):
    from banking import Account

    source = Account("A-1", customer, Decimal("100"), "BYN")
    destination = Account("A-2", customer, Decimal("0"), "BYN")
    transfer = DomesticTransfer("D-1", source, destination, Decimal("10"))
    transfer.execute_domestic()
    with pytest.raises(TransferRejectedError):
        transfer.execute_domestic()
