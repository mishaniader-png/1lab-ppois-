from decimal import Decimal

import pytest

from banking import (
    AccountNotFoundError,
    Address,
    Bank,
    Branch,
    CustomerNotFoundError,
    Department,
    Employee,
    Manager,
    SupportAgent,
    Teller,
    ValidationError,
)


def test_bank_add_and_find_branch():
    bank = Bank("B-1", "Example Bank")
    branch = Branch("BR-1", "Central", Address("Main 1", "Minsk", "220000"))
    bank.add_branch(branch)
    assert bank.find_branch("BR-1") is branch
    with pytest.raises(ValidationError):
        bank.add_branch(branch)
    with pytest.raises(ValidationError):
        bank.find_branch("missing")


def test_branch_employee_management():
    branch = Branch("BR-1", "Central", Address("Main 1", "Minsk", "220000"))
    department = Department("D-1", "Cash")
    employee = Employee("E-1", "Bob", department, Decimal("1000"))
    branch.add_employee(employee)
    assert branch.find_employee("E-1") is employee
    with pytest.raises(ValidationError):
        branch.add_employee(employee)
    with pytest.raises(ValidationError):
        branch.find_employee("missing")


def test_department_members_and_payroll():
    department = Department("D-1", "Cash")
    active = Employee("E-1", "Bob", salary=Decimal("1000"))
    inactive = Employee("E-2", "Jane", salary=Decimal("500"), is_active=False)
    department.add_employee(active)
    department.add_employee(active)
    department.add_employee(inactive)
    assert len(department.employees) == 2
    assert department.total_payroll() == Decimal("1000")


def test_employee_department_change_and_raise():
    first = Department("D-1", "Cash")
    second = Department("D-2", "Loans")
    employee = Employee("E-1", "Bob", first, Decimal("1000"))
    employee.change_department(second)
    assert employee.department is second
    assert employee in second.employees
    assert employee.give_raise(Decimal("10")) == Decimal("1100")
    with pytest.raises(ValidationError):
        employee.give_raise(Decimal("0"))


def test_teller_cash_operations(account):
    teller = Teller("T-1", "Teller", daily_cash_limit=Decimal("500"))
    assert teller.process_cash_deposit(account, Decimal("100")) == Decimal("1100")
    assert teller.process_cash_withdrawal(account, Decimal("100")) == Decimal("1000")
    with pytest.raises(ValidationError):
        teller.process_cash_deposit(account, Decimal("400"))
    with pytest.raises(ValidationError):
        teller.process_cash_withdrawal(account, Decimal("0"))


def test_manager_approval_and_branch_target():
    manager = Manager("M-1", "Manager", salary=Decimal("2000"), approval_limit=Decimal("5000"))
    assert manager.approve_operation(Decimal("4000")) is True
    assert manager.approve_operation(Decimal("6000")) is False
    assert manager.calculate_branch_target() == Decimal("0.00")
    branch = Branch("BR-1", "Central", Address("Main 1", "Minsk", "220000"))
    branch.add_employee(Employee("E-1", "Bob", salary=Decimal("1000")))
    manager.branch = branch
    assert manager.calculate_branch_target() == Decimal("1100.000")


def test_support_agent_ticket_lifecycle():
    agent = SupportAgent("S-1", "Support")
    agent.assign_ticket("TICKET-1")
    assert agent.open_tickets == ["TICKET-1"]
    agent.close_ticket("TICKET-1")
    assert agent.resolved_tickets == 1
    with pytest.raises(ValidationError):
        agent.assign_ticket(" ")
    with pytest.raises(ValidationError):
        agent.assign_ticket("TICKET-2")
        agent.assign_ticket("TICKET-2")
    with pytest.raises(ValidationError):
        agent.close_ticket("missing")


def test_branch_operational_state():
    branch = Branch("BR-1", "Central", Address("Main 1", "Minsk", "220000"))
    assert branch.is_operational() is False
    inactive = Employee("E-1", "Inactive", is_active=False)
    branch.add_employee(inactive)
    assert branch.is_operational() is False
    active = Employee("E-2", "Active")
    branch.add_employee(active)
    assert branch.is_operational() is True
    branch.is_open = False
    assert branch.is_operational() is False


def test_bank_customer_and_account_registry(customer, account):
    bank = Bank("B-1", "Example Bank")
    bank.add_customer(customer)
    assert bank.find_customer(customer.customer_id) is customer
    with pytest.raises(ValidationError):
        bank.add_customer(customer)
    with pytest.raises(CustomerNotFoundError):
        bank.find_customer("missing")

    bank.add_account(account)
    assert bank.find_account(account.account_number) is account
    with pytest.raises(ValidationError):
        bank.add_account(account)
    with pytest.raises(AccountNotFoundError):
        bank.find_account("missing")
