from datetime import datetime
from decimal import Decimal

import pytest

from banking import AuditRecord, Employee, FraudAlert, Notification, ValidationError


def test_fraud_alert_escalation_and_resolution(account):
    alert = FraudAlert("FA-1", account, "Unusual transfer", "low", datetime.now())
    assert alert.escalate() == "medium"
    assert alert.escalate() == "high"
    assert alert.escalate() == "critical"
    assert alert.escalate() == "critical"
    employee = Employee("E-1", "Investigator")
    alert.resolve(employee)
    assert alert.is_resolved is True
    assert alert.assigned_employee is employee
    alert.severity = "unknown"
    with pytest.raises(ValidationError):
        alert.escalate()


def test_audit_record_description_and_review():
    timestamp = datetime(2026, 1, 1, 10, 0)
    record = AuditRecord("AR-1", "E-1", "deposit", "Account", timestamp)
    assert "deposit" in record.describe()
    record.mark_reviewed()
    assert record.is_reviewed is True


def test_notification_lifecycle(customer):
    notification = Notification("N-1", customer, "Payment received", "push")
    assert notification.render() == "[push] Payment received"
    with pytest.raises(ValidationError):
        notification.mark_read()
    notification.mark_sent(datetime(2026, 1, 1, 10, 0))
    assert notification.is_sent is True
    notification.mark_read()
    assert notification.is_read is True
    empty = Notification("N-2", customer, " ", "email")
    with pytest.raises(ValidationError):
        empty.mark_sent()
    unsupported = Notification("N-3", customer, "Hello", "fax")
    with pytest.raises(ValidationError):
        unsupported.mark_sent()
