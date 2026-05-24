from dataclasses import dataclass
from enum import Enum
from uuid import UUID, uuid4

from finance.wallet_practice_2026_05_23_01.wallet_interface import WalletInterface


class TransactionType(str, Enum):
    CREDIT = "CREDIT"
    PURCHASE = "PURCHASE"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"


@dataclass
class Ledger:
    id: UUID
    timestamp: int
    user: str
    type: TransactionType
    amount: int
    transfer_to: str | None = None
    transfer_from: str | None = None


class Wallet:
    """Idea here is to organize the ledger and key data per user."""

    def __init__(self, user: str) -> None:
        self.user = user
        self.ledgers: list[Ledger] = []
        self.balance = 0
        self.purchase_sum = 0

    def add_ledger(self, ledger: Ledger) -> None:
        self.ledgers.append(ledger)
        self.balance += ledger.amount

        if ledger.type == TransactionType.PURCHASE:
            self.purchase_sum += abs(ledger.amount)

    def get_balance(self, at_timestamp: int | None = None) -> int:
        # On the fence about using a getter, vs just grabbinb the balance.
        if at_timestamp is None:
            return self.balance

        balance = 0
        for ledger in self.ledgers:
            if ledger.timestamp > at_timestamp:
                break
            balance += ledger.amount
        return balance

    def statement(self, start_timestamp: int, end_timestamp: int) -> list[str]:
        result = []
        balance = 0
        for ledger in self.ledgers:
            if ledger.timestamp > end_timestamp:
                break

            balance += ledger.amount
            if ledger.timestamp >= start_timestamp:
                if ledger.type == TransactionType.CREDIT:
                    result.append(
                        f"{ledger.timestamp}: {ledger.type.name} {ledger.amount} balance={balance}"
                    )
                elif ledger.type == TransactionType.PURCHASE:
                    result.append(
                        f"{ledger.timestamp}: {ledger.type.name} {abs(ledger.amount)} balance={balance}"
                    )
                elif ledger.type == TransactionType.TRANSFER_OUT:
                    result.append(
                        f"{ledger.timestamp}: {ledger.type.name} {abs(ledger.amount)} to {ledger.transfer_to} balance={balance}"
                    )
                elif ledger.type == TransactionType.TRANSFER_IN:
                    result.append(
                        f"{ledger.timestamp}: {ledger.type.name} {ledger.amount} from {ledger.transfer_from} balance={balance}"
                    )
        return result


class WalletImpl(WalletInterface):
    """Fresh implementation surface for the 2026-05-23 practice run."""

    def __init__(self) -> None:
        self.global_ledger: list[Ledger] = []
        self.wallets: dict[str, Wallet] = {}

    def credit(self, timestamp: int, user: str, amount: int) -> int:
        if user not in self.wallets:
            self.wallets[user] = Wallet(user)

        wallet: Wallet = self.wallets[user]
        ledger = Ledger(uuid4(), timestamp, user, TransactionType.CREDIT, amount)
        wallet.add_ledger(ledger)
        self.global_ledger.append(ledger)
        return wallet.get_balance()

    def purchase(self, timestamp: int, user: str, amount: int) -> int | None:
        if user not in self.wallets:
            return None

        wallet: Wallet = self.wallets[user]
        if wallet.get_balance() < amount:
            return None

        ledger = Ledger(uuid4(), timestamp, user, TransactionType.PURCHASE, -amount)
        wallet.add_ledger(ledger)
        self.global_ledger.append(ledger)
        return wallet.get_balance()

    def transfer(
        self, timestamp: int, source: str, destination: str, amount: int
    ) -> int | None:
        if source not in self.wallets:
            return None
        if destination not in self.wallets:
            self.wallets[destination] = Wallet(destination)

        source_wallet = self.wallets[source]
        destination_wallet = self.wallets[destination]

        ledger_out = Ledger(
            uuid4(),
            timestamp,
            source,
            TransactionType.TRANSFER_OUT,
            -amount,
            transfer_to=destination,
        )
        ledger_in = Ledger(
            uuid4(),
            timestamp,
            destination,
            TransactionType.TRANSFER_IN,
            amount,
            transfer_from=source,
        )
        source_wallet.add_ledger(ledger_out)
        destination_wallet.add_ledger(ledger_in)

        self.global_ledger.append(ledger_out)
        self.global_ledger.append(ledger_in)
        return source_wallet.get_balance()

    def balance(self, timestamp: int, user: str) -> int | None:
        # treating timestamp as just a record for logging, and that
        # it was probably included for api consistency.
        if user not in self.wallets:
            return None

        return self.wallets[user].get_balance()

    def balance_at(self, timestamp: int, user: str, at_timestamp: int) -> int | None:
        if user not in self.wallets:
            return None

        wallet: Wallet = self.wallets[user]
        return wallet.get_balance(at_timestamp)

    def statement(
        self, timestamp: int, user: str, start_timestamp: int, end_timestamp: int
    ) -> list[str]:
        if user not in self.wallets:
            return []

        wallet: Wallet = self.wallets[user]
        return wallet.statement(start_timestamp, end_timestamp)

    def top_customers(self, timestamp: int, k: int) -> list[str]:
        # I Could go two way here (at least two)
        #  1) I could just walk the global ledger for purchases by customer
        #  2) I could pre-compute purchase sum on each wallet.
        # I think I want to try 2)
        temp_purchase_sum: list[tuple[str, int]] = []
        for user, wallet in self.wallets.items():
            # TODO - I broke convention with using the getters
            temp_purchase_sum.append((user, wallet.purchase_sum))

        sorted_purchase_sum = sorted(temp_purchase_sum, key=lambda x: (-x[1], x[0]))
        return list(map(lambda x: f"{x[0]}({x[1]})", sorted_purchase_sum[:k]))
