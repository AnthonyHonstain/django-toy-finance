import uuid
from collections import defaultdict
from operator import itemgetter
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

     2026-05-16 Starting again and picking up where I left off.
     0717-0729 starting on transfer
     * This went pretty well, left a callout that the ledge will probably need
       another abstraction around it to optimize.
     0729-0801 starting on stop_customers
     * got stuck on a few things - both cases I had to use repl / scratch to work it out
     ** stuck on sort
     ** stuck on slice

    """

    def __init__(self) -> None:
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
        source_balance = self._current_sum(0, source)
        if source_balance < amount:
            return None

        new_source_ledger = Ledger(uuid.uuid4(), timestamp, source, -amount)
        # Because we don't have any abstraction around the ledge and user lookup
        # we can just append a new ledger for the user, but this will probably have
        # to be revisited shortly since we O(n) the entire ledger for everything.
        new_destination_ledger = Ledger(uuid.uuid4(), timestamp, destination, amount)
        self._add_ledger(new_source_ledger)
        self._add_ledger(new_destination_ledger)

        return source_balance - amount

    def balance(self, timestamp: int, user: str) -> int:
        return self._current_sum(timestamp, user)

    def top_customers(self, timestamp: int, k: int) -> list[str]:
        customer_balances: dict[str, int] = defaultdict(int)
        for ledger in self.global_ledger:
            customer_balances[ledger.user] += ledger.amount

        customer_balance_values = list(customer_balances.items())
        customer_balance_values.sort()
        sorted_balances = sorted(
            customer_balance_values, key=itemgetter(1), reverse=True
        )

        # Struggling to remember the options to sort in Python
        # list(customer_balance_values).sort()
        # foo = list(customer_balance_values)
        # foo.sort()
        # foo
        # Out[5]: [('a', 100), ('b', 100), ('c', 100)]
        # foo.sort(reverse=True)
        # foo
        # Out[12]: [('c', 102), ('b', 101), ('a', 100)]
        # Started a scratch pad, got lucky
        # bar = [('a', 5), ('b', 6), ('c', 6), ('d', 6), ('e', 10)]
        # sorted_bar = sorted(bar, key=itemgetter(1,0), reverse=True)
        # print(bar)
        # print(sorted_bar) # [('e', 10), ('d', 6), ('c', 6), ('b', 6), ('a', 5)]
        #
        #
        # bar = [('a', 5), ('b', 6), ('c', 6), ('d', 6), ('e', 10)]
        # bar.sort()
        # sorted_bar = sorted(bar, key=itemgetter(1), reverse=True)
        # print(bar)
        # print(sorted_bar) # [('e', 10), ('b', 6), ('c', 6), ('d', 6), ('a', 5)]

        # Trying to remember the slice options
        # used scratch to
        # foo = list(range(10))
        # print(foo)
        # print(foo[:3])
        result = []
        for customer, amount in sorted_balances[:k]:
            result.append(customer)
        return result
