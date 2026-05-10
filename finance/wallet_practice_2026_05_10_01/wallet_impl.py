import uuid
from typing import List
from uuid import UUID

from dataclasses import dataclass

from finance.wallet_practice_2026_05_10_01.wallet_interface import WalletInterface


@dataclass
class Ledger:
    id: UUID
    timestamp: int
    user: str
    amount: int


class WalletImpl(WalletInterface):
    """
    Implementation journal
    0945-1011 Starting with credit
     * laying down the ledger for double entry accounting first.
     * Got hung up briefly on creating a UUID for the dataclass id.
     * Hung up on the dataclass, that was because I let intellij auto import dataclass from black.
     * Copy and paste error where I was trying to decide if balance should be able to calculate sum based on
       arbitrary timestamp (only use ledger's after that data). Only reason I could think of is if we had
       some sort of rollup/aggregator and we could check-point so that we didn't have to sum all history.
     * RESULT - got an initial implementation of credit and balance in place.

    1011-1019 Working on purchase
     * This one went pretty easy, not hangups, and added a more complicated test.
    """

    def __init__(self):
        self.global_ledger: List[Ledger] = list()

    def _add_ledger(self, ledger: Ledger) -> None:
        self.global_ledger.append(ledger)

    def _current_sum(self, timestamp: int, user: str) -> int:
        result = 0
        for ledger in self.global_ledger:
            if ledger.timestamp >= timestamp and ledger.user == user:
                result += ledger.amount
        return result

    def credit(self, timestamp: int, user: str, amount: int) -> int:
        new_ledger = Ledger(uuid.uuid4(), timestamp, user, amount)
        self._add_ledger(new_ledger)

        return self._current_sum(0, user)

    def purchase(self, timestamp: int, user: str, amount: int) -> int | None:
        current_balance = self._current_sum(0, user)

        if current_balance < amount:
            return None

        new_ledger = Ledger(uuid.uuid4(), timestamp, user, -amount)
        self._add_ledger(new_ledger)
        return current_balance - amount

    def transfer(
        self, timestamp: int, source: str, destination: str, amount: int
    ) -> int | None:
        raise NotImplementedError

    def balance(self, timestamp: int, user: str) -> int:
        return self._current_sum(timestamp, user)

    def top_customers(self, timestamp: int, k: int) -> list[str]:
        raise NotImplementedError
