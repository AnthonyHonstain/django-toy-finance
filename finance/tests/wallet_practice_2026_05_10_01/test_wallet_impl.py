from finance.wallet_practice_2026_05_10_01.wallet_impl import WalletImpl

USER_1 = "user1"
USER_2 = "user2"


class TestWalletPractice:
    def test_credit_and_balance(self):
        wallet = WalletImpl()
        credit_result = wallet.credit(1, USER_1, 100)
        assert credit_result == 100

        assert wallet.balance(0, USER_1) == 100
        assert wallet.balance(1, USER_1) == 100
        assert wallet.balance(2, USER_1) == 0

    def test_purchase_success_and_failure(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 100)

        assert wallet.purchase(2, USER_1, 100) == 0
        assert wallet.purchase(2, USER_1, 101) is None

    def test_purchase_with_unknown_user(self):
        wallet = WalletImpl()

        assert wallet.purchase(1, USER_2, 100) == None

    def test_purchase_multiple_credit_and_balance(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 100)

        assert wallet.purchase(2, USER_1, 75) == 25
        assert wallet.credit(3, USER_1, 100) == 125
        assert wallet.purchase(4, USER_1, 124) == 1
        assert wallet.purchase(5, USER_1, 2) is None
        assert wallet.purchase(6, USER_1, 1) == 0

    def test_transfer_between_users(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 100)

        assert wallet.transfer(2, USER_1, USER_2, 51) is 49
        assert wallet.balance(0, USER_1) == 49
        assert wallet.balance(0, USER_2) == 51

    def test_transfer_between_users_source_drained_fully(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 100)
        wallet.credit(2, USER_1, 100)

        assert wallet.transfer(3, USER_1, USER_2, 200) is 0
        assert wallet.balance(0, USER_1) == 0
        assert wallet.balance(0, USER_2) == 200

    def test_transfer_with_insufficient_balance(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 100)
        assert wallet.transfer(2, USER_1, USER_2, 101) is None

    def test_top_customers_user_sort(self):
        wallet = WalletImpl()
        wallet.credit(1, "a", 100)
        wallet.credit(1, "b", 100)
        wallet.credit(1, "c", 100)
        wallet.credit(1, "d", 100)  # gets trimmed
        wallet.credit(1, "e", 90)  # gets trimmed

        assert wallet.top_customers(0, 3) == ["a", "b", "c"]

    def test_top_customers_balance_sort(self):
        wallet = WalletImpl()
        wallet.credit(1, "a", 100)
        wallet.credit(1, "b", 101)
        wallet.credit(1, "c", 102)
        wallet.credit(1, "d", 90)  # gets trimmed

        # This assertion doesn't work ['c', 'b', 'a'] != ['c', 'b', 'a']
        # I am trying to remember the pytest assert rules since I haven't
        # been using pytest for the last year.
        assert wallet.top_customers(0, 3) == ["c", "b", "a"]
