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


@dataclass
class Ledger:
    timestamp: int
    customer_id: str
    tranx_id: UUID
    transaction_type: TxnType
    amount: int
    description: str | None = None


class CustomerAccount:
    def __init__(self, customer_id: str) -> None:
        self.customer_id = customer_id
        self.balance = 0
        self.ledgers: list[Ledger] = []

    def add_ledger(self, ledger: Ledger):
        if ledger.transaction_type in (TxnType.CREDIT, TxnType.CHARGE):
            self.balance += ledger.amount
        self.ledgers.append(ledger)


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
        raise NotImplementedError

    def cancel(self, timestamp: int, customer_id: str) -> bool:
        raise NotImplementedError

    def subscription_status(self, timestamp: int, customer_id: str) -> str | None:
        raise NotImplementedError

    def run_billing(self, timestamp: int) -> list[str]:
        raise NotImplementedError

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
