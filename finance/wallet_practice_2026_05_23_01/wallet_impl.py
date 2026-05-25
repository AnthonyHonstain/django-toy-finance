from dataclasses import dataclass
from enum import Enum
from uuid import UUID, uuid4

from finance.wallet_practice_2026_05_23_01.wallet_interface import WalletInterface


class TransactionType(str, Enum):
    CREDIT = "CREDIT"
    PURCHASE = "PURCHASE"
    TRANSFER_OUT = "TRANSFER_OUT"
    TRANSFER_IN = "TRANSFER_IN"
    REVERSE = "REVERSE"


@dataclass
class Ledger:
    id: UUID
    timestamp: int
    user: str
    type: TransactionType
    amount: int
    transfer_to: str | None = None
    transfer_from: str | None = None
    transfer_id: UUID | None = None
    reverse_txn_id: UUID | None = None


@dataclass
class WalletTxnResponse:
    successful: bool
    id: UUID | None = None
    balance: int | None = None


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

    def get_balance(self) -> int:
        return self.balance

    def get_balance_at(self, at_timestamp: int | None = None) -> int | None:
        if at_timestamp is None:
            return self.balance

        ledger_found = False
        balance = 0
        for ledger in self.ledgers:
            if ledger.timestamp > at_timestamp:
                break
            ledger_found = True
            balance += ledger.amount

        if ledger_found:
            return balance
        return None

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
        self.global_ledger_lookup: dict[UUID, Ledger] = {}

    def credit(self, timestamp: int, user: str, amount: int) -> WalletTxnResponse:
        if user not in self.wallets:
            self.wallets[user] = Wallet(user)

        wallet: Wallet = self.wallets[user]
        id = uuid4()
        ledger = Ledger(id, timestamp, user, TransactionType.CREDIT, amount)
        wallet.add_ledger(ledger)
        self.global_ledger.append(ledger)
        self.global_ledger_lookup[ledger.id] = ledger
        return WalletTxnResponse(True, id, wallet.get_balance())

    def purchase(self, timestamp: int, user: str, amount: int) -> WalletTxnResponse:
        if user not in self.wallets:
            return WalletTxnResponse(False)

        wallet: Wallet = self.wallets[user]
        if wallet.get_balance() < amount:
            return WalletTxnResponse(False)

        id = uuid4()
        ledger = Ledger(id, timestamp, user, TransactionType.PURCHASE, -amount)
        wallet.add_ledger(ledger)
        self.global_ledger.append(ledger)
        self.global_ledger_lookup[ledger.id] = ledger
        return WalletTxnResponse(True, id, wallet.get_balance())

    def transfer(
        self, timestamp: int, source: str, destination: str, amount: int
    ) -> WalletTxnResponse:
        if source not in self.wallets:
            return WalletTxnResponse(False)
        if destination not in self.wallets:
            self.wallets[destination] = Wallet(destination)

        source_wallet = self.wallets[source]
        destination_wallet = self.wallets[destination]

        if source_wallet.get_balance() < amount:
            return WalletTxnResponse(False)

        txf_out_id = uuid4()
        txf_in_id = uuid4()
        ledger_out = Ledger(
            txf_out_id,
            timestamp,
            source,
            TransactionType.TRANSFER_OUT,
            -amount,
            transfer_to=destination,
            transfer_id=txf_in_id,
        )
        ledger_in = Ledger(
            txf_in_id,
            timestamp,
            destination,
            TransactionType.TRANSFER_IN,
            amount,
            transfer_from=source,
            transfer_id=txf_out_id,
        )
        source_wallet.add_ledger(ledger_out)
        destination_wallet.add_ledger(ledger_in)

        self.global_ledger.append(ledger_out)
        self.global_ledger_lookup[ledger_out.id] = ledger_out
        self.global_ledger.append(ledger_in)
        self.global_ledger_lookup[ledger_in.id] = ledger_in
        return WalletTxnResponse(True, txf_out_id, source_wallet.get_balance())

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
        return wallet.get_balance_at(at_timestamp)

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

    def transaction(self, timestamp: int, transaction_id: UUID) -> str | None:
        raise NotImplementedError

    def reverse(self, timestamp: int, transaction_id: UUID) -> bool:
        # Planning - I want to :
        #  * keep the append only nature of the ledger, I am going to try reverse with a reverse transaction
        ledger = self.global_ledger_lookup.get(transaction_id, None)
        if ledger is None:
            return False

        wallet = self.wallets[ledger.user]

        # Start with credit type - the transfer reversal might be sufficiently distinct to
        # justify breaking it out to a function.
        if ledger.type in (TransactionType.CREDIT, TransactionType.PURCHASE):
            if ledger.reverse_txn_id:
                # This has already been reversed.
                return False

            # We have to stop if the reversal would take us below negative
            # Example - we can't reverse a credit if doing so would invalid purchases later.
            balance = wallet.get_balance()
            if balance - ledger.amount < 0:
                return False

            reverse_id = uuid4()
            ledger.reverse_txn_id = reverse_id

            reverse_ledger = Ledger(
                reverse_id,
                timestamp,
                ledger.user,
                TransactionType.REVERSE,
                -ledger.amount,
                reverse_txn_id=ledger.id,
            )
            wallet.add_ledger(reverse_ledger)
            self.global_ledger.append(reverse_ledger)
            self.global_ledger_lookup[reverse_ledger.id] = reverse_ledger
            return True

        return False
