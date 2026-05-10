from finance.wallet_practice_2025_10_12_01.wallet_impl import WalletImpl


class TestWalletPhase1:
    def test_credit_and_balance(self):
        w = WalletImpl()
        assert w.credit(10, "u1", 0) == 0
        assert w.credit(11, "u1", 500) == 500
        assert w.balance(12, "u1") == 500

    def test_purchase_success_and_fail(self):
        w = WalletImpl()
        w.credit(1, "u1", 1000)
        assert w.purchase(2, "u1", 400) == 600
        assert w.purchase(3, "u1", 700) is None
        assert w.balance(4, "u1") == 600

    def test_transfer(self):
        w = WalletImpl()
        w.credit(1, "a", 500)
        w.credit(2, "b", 100)
        assert w.transfer(3, "a", "b", 200) == 300
        assert w.balance(4, "a") == 300
        assert w.balance(4, "b") == 300

    def test_top_customers_basic(self):
        w = WalletImpl()
        w.credit(1, "c", 2000)
        w.credit(1, "b", 2000)
        w.credit(1, "a", 2000)
        w.purchase(2, "a", 600)
        w.purchase(3, "b", 600)
        w.purchase(4, "b", 100)
        assert w.top_customers(5, 2) == ["b(700)", "a(600)"]

    def test_top_customers_ties_and_zero(self):
        w = WalletImpl()
        w.credit(1, "acct2", 10)
        w.credit(1, "acct1", 10)
        # no purchases -> both 0, alphabetical
        assert w.top_customers(2, 5) == ["acct1(0)", "acct2(0)"]
