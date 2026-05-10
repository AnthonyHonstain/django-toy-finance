import collections
from collections import defaultdict
from dataclasses import dataclass
from typing import Literal

from finance.wallet_practice_2025_10_12_01.wallet_interface import WalletInterface

LedgerType = Literal["CREDIT", "PURCHASE", "TRANSFER"]


@dataclass
class LedgerEntry:
    timestamp: int
    type: LedgerType
    source_user: str | None = None
    destination_user: str | None = None
    source_amount: int = 0
    destination_amount: int = 0


class UserWallet:
    def __init__(self, user: str):
        self.user = user
        self.ledger: list[LedgerEntry] = []

    def add_ledger(self, ledger: LedgerEntry) -> None:
        self.ledger.append(ledger)

    def calculate_balance(self) -> int:
        result = 0
        for ledger in self.ledger:
            if ledger.type == "CREDIT":
                result += ledger.destination_amount
            elif ledger.type == "PURCHASE":
                result -= ledger.source_amount
            elif ledger.type == "TRANSFER":
                if ledger.source_user == self.user:
                    result -= ledger.source_amount
                else:
                    result += ledger.destination_amount
        return result

    def sum_purchase_activity(self) -> int:
        result = 0
        for ledger in self.ledger:
            if ledger.type == "PURCHASE":
                result += ledger.source_amount
        return result


class WalletImpl(WalletInterface):

    def __init__(self):
        super().__init__()
        self.user_wallets: dict[str, UserWallet] = {}

    def credit(self, timestamp: int, user: str, amount: int) -> int:
        if user not in self.user_wallets:
            self.user_wallets[user] = UserWallet(user)
        wallet = self.user_wallets[user]

        leger_entry = LedgerEntry(
            timestamp=timestamp,
            type="CREDIT",
            destination_user=user,
            destination_amount=amount,
        )
        wallet.add_ledger(leger_entry)
        return wallet.calculate_balance()

    def purchase(self, timestamp: int, user: str, amount: int) -> int | None:
        if user not in self.user_wallets:
            self.user_wallets[user] = UserWallet(user)
        wallet = self.user_wallets[user]
        balance = wallet.calculate_balance()
        if balance < amount:
            return None

        leger_entry = LedgerEntry(
            timestamp=timestamp,
            type="PURCHASE",
            source_user=user,
            source_amount=amount,
        )
        wallet.add_ledger(leger_entry)
        return wallet.calculate_balance()

    def balance(self, timestamp: int, user: str) -> int:
        if user not in self.user_wallets:
            return 0
        wallet = self.user_wallets[user]
        return wallet.calculate_balance()

    def transfer(
        self, timestamp: int, source: str, dest: str, amount: int
    ) -> int | None:
        if source not in self.user_wallets:
            # Nothing to do if we have no source user to take funds from.
            return None
        source_wallet = self.user_wallets[source]
        if dest not in self.user_wallets:
            self.user_wallets[dest] = UserWallet(dest)
        destination_wallet = self.user_wallets[dest]

        source_balance = source_wallet.calculate_balance()
        if source_balance < amount:
            # Insufficient funds.
            return None

        source_leger_entry = LedgerEntry(
            timestamp=timestamp,
            type="TRANSFER",
            source_user=source,
            source_amount=amount,
            destination_user=dest,
            destination_amount=amount,
        )
        source_wallet.add_ledger(source_leger_entry)

        dest_leger_entry = LedgerEntry(
            timestamp=timestamp,
            type="TRANSFER",
            source_user=source,
            source_amount=amount,
            destination_user=dest,
            destination_amount=amount,
        )
        destination_wallet.add_ledger(dest_leger_entry)
        return source_wallet.calculate_balance()

    def top_customers(self, timestamp: int, k: int) -> list[str]:
        """
        We ended up doing a bunch of gymnastics here, we calculate all the users
        purchase sum.

        Then we have this constraint of needing to sort them by purchase order first, then
        for ties, we need to sort lexicographically. Which ends up being a mix sort orders,
        so like purchase_sum is descending order, and ties should be on account name ascending.

        This solution has more moving parts than I wanted, and ended up with the
        following data structures.
        * Build dict A of purchase_sum -> [user1, user2, ...]
        * List B of sorted keys to dict A
        * Build dict C of purchase_sum -> stack[user1, user2, ...] and sort the stack
        * while loop deconstructing the List B and dict C
        """
        sum_to_user: defaultdict[int, list[str]] = defaultdict(list)
        for user, wallet in self.user_wallets.items():
            purchase_sum = wallet.sum_purchase_activity()
            sum_to_user[purchase_sum].append(user)

        # This logic caused me a lot of trouble ------------------------------------
        purchase_sums = list(sum_to_user.keys())
        purchase_sums.sort()

        purchase_sum_stack_map: dict[int, collections.deque[str]] = {}
        for purchase_sum, user_stack in sum_to_user.items():
            user_stack.sort()
            purchase_sum_stack_map[purchase_sum] = collections.deque(user_stack)

        # print(purchase_sum_stack_map)

        result: list[str] = []
        while len(result) < k and purchase_sum_stack_map:
            current = purchase_sums[-1]
            user = purchase_sum_stack_map[current].popleft()
            # Clean things up if we have the last one
            if not purchase_sum_stack_map[current]:
                purchase_sums.pop()
                del purchase_sum_stack_map[current]

            result.append(f"{user}({current})")
        return result
