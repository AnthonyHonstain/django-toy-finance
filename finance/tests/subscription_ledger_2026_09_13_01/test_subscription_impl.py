from unittest.mock import ANY

import pytest

from finance.subscription_ledger_2026_09_13_01.subscription_impl import (
    SubscriptionLedger,
)
from finance.subscription_ledger_2026_09_13_01.subscription_interface import (
    TransactionResult,
)


class TestSubscriptionLedger:
    # Phase 1: remove one skip at a time, starting here.
    @pytest.mark.skip(
        reason="Fresh practice run: enable Phase 1 scenarios one at a time"
    )
    def test_create_plans_and_customers(self):
        ledger = SubscriptionLedger()

        assert ledger.create_plan(1, "basic", 500) is True
        assert ledger.create_plan(2, "basic", 999) is False
        assert ledger.create_customer(3, "alice") is True
        assert ledger.create_customer(4, "alice") is False

    @pytest.mark.skip(
        reason="Fresh practice run: enable Phase 1 scenarios one at a time"
    )
    def test_credit_and_balance(self):
        ledger = SubscriptionLedger()
        ledger.create_customer(1, "alice")

        assert ledger.add_credit(2, "missing", 500) == TransactionResult(False)
        assert ledger.add_credit(3, "alice", 1_000) == TransactionResult(
            True, ANY, 1_000
        )
        assert ledger.add_credit(4, "alice", 250) == TransactionResult(True, ANY, 1_250)
        assert ledger.balance(5, "alice") == 1_250
        assert ledger.balance(6, "missing") is None

    # Phase 2: subscription lifecycle.
    @pytest.mark.skip(reason="Fresh practice run: enable after Phase 1")
    def test_subscribe_requires_known_customer_and_plan(self):
        ledger = SubscriptionLedger()
        ledger.create_plan(1, "basic", 500)
        ledger.create_customer(2, "alice")

        assert ledger.subscribe(3, "missing", "basic") is False
        assert ledger.subscribe(4, "alice", "missing") is False
        assert ledger.subscribe(5, "alice", "basic") is True
        assert ledger.subscribe(6, "alice", "basic") is False

    @pytest.mark.skip(reason="Fresh practice run: enable after subscribe")
    def test_status_change_plan_and_cancel(self):
        ledger = SubscriptionLedger()
        ledger.create_plan(1, "basic", 500)
        ledger.create_plan(2, "pro", 900)
        ledger.create_customer(3, "alice")

        assert ledger.subscription_status(4, "missing") is None
        assert ledger.subscription_status(5, "alice") == "inactive"
        assert ledger.subscribe(6, "alice", "basic") is True
        assert ledger.subscription_status(7, "alice") == "active:basic"
        assert ledger.change_plan(8, "alice", "pro") is True
        assert ledger.subscription_status(9, "alice") == "active:pro"
        assert ledger.cancel(10, "alice") is True
        assert ledger.cancel(11, "alice") is False
        assert ledger.subscription_status(12, "alice") == "inactive"

    # Phase 3: recurring billing and idempotency.
    @pytest.mark.skip(reason="Fresh practice run: enable after Phase 2")
    def test_billing_charges_active_customers_in_stable_order(self):
        ledger = SubscriptionLedger()
        ledger.create_plan(1, "basic", 500)
        for customer in ("bob", "alice"):
            ledger.create_customer(2, customer)
            ledger.add_credit(3, customer, 1_000)
            ledger.subscribe(4, customer, "basic")

        assert ledger.run_billing(10) == [
            "alice: charged 500 for basic",
            "bob: charged 500 for basic",
        ]
        assert ledger.balance(11, "alice") == 500
        assert ledger.balance(12, "bob") == 500

    @pytest.mark.skip(reason="Fresh practice run: enable after basic billing")
    def test_successful_billing_is_idempotent_for_a_timestamp(self):
        ledger = SubscriptionLedger()
        ledger.create_plan(1, "basic", 500)
        ledger.create_customer(2, "alice")
        ledger.add_credit(3, "alice", 1_000)
        ledger.subscribe(4, "alice", "basic")

        assert ledger.run_billing(10) == ["alice: charged 500 for basic"]
        assert ledger.run_billing(10) == []
        assert ledger.balance(11, "alice") == 500

    @pytest.mark.skip(reason="Fresh practice run: enable after idempotent billing")
    def test_failed_billing_can_be_retried_after_credit(self):
        ledger = SubscriptionLedger()
        ledger.create_plan(1, "pro", 900)
        ledger.create_customer(2, "alice")
        ledger.add_credit(3, "alice", 500)
        ledger.subscribe(4, "alice", "pro")

        assert ledger.run_billing(10) == [
            "alice: payment_failed 900 for pro",
        ]
        assert ledger.balance(11, "alice") == 500
        ledger.add_credit(12, "alice", 400)
        assert ledger.run_billing(10) == ["alice: charged 900 for pro"]
        assert ledger.run_billing(10) == []

    @pytest.mark.skip(reason="Fresh practice run: enable after billing retries")
    def test_plan_change_affects_future_billing(self):
        ledger = SubscriptionLedger()
        ledger.create_plan(1, "basic", 500)
        ledger.create_plan(2, "pro", 900)
        ledger.create_customer(3, "alice")
        ledger.add_credit(4, "alice", 2_000)
        ledger.subscribe(5, "alice", "basic")

        assert ledger.run_billing(10) == ["alice: charged 500 for basic"]
        assert ledger.change_plan(11, "alice", "pro") is True
        assert ledger.run_billing(20) == ["alice: charged 900 for pro"]
        assert ledger.balance(21, "alice") == 600

    # Phase 4: ledger queries and reporting.
    @pytest.mark.skip(reason="Fresh practice run: enable after Phase 3")
    def test_statement_carries_balance_into_requested_range(self):
        ledger = SubscriptionLedger()
        ledger.create_plan(1, "basic", 500)
        ledger.create_customer(2, "alice")
        ledger.add_credit(3, "alice", 1_000)
        ledger.subscribe(4, "alice", "basic")
        ledger.run_billing(5)
        ledger.add_credit(8, "alice", 100)

        assert ledger.statement("alice", 8, 8) == [
            "8: CREDIT 100 balance=600",
        ]

    @pytest.mark.skip(reason="Fresh practice run: enable after statements")
    def test_top_plans_rank_by_successful_billing_revenue(self):
        ledger = SubscriptionLedger()
        ledger.create_plan(1, "basic", 500)
        ledger.create_plan(2, "pro", 900)
        for customer, plan in (("alice", "basic"), ("bob", "pro")):
            ledger.create_customer(3, customer)
            ledger.add_credit(4, customer, 2_000)
            ledger.subscribe(5, customer, plan)

        ledger.run_billing(10)
        ledger.run_billing(20)

        assert ledger.top_plans_by_revenue(21, 2) == ["pro(1800)", "basic(1000)"]
