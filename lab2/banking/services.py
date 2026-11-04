"""Fraud, audit, and customer notification models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .accounts import Account
from .exceptions import ValidationError
from .organization import Employee
from .people import Customer


@dataclass(eq=False)
class FraudAlert:
    alert_id: str
    account: Account
    reason: str
    severity: str
    created_at: datetime
    is_resolved: bool = False
    assigned_employee: Employee | None = None

    def escalate(self) -> str:
        levels = ["low", "medium", "high", "critical"]
        if self.severity not in levels:
            raise ValidationError("Unknown fraud alert severity")
        index = levels.index(self.severity)
        self.severity = levels[min(index + 1, len(levels) - 1)]
        return self.severity

    def resolve(self, employee: Employee) -> None:
        self.assigned_employee = employee
        self.is_resolved = True


@dataclass(eq=False)
class AuditRecord:
    record_id: str
    actor_id: str
    action: str
    entity_type: str
    created_at: datetime
    is_reviewed: bool = False

    def describe(self) -> str:
        return f"{self.created_at.isoformat()} | {self.actor_id} | {self.action} | {self.entity_type}"

    def mark_reviewed(self) -> None:
        self.is_reviewed = True


@dataclass(eq=False)
class Notification:
    notification_id: str
    customer: Customer
    message: str
    channel: str
    is_sent: bool = False
    is_read: bool = False
    sent_at: datetime | None = None

    def mark_sent(self, sent_at: datetime | None = None) -> None:
        if not self.message.strip():
            raise ValidationError("Notification message cannot be empty")
        if self.channel not in {"email", "sms", "push"}:
            raise ValidationError("Unsupported notification channel")
        self.is_sent = True
        self.sent_at = sent_at or datetime.now()

    def mark_read(self) -> None:
        if not self.is_sent:
            raise ValidationError("Unsent notification cannot be marked as read")
        self.is_read = True

    def render(self) -> str:
        return f"[{self.channel}] {self.message}"
