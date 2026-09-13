from finance.subscription_ledger_2026_09_13_01.subscription_interface import (
    SubscriptionLedgerInterface,
    TransactionResult,
)


class SubscriptionLedger(SubscriptionLedgerInterface):
    """Fresh implementation surface for the 2026-09-13 practice run."""

    def __init__(self) -> None:
        # Choose the state and indexes you want as each phase demands them.
        pass

    def create_plan(self, timestamp: int, plan_id: str, price: int) -> bool:
        raise NotImplementedError

    def create_customer(self, timestamp: int, customer_id: str) -> bool:
        raise NotImplementedError

    def add_credit(
        self, timestamp: int, customer_id: str, amount: int
    ) -> TransactionResult:
        raise NotImplementedError

    def balance(self, timestamp: int, customer_id: str) -> int | None:
        raise NotImplementedError

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
