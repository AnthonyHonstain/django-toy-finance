from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass
class TransactionResponse:
    successful: bool
    id: UUID | None = None
    balance: int | None = None


class SubscriptionInterface(ABC):
    """Contract for a subscription ledger practice implementation.

    Amounts are integer cents or arbitrary integer units. Timestamps are plain
    integers to keep the exercise focused on data modeling rather than date
    handling. Mutating operations may assume calls arrive in timestamp order
    unless a test explicitly says otherwise.

    Reference behavior:

    * Customers must exist before most billing operations can succeed.
    * Credits increase a customer's available balance.
    * Charges decrease a customer's available balance when allowed.
    * Subscriptions create recurring charges when `run_billing` is called.
    * Billing runs should be idempotent for the same timestamp/period.
    * Statements show one customer's ledger rows in timestamp order.
    * Revenue rankings are based on successful charges, with ties broken by
      customer ID.
    """

    @abstractmethod
    def create_customer(self, timestamp: int, customer_id: str) -> bool:
        """Create a customer.

        Return True when the customer is created. Return False when the
        customer already exists.
        """

    @abstractmethod
    def add_credit(
        self, timestamp: int, customer_id: str, amount: int
    ) -> TransactionResponse:
        """Add credit to a customer and return transaction metadata."""

    @abstractmethod
    def charge(
        self, timestamp: int, customer_id: str, amount: int, description: str
    ) -> TransactionResponse:
        """Charge a customer and return transaction metadata.

        The implementation should decide whether charges may make balances
        negative or whether they require available credit.
        """

    @abstractmethod
    def balance(self, timestamp: int, customer_id: str) -> int | None:
        """Return the customer's current balance, or None if missing."""

    @abstractmethod
    def subscribe(
        self, timestamp: int, customer_id: str, plan_id: str, monthly_amount: int
    ) -> bool:
        """Subscribe a customer to a recurring plan."""

    @abstractmethod
    def cancel(self, timestamp: int, customer_id: str) -> bool:
        """Cancel a customer's active subscription."""

    @abstractmethod
    def subscription_status(self, timestamp: int, customer_id: str) -> str | None:
        """Return a customer's subscription status, or None if missing."""

    @abstractmethod
    def run_billing(self, timestamp: int) -> list[str]:
        """Run recurring billing for active subscriptions.

        Return formatted billing result rows. Running billing more than once for
        the same billing timestamp should not create duplicate charges.
        """

    @abstractmethod
    def statement(
        self, customer_id: str, start_timestamp: int, end_timestamp: int
    ) -> list[str]:
        """Return formatted ledger rows for one customer in an inclusive range."""

    @abstractmethod
    def top_customers_by_revenue(self, timestamp: int, k: int) -> list[str]:
        """Return the top `k` customers by successful charge activity.

        Format each result as `"customer_id(amount)"`. Sort by amount
        descending, then customer ID ascending.
        """

    @abstractmethod
    def transaction(self, timestamp: int, transaction_id: UUID) -> str | None:
        """Return a formatted transaction description, or None if unknown."""

    @abstractmethod
    def reverse(self, timestamp: int, transaction_id: UUID) -> bool:
        """Reverse a transaction if it is safe to do so.

        Return False when the transaction is unknown, already reversed, or not
        safely reversible.
        """
