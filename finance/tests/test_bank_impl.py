from finance.bank_impl import BankImpl, Account


class TestBank:
    def test_add(self):
        bank = BankImpl()
        assert bank.add(0, "acct1", 2) == 2
        assert bank.add(1, "acct2", 3) == 3
        assert bank.add(2, "acct1", 2) == 4

    def test_transfer(self):
        bank = BankImpl()
        assert bank.transfer(0, "acct1", "acct2", 2) is None
        assert bank.add(1, "acct1", 2) == 2
        assert bank.transfer(2, "acct1", "acct2", 2) is None
        assert bank.add(3, "acct2", 3) == 3
        assert bank.transfer(4, "acct1", "acct2", 2) == 0
        assert bank.transfer(5, "acct2", "acct1", 4) == 1

    def test_top_spenders(self):
        bank = BankImpl()
        assert bank.add(1, "acct1", 10) == 10
        assert bank.add(2, "acct2", 10) == 10
        assert bank.transfer(3, "acct1", "acct2", 6) == 4
        assert bank.transfer(4, "acct2", "acct1", 5) == 11
        assert bank.top_spenders(5, 0) == []
        assert bank.top_spenders(5, 1) == ["acct1(6)"]
        assert bank.top_spenders(5, 2) == ["acct1(6)", "acct2(5)"]

    def test_add_zero_amount(self):
        bank = BankImpl()
        assert bank.add(10, "acct1", 0) == 0
        assert bank.add(11, "acct1", 5) == 5
        assert bank.add(12, "acct1", 0) == 5

    def test_transfer_insufficient_funds(self):
        bank = BankImpl()
        bank.add(1, "acct_source", 5)
        bank.add(1, "acct_dest", 10)
        # Transfer exceeds balance => should fail
        assert bank.transfer(2, "acct_source", "acct_dest", 6) is None

    def test_transfer_nonexistent_account(self):
        bank = BankImpl()
        bank.add(1, "existing_acct", 5)
        assert bank.transfer(2, "unknown_source", "existing_acct", 5) is None
        assert bank.transfer(3, "existing_acct", "unknown_dest", 5) is None

    def test_top_spenders_with_ties(self):
        bank = BankImpl()
        bank.add(0, "acctC", 20)
        bank.add(1, "acctB", 20)
        bank.transfer(2, "acctB", "acctC", 10)
        bank.add(3, "acctA", 15)
        bank.transfer(4, "acctA", "acctC", 10)
        assert bank.top_spenders(5, 2) == ["acctA(10)", "acctB(10)"]

    def test_top_spenders_large_request(self):
        bank = BankImpl()
        bank.add(1, "acct1", 5)
        bank.add(2, "acct2", 10)
        top_5 = bank.top_spenders(3, 5)
        assert len(top_5) == 2
        # Both have spend=0 => tie => alphabetical
        assert top_5 == ["acct1(0)", "acct2(0)"]

    def test_top_spenders_with_withdraw(self):
        bank = BankImpl()
        bank.add(1, "acct1", 5000)
        bank.add(2, "acct2", 1000)
        assert bank.withdraw(3, "acct1", 5000) == 0
        top_5 = bank.top_spenders(4, 5)
        assert top_5 == ["acct1(5000)", "acct2(0)"]
        two_days_in_future = Account.CASH_BACK_HOLDING_PERIOD_MS * 2
        top_5 = bank.top_spenders(two_days_in_future, 5)
        assert top_5 == ["acct1(5000)", "acct2(0)"]

    def test_withdraw(self):
        bank = BankImpl()
        assert bank.add(0, "acct1", 2000) == 2000
        assert bank.add(1, "acct2", 3000) == 3000
        assert bank.withdraw(2, "acct1", 1000) == 1000
        two_days_in_future = Account.CASH_BACK_HOLDING_PERIOD_MS * 2
        assert bank.add(two_days_in_future, "acct1", 1000) == 2020
        assert bank.add(two_days_in_future * 2, "acct1", 1000) == 3020

    def test_withdraw_with_transfer(self):
        bank = BankImpl()
        assert bank.add(0, "acct1", 2000) == 2000
        assert bank.add(1, "acct2", 3000) == 3000
        assert bank.withdraw(2, "acct1", 1000) == 1000
        assert bank.transfer(3, "acct1", "acct2", 1020) is None
        two_days_in_future = Account.CASH_BACK_HOLDING_PERIOD_MS * 2
        assert bank.transfer(two_days_in_future, "acct1", "acct2", 1020) == 0
        assert bank.add(two_days_in_future * 2, "acct1", 0) == 20

    def test_check_payment_status(self):
        bank = BankImpl()
        assert bank.add(0, "acct1", 2000) == 2000
        assert bank.add(1, "acct2", 3000) == 3000
        assert bank.check_payment_status(2, "acct1", 2) is None

        assert bank.withdraw(3, "acct1", 1000) == 1000
        assert bank.transfer(4, "acct1", "acct2", 1020) is None
        assert bank.check_payment_status(5, "acct1", 3) == "IN_PROGRESS"
        assert bank.check_payment_status(6, "acct2", 3) is None
        two_days_in_future = Account.CASH_BACK_HOLDING_PERIOD_MS * 2
        assert (
            bank.check_payment_status(two_days_in_future, "acct1", 3)
            == "CASHBACK_RECEIVED"
        )
