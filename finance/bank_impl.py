from dataclasses import dataclass
from math import floor
from enum import Enum, auto
from finance.bank_interface import BankInterface


class LedgerType(Enum):
    TRANSFER = auto()
    CASH_BACK = auto()


@dataclass
class Ledger:
    timestamp: int
    user_account: str
    amount: int
    ledger_type: LedgerType


@dataclass
class AccountBalance:
    user_account: str
    spend: int


class Account:

    CASH_BACK_HOLDING_PERIOD_MS = 86400000

    def __init__(self, account_name: str):
        self.account_name = account_name
        self.ledger_list: list[Ledger] = []

    def add(self, ledger: Ledger) -> None:
        self.ledger_list.append(ledger)

    def calculate_balance(self, timestamp: int) -> int:
        current_balance = 0
        for ledger in self.ledger_list:
            if ledger.ledger_type == LedgerType.TRANSFER:
                current_balance += ledger.amount
            elif ledger.ledger_type == LedgerType.CASH_BACK and self.cashback_is_active(
                timestamp, ledger
            ):
                current_balance += ledger.amount

        return current_balance

    def calculate_spend(self) -> int:
        current_spend = 0
        for ledger in self.ledger_list:
            if ledger.amount < 0:
                current_spend += abs(ledger.amount)
        return current_spend

    def get_payment_by_timestamp(self, timestamp: int) -> Ledger | None:
        for ledger in self.ledger_list:
            if ledger.timestamp == timestamp:
                return ledger
        return None

    def cashback_is_active(self, timestamp: int, ledger: Ledger) -> bool:
        cash_back_active_ms = ledger.timestamp + self.CASH_BACK_HOLDING_PERIOD_MS
        return cash_back_active_ms < timestamp

    def _debug_ledger(self):
        print()
        print(f"Dump ledger for {self.account_name}")
        for ledger in self.ledger_list:
            print(ledger)
        print()


class BankImpl(BankInterface):
    def __init__(self):
        self.account_map: dict[str, Account] = {}

    def add(self, timestamp: int, user_account: str, amount: int) -> int:
        if user_account not in self.account_map:
            self.account_map[user_account] = Account(user_account)
        account = self.account_map[user_account]
        new_ledger = Ledger(timestamp, user_account, amount, LedgerType.TRANSFER)
        account.add(new_ledger)
        # account._debug_ledger()
        return account.calculate_balance(timestamp)

    def transfer(
        self,
        timestamp: int,
        user_account_source: str,
        user_account_destination: str,
        amount: int,
    ) -> int | None:
        if user_account_source not in self.account_map:
            return None
        if user_account_destination not in self.account_map:
            return None

        account_source = self.account_map[user_account_source]
        account_dest = self.account_map[user_account_destination]
        source_balance = account_source.calculate_balance(timestamp)
        if source_balance < amount:
            return None

        account_source.add(
            Ledger(timestamp, user_account_source, -amount, LedgerType.TRANSFER)
        )
        new_ledger_cashback = Ledger(
            timestamp, user_account_source, floor(amount * 0.02), LedgerType.CASH_BACK
        )
        account_source.add(new_ledger_cashback)
        account_dest.add(
            Ledger(timestamp, user_account_destination, amount, LedgerType.TRANSFER)
        )
        return source_balance - amount

    def top_spenders(self, timestamp: int, number_of_top_spenders: int) -> list[str]:
        account_balances = []
        for user_account, account in self.account_map.items():
            spend = account.calculate_spend()
            account_balances.append(AccountBalance(user_account, spend))
        account_balances.sort(key=lambda ab: (-ab.spend, ab.user_account))
        result = []
        for account_balance in account_balances[:number_of_top_spenders]:
            result.append(f"{account_balance.user_account}({account_balance.spend})")
        return result

    def withdraw(self, timestamp: int, user_account: str, amount: int) -> int | None:
        if amount <= 0:
            raise ValueError()
        if user_account not in self.account_map:
            return None
        account = self.account_map[user_account]
        source_balance = account.calculate_balance(timestamp)
        if source_balance < amount:
            return None

        new_ledger = Ledger(timestamp, user_account, -amount, LedgerType.TRANSFER)
        account.add(new_ledger)
        new_ledger_cashback = Ledger(
            timestamp, user_account, floor(amount * 0.02), LedgerType.CASH_BACK
        )
        account.add(new_ledger_cashback)
        return account.calculate_balance(timestamp)

    def check_payment_status(
        self, timestamp: int, user_account: str, payment_timestamp: int
    ) -> str | None:
        if user_account not in self.account_map:
            return None
        account = self.account_map[user_account]
        ledger = account.get_payment_by_timestamp(payment_timestamp)
        if not ledger:
            return None
        elif account.cashback_is_active(timestamp, ledger):
            return "CASHBACK_RECEIVED"
        else:
            return "IN_PROGRESS"
