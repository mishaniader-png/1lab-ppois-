"""Bank, branch, department, and employee models."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from .accounts import Account
from .exceptions import AccountNotFoundError, CustomerNotFoundError, ValidationError
from .people import Address, Customer


@dataclass(eq=False)
class Bank:
    bank_id: str
    name: str
    branches: list[Branch] = field(default_factory=list)
    license_number: str = ""
    customers: list[Customer] = field(default_factory=list)
    accounts: list[Account] = field(default_factory=list)

    def add_branch(self, branch: Branch) -> None:
        if any(item.branch_id == branch.branch_id for item in self.branches):
            raise ValidationError("Branch already belongs to this bank")
        self.branches.append(branch)

    def find_branch(self, branch_id: str) -> Branch:
        for branch in self.branches:
            if branch.branch_id == branch_id:
                return branch
        raise ValidationError("Branch was not found")

    def add_customer(self, customer: Customer) -> None:
        if any(item.customer_id == customer.customer_id for item in self.customers):
            raise ValidationError("Customer already belongs to this bank")
        self.customers.append(customer)

    def find_customer(self, customer_id: str) -> Customer:
        for customer in self.customers:
            if customer.customer_id == customer_id:
                return customer
        raise CustomerNotFoundError("Customer was not found")

    def add_account(self, account: Account) -> None:
        if any(item.account_number == account.account_number for item in self.accounts):
            raise ValidationError("Account already belongs to this bank")
        self.accounts.append(account)

    def find_account(self, account_number: str) -> Account:
        for account in self.accounts:
            if account.account_number == account_number:
                return account
        raise AccountNotFoundError("Account was not found")


@dataclass(eq=False)
class Branch:
    branch_id: str
    name: str
    address: Address
    employees: list[Employee] = field(default_factory=list)
    is_open: bool = True

    def add_employee(self, employee: Employee) -> None:
        if any(item.employee_id == employee.employee_id for item in self.employees):
            raise ValidationError("Employee is already assigned to this branch")
        self.employees.append(employee)

    def find_employee(self, employee_id: str) -> Employee:
        for employee in self.employees:
            if employee.employee_id == employee_id:
                return employee
        raise ValidationError("Employee was not found in this branch")

    def is_operational(self) -> bool:
        return self.is_open and any(employee.is_active for employee in self.employees)


@dataclass(eq=False)
class Department:
    department_id: str
    name: str
    employees: list[Employee] = field(default_factory=list)
    budget: Decimal = Decimal("0.00")

    def add_employee(self, employee: Employee) -> None:
        if all(item.employee_id != employee.employee_id for item in self.employees):
            self.employees.append(employee)

    def total_payroll(self) -> Decimal:
        return sum((employee.salary for employee in self.employees if employee.is_active), Decimal("0.00"))


@dataclass(eq=False)
class Employee:
    employee_id: str
    full_name: str
    department: Department | None = None
    salary: Decimal = Decimal("0.00")
    is_active: bool = True

    def change_department(self, department: Department) -> None:
        self.department = department
        department.add_employee(self)

    def give_raise(self, percentage: Decimal) -> Decimal:
        if percentage <= 0:
            raise ValidationError("Raise percentage must be positive")
        self.salary += self.salary * percentage / Decimal("100")
        return self.salary


@dataclass(eq=False)
class Teller(Employee):
    branch: Branch | None = None
    daily_cash_limit: Decimal = Decimal("5000.00")
    cash_processed: Decimal = Decimal("0.00")

    def process_cash_deposit(self, account: Account, amount: Decimal) -> Decimal:
        if amount <= 0 or self.cash_processed + amount > self.daily_cash_limit:
            raise ValidationError("Cash deposit exceeds teller limits")
        account.deposit(amount)
        self.cash_processed += amount
        return account.balance

    def process_cash_withdrawal(self, account: Account, amount: Decimal) -> Decimal:
        if amount <= 0 or self.cash_processed + amount > self.daily_cash_limit:
            raise ValidationError("Cash withdrawal exceeds teller limits")
        account.withdraw(amount)
        self.cash_processed += amount
        return account.balance


@dataclass(eq=False)
class Manager(Employee):
    branch: Branch | None = None
    approval_limit: Decimal = Decimal("10000.00")
    managed_employees: list[Employee] = field(default_factory=list)

    def approve_operation(self, amount: Decimal) -> bool:
        return self.is_active and Decimal("0") < amount <= self.approval_limit

    def calculate_branch_target(self) -> Decimal:
        if self.branch is None:
            return Decimal("0.00")
        payroll = sum((employee.salary for employee in self.branch.employees), Decimal("0.00"))
        return payroll * Decimal("1.10")


@dataclass(eq=False)
class SupportAgent(Employee):
    department: Department | None = None
    open_tickets: list[str] = field(default_factory=list)
    resolved_tickets: int = 0

    def assign_ticket(self, ticket_id: str) -> None:
        if not ticket_id.strip() or ticket_id in self.open_tickets:
            raise ValidationError("Ticket ID is empty or already assigned")
        self.open_tickets.append(ticket_id)

    def close_ticket(self, ticket_id: str) -> None:
        if ticket_id not in self.open_tickets:
            raise ValidationError("Ticket is not assigned to this agent")
        self.open_tickets.remove(ticket_id)
        self.resolved_tickets += 1
