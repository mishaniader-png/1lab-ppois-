from datetime import date
from decimal import Decimal

import pytest

from banking import Account, ContactInfo, Customer


@pytest.fixture
def customer() -> Customer:
    return Customer("C-001", "Alice Smith", ContactInfo("alice@example.com", "+375291234567"))


@pytest.fixture
def account(customer: Customer) -> Account:
    return Account("BY00-001", customer, Decimal("1000.00"), "BYN", True, date(2026, 1, 1))
