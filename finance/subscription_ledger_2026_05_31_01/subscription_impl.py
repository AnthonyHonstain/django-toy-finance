from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from finance.subscription_ledger_2026_05_31_01.subscription_interface import (
    SubscriptionInterface,
    TransactionResponse,
)


class TxnType(StrEnum):
    CREDIT = "CREDIT"
    CHARGE = "CHARGE"


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELED = "canceled"


@dataclass
class Ledger:
    timestamp: int
    customer_id: str
    tranx_id: UUID
    transaction_type: TxnType
    amount: int
    description: str | None = None
    subscription_plan_id: str | None = None


@dataclass
class Subscription:
    plan_id: str
    monthly_amount: int
    status: SubscriptionStatus
    created_timestamp: int
    canceled_timestamp: int | None = None

    def is_active(self, timestamp: int) -> bool:
        active_as_of_timestamp = self.created_timestamp <= timestamp
        if self.canceled_timestamp:
            active_as_of_timestamp = (
                active_as_of_timestamp and timestamp < self.canceled_timestamp
            )
        return active_as_of_timestamp


class CustomerAccount:
    def __init__(self, customer_id: str) -> None:
        self.customer_id = customer_id
        self.balance = 0
        self.ledgers: list[Ledger] = []
        self.subscriptions: dict[str, Subscription] = {}

    def add_ledger(self, ledger: Ledger) -> None:
        if ledger.transaction_type in (TxnType.CREDIT, TxnType.CHARGE):
            self.balance += ledger.amount
        self.ledgers.append(ledger)

    def add_subscription(self, subscription: Subscription) -> None:
        # As I read it, it seems like this problem is trying to box me
        # in to a single subscription per user based on the API design.
        # I think I read the plan_id as a signal on multiple subscriptions
        # per user, but now that I think more on the API, I think plan_id
        # was just for validation (to add more complexity/visibility to method
        # results and the tests)
        if subscription.plan_id in self.subscriptions:
            raise Exception(
                "Only one subscription per plan_id allowed at a time per user"
            )
        self.subscriptions[subscription.plan_id] = subscription

    def get_subscription(self) -> Subscription | None:
        if len(self.subscriptions) > 1:
            raise Exception("More than one subscription found, invalid state")
        for k, v in self.subscriptions.items():
            return v
        return None

    def get_subscription_ledger(self, timestamp: int, plan_id: str) -> Ledger | None:
        for ledger in self.ledgers:
            if (
                ledger.timestamp == timestamp
                and ledger.transaction_type == TxnType.CHARGE
                and ledger.subscription_plan_id == plan_id
            ):
                return ledger
        return None


class SubscriptionImpl(SubscriptionInterface):
    """Fresh implementation surface for the subscription ledger exercise."""

    def __init__(self) -> None:
        self.customer_accounts: dict[str, CustomerAccount] = {}

    def create_customer(self, timestamp: int, customer_id: str) -> bool:
        if customer_id in self.customer_accounts:
            return False

        customer_account = CustomerAccount(customer_id)
        self.customer_accounts[customer_id] = customer_account
        return True

    def add_credit(
        self, timestamp: int, customer_id: str, amount: int
    ) -> TransactionResponse:
        if customer_id not in self.customer_accounts:
            return TransactionResponse(False)

        customer_account = self.customer_accounts[customer_id]
        tranx_id = uuid4()
        ledger = Ledger(timestamp, customer_id, tranx_id, TxnType.CREDIT, amount)
        customer_account.add_ledger(ledger)
        return TransactionResponse(True, tranx_id, customer_account.balance)

    def charge(
        self, timestamp: int, customer_id: str, amount: int, description: str
    ) -> TransactionResponse:
        if customer_id not in self.customer_accounts:
            return TransactionResponse(False)

        # Not allowing negative balance
        customer_account = self.customer_accounts[customer_id]
        if customer_account.balance - amount < 0:
            return TransactionResponse(False)

        tranx_id = uuid4()
        ledger = Ledger(
            timestamp, customer_id, tranx_id, TxnType.CHARGE, -amount, description
        )
        customer_account.add_ledger(ledger)
        return TransactionResponse(True, tranx_id, customer_account.balance)

    def balance(self, timestamp: int, customer_id: str) -> int | None:
        if customer_id not in self.customer_accounts:
            return None
        customer_account = self.customer_accounts[customer_id]
        return customer_account.balance

    def subscribe(
        self, timestamp: int, customer_id: str, plan_id: str, monthly_amount: int
    ) -> bool:
        if customer_id not in self.customer_accounts:
            return False

        customer = self.customer_accounts[customer_id]
        subscription = Subscription(
            plan_id, monthly_amount, SubscriptionStatus.ACTIVE, timestamp
        )
        customer.add_subscription(subscription)
        return True

    def cancel(self, timestamp: int, customer_id: str) -> bool:
        if customer_id not in self.customer_accounts:
            return False
        customer = self.customer_accounts[customer_id]
        subscription = customer.get_subscription()
        if subscription:
            # What if already canceled? going to write this to be idempotent initially
            # but that side steps issues like repeated created/cancel and
            # conditions like trying to cancel something before it was created.
            subscription.status = SubscriptionStatus.CANCELED
            subscription.canceled_timestamp = timestamp
            return True
        return False

    def subscription_status(self, timestamp: int, customer_id: str) -> str | None:
        if customer_id not in self.customer_accounts:
            return "inactive"

        customer = self.customer_accounts[customer_id]
        subscription = customer.get_subscription()
        if subscription:
            active_as_of_timestamp = subscription.is_active(timestamp)

            if (
                active_as_of_timestamp
                and subscription.status == SubscriptionStatus.ACTIVE
            ):
                return f"{subscription.status}:{subscription.plan_id}"

            if subscription.status == SubscriptionStatus.CANCELED:
                return f"{subscription.status}"
        return "inactive"

    def run_billing(self, timestamp: int) -> list[str]:
        result = []
        for customer in self.customer_accounts.values():
            if subscription := customer.get_subscription():
                # We have a few things to check
                # 1) subscription is active during the timestamp
                # 2) it doesn't create additional charges for same timestamp
                if not subscription.is_active(timestamp):
                    # No longer active, not active yet
                    continue
                if customer.get_subscription_ledger(timestamp, subscription.plan_id):
                    # Already processed
                    continue
                ledger = Ledger(
                    timestamp,
                    customer.customer_id,
                    uuid4(),
                    TxnType.CHARGE,
                    -subscription.monthly_amount,
                    subscription_plan_id=subscription.plan_id,
                )
                customer.add_ledger(ledger)
                result.append(
                    f"{customer.customer_id}: charged {subscription.monthly_amount} for {subscription.plan_id}"
                )

        return result

    def statement(
        self, customer_id: str, start_timestamp: int, end_timestamp: int
    ) -> list[str]:
        raise NotImplementedError

    def top_customers_by_revenue(self, timestamp: int, k: int) -> list[str]:
        raise NotImplementedError

    def transaction(self, timestamp: int, transaction_id: UUID) -> str | None:
        raise NotImplementedError

    def reverse(self, timestamp: int, transaction_id: UUID) -> bool:
        raise NotImplementedError
