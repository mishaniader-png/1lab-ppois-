# Banking domain — PPOIS Lab 2

Учебная модель банковской сферы: клиенты, отделения, счета, карты, платежи,
переводы, депозиты, кредиты, валютные операции, уведомления и аудит.

## Количественные требования ЛР2

| Показатель | Реализовано | Требование |
|---|---:|---:|
| Доменные классы | 50 | не менее 50 |
| Поля, объявленные непосредственно в классах | 230 | не менее 150 |
| Содержательные методы | 114 | не менее 100 |
| Уникальные имена методов | 105 | контрольный дополнительный показатель |
| Ассоциации между классами | 42 | не менее 30 |
| Собственные классы исключений | 12 | не менее 12 |
| Unit-тесты | 65 | — |
| Покрытие тестами | 100% | более 90% |

В таблице перечислены поля, объявленные в конкретном классе. У классов-наследников
также доступны унаследованные поля базового класса; они не дублируются в колонке.
Все методы в таблице реализуют поведение предметной области, а не являются
геттерами или сеттерами.

## Каталог классов

Формат: класс | собственные поля | содержательные методы | ассоциации.

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `Address` | `street`, `city`, `postal_code`, `country` | `format()`, `is_in_city()` | — |
| `ContactInfo` | `email`, `phone`, `preferred_channel` | `is_valid()`, `choose_channel()` | — |
| `Customer` | `customer_id`, `full_name`, `contact`, `is_active` | `update_contact()`, `deactivate()`, `can_use_digital_services()` | `ContactInfo` |
| `IndividualCustomer` | `birth_date`, `tax_id`, `risk_level` | `is_adult()`, `update_tax_id()` | — |
| `BusinessCustomer` | `company_name`, `registration_number`, `industry` | `update_industry()`, `is_registered()` | — |
| `IdentificationDocument` | `document_type`, `number`, `expires_on`, `issuer` | `is_expired()`, `renew()` | — |
| `IdentityVerification` | `customer_id`, `document`, `verified`, `checked_at` | `approve()`, `reject()` | `IdentificationDocument` |
| `CustomerProfile` | `customer`, `segment`, `notes`, `created_at` | `add_note()`, `assign_segment()` | `Customer`, `CustomerSegment` |
| `CustomerSegment` | `name`, `min_balance`, `cashback_rate`, `description` | `qualifies()`, `cashback_for()` | — |
| `LoyaltyAccount` | `customer_id`, `points`, `tier`, `last_updated` | `earn_points()`, `redeem_points()` | — |
| `Bank` | `bank_id`, `name`, `branches`, `license_number`, `customers`, `accounts` | `add_branch()`, `find_branch()`, `add_customer()`, `find_customer()`, `add_account()`, `find_account()` | `Account`, `Branch`, `Customer` |
| `Branch` | `branch_id`, `name`, `address`, `employees`, `is_open` | `add_employee()`, `find_employee()`, `is_operational()` | `Address`, `Employee` |
| `Department` | `department_id`, `name`, `employees`, `budget` | `add_employee()`, `total_payroll()` | `Employee` |
| `Employee` | `employee_id`, `full_name`, `department`, `salary`, `is_active` | `change_department()`, `give_raise()` | `Department` |
| `Teller` | `branch`, `daily_cash_limit`, `cash_processed` | `process_cash_deposit()`, `process_cash_withdrawal()` | `Branch` |
| `Manager` | `branch`, `approval_limit`, `managed_employees` | `approve_operation()`, `calculate_branch_target()` | `Branch`, `Employee` |
| `SupportAgent` | `department`, `open_tickets`, `resolved_tickets` | `assign_ticket()`, `close_ticket()` | `Department` |
| `Account` | `account_number`, `owner`, `balance`, `currency`, `is_active`, `opened_at` | `deposit()`, `withdraw()`, `close()`, `has_sufficient_funds()` | `Customer` |
| `CurrentAccount` | `monthly_fee`, `overdraft_limit` | `charge_monthly_fee()`, `available_balance()` | — |
| `SavingsAccount` | `annual_interest_rate`, `minimum_balance` | `calculate_interest()`, `capitalize_interest()` | — |
| `BusinessAccount` | `overdraft_limit`, `company_name` | `set_overdraft_limit()`, `available_balance()` | — |
| `JointAccount` | `holders`, `max_holders` | `add_holder()`, `remove_holder()` | `Customer` |
| `StatementEntry` | `entry_id`, `timestamp`, `description`, `amount`, `direction`, `reference` | `is_debit()`, `formatted_line()` | — |
| `AccountStatement` | `account_number`, `period_start`, `period_end`, `opening_balance`, `entries` | `add_entry()`, `calculate_closing_balance()`, `total_debits()` | `StatementEntry` |
| `Merchant` | `merchant_id`, `name`, `category`, `country`, `is_blocked` | `update_category()`, `is_high_risk()` | — |
| `Card` | `card_number`, `account`, `holder`, `expiry_date`, `is_blocked`, `pin_hash` | `block()`, `activate()`, `is_usable_on()` | `Account`, `Customer` |
| `DebitCard` | `daily_limit`, `daily_spent` | `can_pay()`, `record_payment()` | — |
| `CreditCard` | `credit_limit`, `outstanding_balance` | `available_credit()`, `record_credit_purchase()` | — |
| `CardTransaction` | `transaction_id`, `card`, `merchant`, `amount`, `timestamp`, `status` | `approve()`, `reverse()` | `Card`, `Merchant` |
| `PaymentTerminal` | `terminal_id`, `merchant`, `address`, `is_connected`, `processed_count` | `connect()`, `process_payment()` | `Address`, `Merchant` |
| `Transfer` | `transfer_id`, `source`, `destination`, `amount`, `status`, `reference` | `validate()`, `execute()`, `cancel()` | `Account` |
| `DomesticTransfer` | `bank_code`, `fee_rate` | `calculate_fee()`, `execute_domestic()` | — |
| `InternationalTransfer` | `destination_country`, `swift_code`, `exchange_rate` | `calculate_fee()`, `converted_amount()` | — |
| `Payment` | `payment_id`, `payer`, `payee_name`, `amount`, `status`, `reference` | `mark_paid()`, `cancel()` | `Account` |
| `StandingOrder` | `order_id`, `source`, `beneficiary`, `amount`, `interval_days`, `next_execution`, `is_active` | `should_execute()`, `record_execution()` | `Account` |
| `DirectDebit` | `mandate_id`, `account`, `creditor_name`, `max_amount`, `is_authorized` | `authorize()`, `collect()` | `Account` |
| `InterestRate` | `currency`, `annual_rate`, `effective_from` | `annual_to_monthly()`, `apply_to()` | — |
| `DepositProduct` | `product_id`, `name`, `min_amount`, `interest_rate`, `term_days` | `estimate_return()`, `is_available_for()` | `InterestRate` |
| `Deposit` | `deposit_id`, `account`, `product`, `principal`, `opened_on`, `maturity_date`, `is_closed`, `is_funded` | `fund()`, `accrue_interest()`, `close()` | `Account`, `DepositProduct` |
| `Fee` | `fee_code`, `name`, `fixed_amount`, `percentage_rate`, `is_waived` | `calculate()`, `waive()` | — |
| `ExchangeRate` | `base_currency`, `quote_currency`, `rate`, `updated_at` | `convert()`, `invert()` | — |
| `CurrencyExchange` | `exchange_id`, `source_account`, `target_account`, `amount`, `rate`, `is_executed` | `quote()`, `execute()` | `Account`, `ExchangeRate` |
| `CreditScore` | `customer_id`, `base_score`, `factors` | `add_factor()`, `calculate_score()` | — |
| `LoanProduct` | `product_id`, `name`, `annual_rate`, `min_term_months`, `max_term_months`, `max_amount` | `estimate_monthly_payment()`, `validate_term()` | — |
| `LoanApplication` | `application_id`, `applicant`, `product`, `requested_amount`, `term_months`, `credit_score`, `status`, `rejection_reason` | `approve()`, `reject()` | `CreditScore`, `Customer`, `LoanProduct` |
| `Repayment` | `repayment_id`, `loan_id`, `amount`, `due_date`, `paid_on`, `principal_paid`, `interest_paid` | `split_payment()`, `is_late()` | — |
| `Loan` | `loan_id`, `borrower`, `product`, `principal`, `annual_rate`, `term_months`, `outstanding_balance`, `repayments`, `status` | `calculate_payment()`, `register_repayment()`, `mark_defaulted()` | `Customer`, `LoanProduct`, `Repayment` |
| `FraudAlert` | `alert_id`, `account`, `reason`, `severity`, `created_at`, `is_resolved`, `assigned_employee` | `escalate()`, `resolve()` | `Account`, `Employee` |
| `AuditRecord` | `record_id`, `actor_id`, `action`, `entity_type`, `created_at`, `is_reviewed` | `describe()`, `mark_reviewed()` | — |
| `Notification` | `notification_id`, `customer`, `message`, `channel`, `is_sent`, `is_read`, `sent_at` | `mark_sent()`, `mark_read()`, `render()` | `Customer` |

