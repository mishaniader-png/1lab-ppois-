from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from banking import (
    Address,
    BusinessCustomer,
    ContactInfo,
    Customer,
    CustomerProfile,
    CustomerSegment,
    IdentificationDocument,
    IdentityVerification,
    IndividualCustomer,
    LoyaltyAccount,
    ValidationError,
    InvalidAmountError,
)


def test_address_format_and_city_comparison():
    address = Address("Lenina 1", "Minsk", "220000")
    assert address.format() == "Lenina 1, Minsk, 220000, Belarus"
    assert address.is_in_city(" minsk ") is True
    assert address.is_in_city("Brest") is False


def test_contact_validation_and_channel_selection():
    contact = ContactInfo("person@example.com", "+375291234567")
    assert contact.is_valid() is True
    assert ContactInfo("bad-email", "12").is_valid() is False
    contact.choose_channel("sms")
    assert contact.preferred_channel == "sms"
    with pytest.raises(ValidationError):
        contact.choose_channel("telegram")


def test_customer_contact_update_and_deactivation(customer):
    new_contact = ContactInfo("new@example.com", "+375291111111")
    customer.update_contact(new_contact)
    assert customer.contact is new_contact
    with pytest.raises(ValidationError):
        customer.update_contact(ContactInfo("bad", "1"))
    customer.deactivate()
    assert customer.is_active is False


def test_individual_customer_age_and_tax_id(customer):
    person = IndividualCustomer(
        customer.customer_id,
        customer.full_name,
        customer.contact,
        True,
        date(2000, 5, 10),
        "123456789",
        "standard",
    )
    assert person.is_adult(date(2026, 5, 10)) is True
    assert person.is_adult(date(2017, 5, 9)) is False
    person.update_tax_id("987654321")
    assert person.tax_id == "987654321"
    with pytest.raises(ValidationError):
        person.update_tax_id("  ")


def test_business_customer_industry_and_registration(customer):
    company = BusinessCustomer(
        customer.customer_id,
        customer.full_name,
        customer.contact,
        True,
        "ACME LLC",
        "REG-123",
        "retail",
    )
    assert company.is_registered() is True
    company.update_industry("IT")
    assert company.industry == "IT"
    with pytest.raises(ValidationError):
        company.update_industry(" ")
    company.registration_number = ""
    assert company.is_registered() is False


def test_identification_document_expiry_and_renewal():
    document = IdentificationDocument("passport", "AB123", date(2025, 1, 1), "MVD")
    assert document.is_expired(date(2026, 1, 1)) is True
    assert document.is_expired(date(2024, 1, 1)) is False
    document.renew(date.today() + timedelta(days=365), "New issuer")
    assert document.issuer == "New issuer"
    with pytest.raises(ValidationError):
        document.renew(date.today() - timedelta(days=1))
    with pytest.raises(ValidationError):
        document.renew(date.today() + timedelta(days=1), " ")


def test_identity_verification_approval_and_rejection():
    valid_document = IdentificationDocument("passport", "AB123", date.today() + timedelta(days=100), "MVD")
    verification = IdentityVerification("C-1", valid_document)
    checked_at = datetime.now()
    verification.approve(checked_at)
    assert verification.verified is True
    assert verification.checked_at == checked_at
    verification.reject(checked_at)
    assert verification.verified is False
    expired = IdentificationDocument("passport", "OLD", date.today() - timedelta(days=1), "MVD")
    with pytest.raises(ValidationError):
        IdentityVerification("C-2", expired).approve()


def test_customer_profile_notes_and_segment_assignment(customer):
    profile = CustomerProfile(customer)
    profile.add_note("VIP candidate")
    assert profile.notes == ["VIP candidate"]
    with pytest.raises(ValidationError):
        profile.add_note(" ")
    segment = CustomerSegment("Gold", Decimal("500"), Decimal("2.5"), "Gold customers")
    profile.assign_segment(segment)
    assert profile.segment is segment


def test_customer_segment_qualification_and_cashback():
    segment = CustomerSegment("Gold", Decimal("500"), Decimal("2.5"), "Gold customers")
    assert segment.qualifies(Decimal("700")) is True
    assert segment.qualifies(Decimal("300")) is False
    assert segment.cashback_for(Decimal("200")) == Decimal("5.00")
    with pytest.raises(InvalidAmountError):
        segment.cashback_for(Decimal("0"))


def test_loyalty_points_earn_and_redeem():
    loyalty = LoyaltyAccount("C-1")
    assert loyalty.earn_points(Decimal("125")) == 12
    assert loyalty.points == 12
    loyalty.redeem_points(5)
    assert loyalty.points == 7
    with pytest.raises(ValidationError):
        loyalty.redeem_points(0)
    with pytest.raises(ValidationError):
        loyalty.redeem_points(100)
    with pytest.raises(InvalidAmountError):
        loyalty.earn_points(Decimal("-1"))


def test_customer_digital_service_eligibility(customer):
    assert customer.can_use_digital_services() is True
    customer.contact = ContactInfo("bad", "1")
    assert customer.can_use_digital_services() is False
    customer.is_active = False
    assert customer.can_use_digital_services() is False


def test_document_renewal_without_changing_issuer():
    document = IdentificationDocument("passport", "AB123", date(2025, 1, 1), "MVD")
    document.renew(date.today() + timedelta(days=30))
    assert document.issuer == "MVD"
