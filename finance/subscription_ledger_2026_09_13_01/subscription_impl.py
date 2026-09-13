from dataclasses import dataclass
from enum import StrEnum, auto
from uuid import uuid4

from finance.subscription_ledger_2026_09_13_01.subscription_interface import (
    SubscriptionLedgerInterface,
    TransactionResult,
)


class PlanType(StrEnum):
    BASIC = auto()
    PRO = auto()


@dataclass
class Plan:
    timestamp: int
    plan_id: PlanType
    price: int


@dataclass
class Ledger:
    # Debating double entry accounting and how it relates to a global ledger
    # vs having each customer hold a ledger.
    # UPDATE - Oh there isn't a transfer in this one... I wasn't groking the full problem context
    timestamp: int
    customer_id: str
    amount: int


class Customer:
    created_timestamp: int
    customer_id: str

    def __init__(self, created_timestamp: int, customer_id: str):
        self.created_timestamp = created_timestamp
        self.customer_id = customer_id
        self.ledger_list: list[Ledger] = []

    def add_credit(self, timestamp, amount):
        self.ledger_list.append(Ledger(timestamp, self.customer_id, amount))

    def balance(self):
        total = 0
        for ledger in self.ledger_list:
            total += ledger.amount
        return total


class SubscriptionLedger(SubscriptionLedgerInterface):
    """Fresh implementation surface for the 2026-09-13 practice run."""

    def __init__(self) -> None:
        # Choose the state and indexes you want as each phase demands them.
        self.plans: dict[PlanType, Plan] = {}
        self.customers: dict[str, Customer] = {}

    def create_plan(self, timestamp: int, plan_id: str, price: int) -> bool:
        if plan_id not in PlanType:
            return False
        plan_enum = PlanType(plan_id)
        if plan_enum in self.plans:
            return False

        self.plans[plan_enum] = Plan(timestamp, plan_enum, price)
        return True

    def create_customer(self, timestamp: int, customer_id: str) -> bool:
        if customer_id in self.customers:
            return False

        self.customers[customer_id] = Customer(
            created_timestamp=timestamp, customer_id=customer_id
        )
        return True

    def add_credit(
        self, timestamp: int, customer_id: str, amount: int
    ) -> TransactionResult:
        if customer_id not in self.customers:
            return TransactionResult(False, None, None)

        customer = self.customers[customer_id]
        customer.add_credit(timestamp, amount)
        balance = customer.balance()

        return TransactionResult(True, uuid4(), balance)

    def balance(self, timestamp: int, customer_id: str) -> int | None:
        if customer_id not in self.customers:
            return None

        customer = self.customers[customer_id]
        balance = customer.balance()
        return balance

    def subscribe(self, timestamp: int, customer_id: str, plan_id: str) -> bool:
        raise NotImplementedError

    def change_plan(self, timestamp: int, customer_id: str, plan_id: str) -> bool:
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

    def top_plans_by_revenue(self, timestamp: int, k: int) -> list[str]:
        raise NotImplementedError