## Собственные исключения

- `BankingError`
- `ValidationError`
- `CustomerNotFoundError`
- `AccountNotFoundError`
- `AccountClosedError`
- `InsufficientFundsError`
- `InvalidAmountError`
- `CardBlockedError`
- `CardExpiredError`
- `TransferRejectedError`
- `LoanNotApprovedError`
- `CurrencyRateNotFoundError`

## Структура проекта

```text
banking_project/
├── main.py                 # асинхронный CLI — начальная заготовка
├── banking/
│   ├── __init__.py
│   ├── exceptions.py
│   ├── people.py
│   ├── organization.py
│   ├── accounts.py
│   ├── cards.py
│   ├── payments.py
│   ├── products.py
│   ├── lending.py
│   └── services.py
├── tests/
│   ├── conftest.py
│   ├── test_people.py
│   ├── test_organization.py
│   ├── test_accounts.py
│   ├── test_cards.py
│   ├── test_payments.py
│   ├── test_products.py
│   ├── test_lending.py
│   └── test_services.py
├── pyproject.toml
└── .gitignore
```

Архитектура намеренно простая: обычные модули по областям банковской предметной
области, без дополнительных слоёв, контейнеров зависимостей и репозиторных
абстракций. Доменная логика синхронная и не зависит от консольного интерфейса.
В корне уже есть минимальная заготовка `main.py`; асинхронное меню и сценарии CLI будем реализовывать вместе на следующем этапе.

## Запуск тестов

Установить тестовые зависимости:

```bash
python -m pip install -e ".[test]"
```

Запустить тесты:

```bash
python -m pytest -q
```

Проверить покрытие:

```bash
python -m pytest --cov=banking --cov-report=term-missing
```

Текущий результат проверки: **65 тестов пройдены, покрытие 100%**.

## Что ещё добавить перед финальной сдачей

- асинхронный `main.py` с консольным меню и демонстрацией ключевых операций;
- документацию/описание запуска CLI;
- GitHub Actions для запуска тестов, проверки покрытия и линтера;
- сборку и публикацию артефакта в GitHub Releases.

Эти пункты не включены в текущий этап, потому что CLI и Git workflow будем
делать отдельно и разбирать вместе.
