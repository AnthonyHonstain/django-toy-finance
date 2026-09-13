from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class TransactionResult:
    successful: bool
    transaction_id: UUID | None = None
    balance: int | None = None


class SubscriptionLedgerInterface(ABC):
    """Contract for the 2026-09-13 subscription-ledger practice run.

    Amounts are positive integer cents. Timestamps are integer event markers
    supplied by the caller. Calls normally arrive in timestamp order, except
    that a failed billing timestamp may be retried after later credit is added.
    Supported plan identifiers are the fixed values ``basic`` and ``pro``;
    attempts to create other plan IDs fail. A customer may have at most one
    current subscription, and a plan change affects future billing only.

    Billing rules:

    * A customer must exist before receiving credit or subscribing.
    * A plan must exist before a customer can subscribe to it.
    * Billing never makes an account balance negative.
    * Each customer can be charged at most once for a billing timestamp.
    * A failed attempt caused by insufficient credit may be retried after the
      customer receives more credit.
    * Result rows are sorted by customer ID for deterministic output.
    """

    @abstractmethod
    def create_plan(self, timestamp: int, plan_id: str, price: int) -> bool:
        """Create a supported plan.

        Return False if the plan ID is unsupported or already exists.
        """

    @abstractmethod
    def create_customer(self, timestamp: int, customer_id: str) -> bool:
        """Create a customer, returning False if the customer already exists."""

    @abstractmethod
    def add_credit(
        self, timestamp: int, customer_id: str, amount: int
    ) -> TransactionResult:
        """Credit an existing customer and return the resulting balance."""

    @abstractmethod
    def balance(self, timestamp: int, customer_id: str) -> int | None:
        """Return the current balance, or None when the customer is unknown."""

    @abstractmethod
    def subscribe(self, timestamp: int, customer_id: str, plan_id: str) -> bool:
        """Start a subscription for a customer with no current subscription."""

    @abstractmethod
    def change_plan(self, timestamp: int, customer_id: str, plan_id: str) -> bool:
        """Change an active customer's plan for future billing runs."""

    @abstractmethod
    def cancel(self, timestamp: int, customer_id: str) -> bool:
        """Cancel an active subscription; repeated cancellation returns False."""

    @abstractmethod
    def subscription_status(self, timestamp: int, customer_id: str) -> str | None:
        """Return None for an unknown customer, otherwise inactive or active:PLAN."""

    @abstractmethod
    def run_billing(self, timestamp: int) -> list[str]:
        """Attempt billing for every active subscription.

        Successful rows use ``CUSTOMER: charged PRICE for PLAN``. Insufficient
        credit rows use ``CUSTOMER: payment_failed PRICE for PLAN``.
        """

    @abstractmethod
    def statement(
        self, customer_id: str, start_timestamp: int, end_timestamp: int
    ) -> list[str]:
        """Return ledger rows in an inclusive range with running balances."""

    @abstractmethod
    def top_plans_by_revenue(self, timestamp: int, k: int) -> list[str]:
        """Rank plans by successful billing revenue, then plan ID ascending."""
