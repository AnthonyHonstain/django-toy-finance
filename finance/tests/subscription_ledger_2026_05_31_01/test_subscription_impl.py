from finance.subscription_ledger_2026_05_31_01.subscription_impl import (
    SubscriptionImpl,
)
from finance.subscription_ledger_2026_05_31_01.subscription_interface import (
    TransactionResponse,
)

CUSTOMER_1 = "customer1"
CUSTOMER_2 = "customer2"


class TestSubscriptionLedger:
    def test_create_customer_and_balance(self):
        ledger = SubscriptionImpl()

        assert ledger.create_customer(1, CUSTOMER_1) is True
        assert ledger.create_customer(2, CUSTOMER_1) is False
        assert ledger.balance(3, CUSTOMER_1) == 0
        assert ledger.balance(4, "missing") is None

    def test_credit_unknown_customer(self):
        ledger = SubscriptionImpl()
        ledger.create_customer(1, CUSTOMER_1)

        credit = ledger.add_credit(2, CUSTOMER_2, 1000)
        assert credit.successful is False

    def test_credit(self):
        ledger = SubscriptionImpl()
        ledger.create_customer(1, CUSTOMER_1)

        credit = ledger.add_credit(2, CUSTOMER_1, 1000)
        assert credit.successful is True
        assert credit.balance == 1000

        credit = ledger.add_credit(3, CUSTOMER_1, 2000)
        assert credit.successful is True
        assert credit.balance == 3000

    def test_charge_insufficient(self):
        ledger = SubscriptionImpl()
        ledger.create_customer(1, CUSTOMER_1)

        charge = ledger.charge(2, CUSTOMER_1, 250, "one-time setup")
        assert charge.successful is False

    def test_credit_and_charge(self):
        ledger = SubscriptionImpl()
        ledger.create_customer(1, CUSTOMER_1)

        credit = ledger.add_credit(2, CUSTOMER_1, 1000)
        assert credit.successful is True
        assert credit.balance == 1000

        charge = ledger.charge(3, CUSTOMER_1, 250, "one-time setup")
        assert charge.successful is True
        assert charge.balance == 750
        assert ledger.balance(4, CUSTOMER_1) == 750

    def test_charge_missing_customer_fails(self):
        ledger = SubscriptionImpl()

        assert ledger.charge(1, "missing", 250, "one-time setup") == (
            TransactionResponse(False)
        )

    def test_subscribe_cancel_and_status(self):
        ledger = SubscriptionImpl()
        ledger.create_customer(1, CUSTOMER_1)

        assert ledger.subscription_status(2, CUSTOMER_1) == "inactive"
        assert ledger.subscribe(3, CUSTOMER_1, "basic", 500) is True
        assert ledger.subscription_status(4, CUSTOMER_1) == "active:basic"
        assert ledger.cancel(5, CUSTOMER_1) is True
        assert ledger.subscription_status(6, CUSTOMER_1) == "canceled"

    def test_run_billing_is_idempotent_for_same_timestamp(self):
        ledger = SubscriptionImpl()
        ledger.create_customer(1, CUSTOMER_1)
        ledger.add_credit(2, CUSTOMER_1, 1000)
        ledger.subscribe(3, CUSTOMER_1, "basic", 500)

        assert ledger.run_billing(10) == ["customer1: charged 500 for basic"]
        assert ledger.run_billing(10) == []
        assert ledger.balance(11, CUSTOMER_1) == 500

    def test_statement_uses_opening_balance_before_range(self):
        ledger = SubscriptionImpl()
        ledger.create_customer(1, CUSTOMER_1)
        ledger.add_credit(2, CUSTOMER_1, 1000)
        ledger.charge(3, CUSTOMER_1, 400, "setup")
        ledger.add_credit(6, CUSTOMER_1, 50)

        assert ledger.statement(CUSTOMER_1, 6, 6) == [
            "6: CREDIT 50 balance=650",
        ]

    def test_top_customers_by_revenue(self):
        ledger = SubscriptionImpl()
        ledger.create_customer(1, "alice")
        ledger.create_customer(2, "bob")
        ledger.add_credit(3, "alice", 1000)
        ledger.add_credit(4, "bob", 1000)
        ledger.charge(5, "alice", 400, "setup")
        ledger.charge(6, "alice", 200, "usage")
        ledger.charge(7, "bob", 500, "setup")

        assert ledger.top_customers_by_revenue(10, 2) == [
            "alice(600)",
            "bob(500)",
        ]

    def test_reverse_charge(self):
        ledger = SubscriptionImpl()
        ledger.create_customer(1, CUSTOMER_1)
        ledger.add_credit(2, CUSTOMER_1, 1000)
        charge = ledger.charge(3, CUSTOMER_1, 250, "setup")
        assert charge.id is not None

        assert ledger.reverse(4, charge.id) is True
        assert ledger.balance(5, CUSTOMER_1) == 1000
        assert ledger.reverse(6, charge.id) is False
