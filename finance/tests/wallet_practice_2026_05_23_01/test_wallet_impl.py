import pytest

from finance.wallet_practice_2026_05_23_01.wallet_impl import WalletImpl

USER_1 = "user1"
USER_2 = "user2"


class TestWalletPractice:
    def test_credit(self):
        wallet = WalletImpl()
        assert wallet.credit(1, USER_1, 100) == 100

    def test_credit_repeated(self):
        wallet = WalletImpl()
        assert wallet.credit(1, USER_1, 100) == 100
        assert wallet.credit(2, USER_1, 200) == 300

    def test_credit_and_balance(self):
        wallet = WalletImpl()

        assert wallet.credit(1, USER_1, 100) == 100
        assert wallet.balance(2, USER_1) == 100
        assert wallet.balance(3, "missing") is None

    def test_purchase_success_and_failure(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 100)

        assert wallet.purchase(2, USER_1, 75) == 25
        assert wallet.purchase(3, USER_1, 26) is None
        assert wallet.balance(4, USER_1) == 25

    def test_transfer_between_users(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 100)

        assert wallet.transfer(2, USER_1, USER_2, 51) == 49
        assert wallet.balance(3, USER_1) == 49
        assert wallet.balance(4, USER_2) == 51

    def test_balance_at_between_account_events(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 500)
        wallet.purchase(3, USER_1, 200)
        wallet.transfer(5, USER_1, USER_2, 100)

        assert wallet.balance_at(10, USER_1, 1) == 500
        assert wallet.balance_at(10, USER_1, 3) == 300
        assert wallet.balance_at(10, USER_1, 4) == 300
        assert wallet.balance_at(10, USER_1, 5) == 200
        assert wallet.balance_at(10, "missing", 5) is None

    def test_statement_filters_to_one_user_and_time_range(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 500)
        wallet.purchase(2, USER_1, 200)
        wallet.credit(3, USER_2, 999)
        wallet.transfer(4, USER_1, USER_2, 100)

        assert wallet.statement(10, USER_1, 1, 3) == [
            "1: CREDIT 500 balance=500",
            "2: PURCHASE 200 balance=300",
        ]

    def test_statement_includes_transfer_entries_for_each_user(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 500)
        wallet.transfer(2, USER_1, USER_2, 125)

        assert wallet.statement(10, USER_1, 1, 2) == [
            "1: CREDIT 500 balance=500",
            "2: TRANSFER_OUT 125 to user2 balance=375",
        ]
        assert wallet.statement(10, USER_2, 1, 2) == [
            "2: TRANSFER_IN 125 from user1 balance=125",
        ]

    def test_statement_uses_opening_balance_before_range(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 500)
        wallet.purchase(2, USER_1, 100)
        wallet.credit(5, USER_1, 25)

        assert wallet.statement(10, USER_1, 5, 5) == [
            "5: CREDIT 25 balance=425",
        ]

    def test_top_customers_counts_purchases_not_credits_or_transfers(self):
        wallet = WalletImpl()
        wallet.credit(1, "alice", 1000)
        wallet.credit(2, "bob", 10_000)
        wallet.purchase(3, "alice", 400)
        wallet.purchase(4, "alice", 200)
        wallet.purchase(5, "bob", 100)
        wallet.transfer(6, "bob", "alice", 500)

        assert wallet.top_customers(10, 2) == ["alice(600)", "bob(100)"]

    def test_top_customers_ties_sort_by_user(self):
        wallet = WalletImpl()
        wallet.credit(1, "c", 1000)
        wallet.credit(2, "a", 1000)
        wallet.credit(3, "b", 1000)
        wallet.purchase(4, "c", 100)
        wallet.purchase(5, "a", 100)
        wallet.purchase(6, "b", 100)

        assert wallet.top_customers(10, 2) == ["a(100)", "b(100)"]
