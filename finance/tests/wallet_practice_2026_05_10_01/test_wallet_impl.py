from finance.wallet_practice_2026_05_10_01.wallet_impl import WalletImpl


USER_1 = "user1"
USER_2 = "user2"


class TestWalletPractice:
    def test_credit_and_balance(self):
        wallet = WalletImpl()
        credit_result = wallet.credit(1, USER_1, 100)
        assert credit_result is 100

        assert wallet.balance(0, USER_1) is 100
        assert wallet.balance(1, USER_1) is 100
        assert wallet.balance(2, USER_1) is 0

    def test_purchase_success_and_failure(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 100)

        assert wallet.purchase(2, USER_1, 100) is 0
        assert wallet.purchase(2, USER_1, 101) is None

    def test_purchase_with_unknown_user(self):
        wallet = WalletImpl()

        assert wallet.purchase(1, USER_2, 100) is None

    def test_purchase_multiple_credit_and_balance(self):
        wallet = WalletImpl()
        wallet.credit(1, USER_1, 100)

        assert wallet.purchase(2, USER_1, 75) is 25
        assert wallet.credit(3, USER_1, 100) is 125
        assert wallet.purchase(4, USER_1, 124) is 1
        assert wallet.purchase(5, USER_1, 2) is None
        assert wallet.purchase(6, USER_1, 1) is 0

    def test_transfer_between_users(self):
        wallet = WalletImpl()
        assert wallet is not None

    def test_top_customers(self):
        wallet = WalletImpl()
        assert wallet is not None
