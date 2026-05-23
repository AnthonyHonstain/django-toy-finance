import uuid
from collections import defaultdict
from enum import Enum
from operator import itemgetter
from typing import List, Dict
from uuid import UUID

from dataclasses import dataclass

from finance.wallet_practice_2026_05_10_01.wallet_interface import WalletInterface


class OperationType(Enum):
    CREDIT = 1
    PURCHASE = 2
    TRANSFER_OUT = 3
    TRANSFER_IN = 4


@dataclass
class Ledger:
    id: UUID
    timestamp: int
    operation_type: OperationType
    user: str
    amount: int
    transfer_id: UUID | None


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

    2026-05-17 starting phase 2 with some new methods to implement
    0709-0740 starting balance_at
    * I don't like the initial way I am traversing the ledger
    * Didn't end up doing a significant restructure, but did rework how I handled None
      and retouched how I was doing balance. Recorded my lessons learned in the balance_at
      interface method comment.
    0740-0820 going to quickly do the statement
    * Oh its goin to force me to track more info in the ledger
    * Will add an enum
    * It also wants the from and the to user in the statement. PROBLEM I wasn't
      considering an easy way to get both ends of the transfer for this problem.
    * also did the top customer, I should have been more careful and just done
      the right thing in phase 1. My sorts were wrong

    AGENT review
    * Good phase 2 jump: OperationType and richer ledger rows were the right
      direction once statements and historical balance entered the API.
    * Strongest part was recognizing that transfer statements need both sides
      of a transfer, not just signed amounts.
    * Main contract issue: balance now returns None in some cases, but the
      interface still says it returns int.
    * Fragile spot: transfer_lookup depends on source/destination list ordering.
      A TransferPair or explicit source/destination fields would be sturdier.
    * Statement balances currently start at 0 for the requested range; a real
      statement probably needs an opening balance before start_timestamp.
    * top_customers is conceptually closer by counting purchases only, but still
      needs the interface format user(amount) and an unskipped contract test.

    2026-05-23 finish phase 2
    1000-1016 Cleaned up the rest phase 2, had to fix the discrepancy in top_purchase
    1016-1030
    * I didn't like the implementation of statement, the way we positionally look up the
      pair of transfers feels really error prone.
    * I also didn't like the way we traverse the entire ledger every time.
    * Idea here - do a cleanup / re-organization
    ** break the need for the transfer_lookup by expanding ledger
    ** break out each user to have their own ledger and aggregation.
    * You know what, its probably more clear to just rewrite it at this point, that
      way my initial mistakes are preserved for posterity.

    -- Code I abandoned
    class PersonalAccount:
        def __init__(self) -> None:
            self.ledgers: List[Ledger] = list()
            self.current_balance: int = 0

        def add_ledger(self, ledger: Ledger) -> None:
            self.ledgers.append(ledger)
            self.current_balance += ledger.amount

    self.personal_accounts: Dict[str, PersonalAccount] = dict()
    self.personal_accounts[ledger.user].add_ledger(ledger)
    """

    def __init__(self) -> None:
        self.global_ledger: List[Ledger] = list()
        self.transfer_lookup: Dict[UUID, list[Ledger]] = defaultdict(list)

    def _add_ledger(self, ledger: Ledger) -> None:
        self.global_ledger.append(ledger)
        if ledger.transfer_id:
            self.transfer_lookup[ledger.transfer_id].append(ledger)

    def _current_sum(
        self,
        beginning_timestamp_inclusive: int | None,
        ending_timestamp_inclusive: int | None,
        user: str,
    ) -> int | None:

        result = None
        for ledger in self.global_ledger:
            if ledger.user != user:
                continue

            after_beginning = self._after_beginning(
                beginning_timestamp_inclusive, ledger
            )
            before_ending = self._before_ending(ending_timestamp_inclusive, ledger)

            if after_beginning and before_ending:
                if result is None:
                    result = 0
                result += ledger.amount
        return result

    @staticmethod
    def _after_beginning(
        beginning_timestamp_inclusive: int | None, ledger: Ledger
    ) -> bool:
        after_beginning = True
        if (
            beginning_timestamp_inclusive
            and ledger.timestamp < beginning_timestamp_inclusive
        ):
            after_beginning = False
        return after_beginning

    @staticmethod
    def _before_ending(ending_timestamp_inclusive: int | None, ledger: Ledger) -> bool:
        before_ending = True
        if ending_timestamp_inclusive and ledger.timestamp > ending_timestamp_inclusive:
            before_ending = False
        return before_ending

    def credit(self, timestamp: int, user: str, amount: int) -> int:
        new_ledger = Ledger(
            uuid.uuid4(), timestamp, OperationType.CREDIT, user, amount, None
        )
        self._add_ledger(new_ledger)

        balance = self._current_sum(None, None, user)
        if balance is None:
            raise Exception("credit found no balance, something is wrong with ledger")
        return balance

    def purchase(self, timestamp: int, user: str, amount: int) -> int | None:
        current_balance = self._current_sum(None, None, user)

        if current_balance is None or current_balance < amount:
            return None

        new_ledger = Ledger(
            uuid.uuid4(), timestamp, OperationType.PURCHASE, user, -amount, None
        )
        self._add_ledger(new_ledger)
        return current_balance - amount

    def transfer(
        self, timestamp: int, source: str, destination: str, amount: int
    ) -> int | None:
        source_balance = self._current_sum(None, None, source)
        if source_balance is None or source_balance < amount:
            return None

        transfer_id = uuid.uuid4()
        new_source_ledger = Ledger(
            uuid.uuid4(),
            timestamp,
            OperationType.TRANSFER_OUT,
            source,
            -amount,
            transfer_id,
        )
        # Because we don't have any abstraction around the ledge and user lookup
        # we can just append a new ledger for the user, but this will probably have
        # to be revisited shortly since we O(n) the entire ledger for everything.
        new_destination_ledger = Ledger(
            uuid.uuid4(),
            timestamp,
            OperationType.TRANSFER_IN,
            destination,
            amount,
            transfer_id,
        )
        self._add_ledger(new_source_ledger)
        self._add_ledger(new_destination_ledger)

        return source_balance - amount

    def balance(self, timestamp: int, user: str) -> int | None:
        return self._current_sum(timestamp, None, user)

    def balance_at(self, timestamp: int, user: str, at_timestamp: int) -> int | None:
        return self._current_sum(None, at_timestamp, user)

    def statement(
        self, timestamp: int, user: str, start_timestamp: int, end_timestamp: int
    ) -> list[str]:
        result = []
        balance = 0
        for ledger in self.global_ledger:
            if ledger.user != user:
                continue

            after_beginning = self._after_beginning(start_timestamp, ledger)
            before_ending = self._before_ending(end_timestamp, ledger)

            if after_beginning and before_ending:
                balance += ledger.amount
                if ledger.operation_type == OperationType.CREDIT:
                    result.append(
                        f"{ledger.timestamp}: CREDIT {ledger.amount} balance={balance}"
                    )
                elif ledger.operation_type == OperationType.PURCHASE:
                    result.append(
                        f"{ledger.timestamp}: PURCHASE {-ledger.amount} balance={balance}"
                    )
                elif ledger.operation_type == OperationType.TRANSFER_IN:
                    if not ledger.transfer_id:
                        raise Exception("Transfer ledger is missing transfer id")
                    both_ledgers = self.transfer_lookup[ledger.transfer_id]
                    # WARNING - I am playing fast an loose with implied ordering of transfer_lookup list
                    src_ledger = both_ledgers[0]
                    result.append(
                        f"{ledger.timestamp}: TRANSFER_IN {ledger.amount} from {src_ledger.user} balance={balance}"
                    )
                elif ledger.operation_type == OperationType.TRANSFER_OUT:
                    if not ledger.transfer_id:
                        raise Exception("Transfer ledger is missing transfer id")
                    both_ledgers = self.transfer_lookup[ledger.transfer_id]
                    # WARNING - I am playing fast an loose with implied ordering of transfer_lookup list
                    dest_ledger = both_ledgers[1]
                    result.append(
                        f"{ledger.timestamp}: TRANSFER_OUT {-ledger.amount} to {dest_ledger.user} balance={balance}"
                    )
        return result

    def top_customers(self, timestamp: int, k: int) -> list[str]:
        customer_balances: dict[str, int] = defaultdict(int)
        for ledger in self.global_ledger:
            if ledger.operation_type == OperationType.PURCHASE:
                customer_balances[ledger.user] += abs(ledger.amount)

        customer_balance_values = list(customer_balances.items())
        sorted_balances = sorted(customer_balance_values, key=lambda x: (-x[1], x[0]))

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
            result.append(f"{customer}({amount})")
        return result
