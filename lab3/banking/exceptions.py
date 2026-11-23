"""Domain-specific exceptions for the banking application."""


class BankingError(Exception):
    """Base class for banking domain errors."""


class ValidationError(BankingError):
    """Raised when input data or a requested operation is invalid."""


class CustomerNotFoundError(BankingError):
    """Raised when a customer cannot be found."""


class AccountNotFoundError(BankingError):
    """Raised when an account cannot be found."""


class AccountClosedError(BankingError):
    """Raised when an operation targets a closed account."""


class InsufficientFundsError(BankingError):
    """Raised when an account does not have enough available money."""


class InvalidAmountError(BankingError):
    """Raised when a monetary amount is zero or negative."""


class CardBlockedError(BankingError):
    """Raised when a blocked card is used."""


class CardExpiredError(BankingError):
    """Raised when an expired card is used."""


class TransferRejectedError(BankingError):
    """Raised when a transfer or payment cannot be completed."""


class LoanNotApprovedError(BankingError):
    """Raised when a loan application does not satisfy approval rules."""


class CurrencyRateNotFoundError(BankingError):
    """Raised when a valid exchange rate is unavailable."""
