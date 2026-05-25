from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass
class WalletTxnResponse:
    successful: bool
    id: UUID | None = None
    balance: int | None = None


class WalletInterface(ABC):
    """Contract for a wallet practice implementation.

    Timestamps are included to mimic interview-style APIs where operations are
    ordered externally. Mutating operations may assume calls arrive in timestamp
    order unless a test explicitly says otherwise.

    Reference scenarios:

    * A new user starts with no account history.
    * `credit(1, "alice", 500)` returns a successful response with balance 500.
    * After that, `purchase(2, "alice", 200)` returns a successful response
      with balance 300.
    * `purchase(3, "alice", 400)` returns an unsuccessful response and leaves
      Alice at 300.
    * `transfer(4, "alice", "bob", 100)` returns a successful response with
      Alice's balance, 200.
    * After the transfer, `balance(5, "bob")` returns 100.
    * Top customers are ranked by total successful purchase amount, descending.
    * Ties in top customers are broken lexicographically by user ID.
    """

    @abstractmethod
    def credit(self, timestamp: int, user: str, amount: int) -> WalletTxnResponse:
        """Add `amount` to `user` and return transaction metadata."""

    @abstractmethod
    def purchase(self, timestamp: int, user: str, amount: int) -> WalletTxnResponse:
        """Spend `amount` if the user has enough money.

        Return a successful response with the transaction ID and remaining
        balance. Return an unsuccessful response when funds are insufficient,
        and do not change the balance.
        """

    @abstractmethod
    def transfer(
        self, timestamp: int, source: str, destination: str, amount: int
    ) -> WalletTxnResponse:
        """Move money from `source` to `destination`.

        Return a successful response with the source user's remaining balance.
        Return an unsuccessful response when the source user does not exist or
        lacks funds. Creating the destination user during a successful transfer
        is acceptable for this practice run.
        """

    @abstractmethod
    def balance(self, timestamp: int, user: str) -> int | None:
        """Return the user's current available balance.

        Return None if the user does not exist.
        """

    @abstractmethod
    def balance_at(self, timestamp: int, user: str, at_timestamp: int) -> int | None:
        """Return the user's balance as of `at_timestamp`.

        Return None if the user did not exist yet.
        """

    @abstractmethod
    def statement(
        self, timestamp: int, user: str, start_timestamp: int, end_timestamp: int
    ) -> list[str]:
        """Return formatted ledger entries for one user in an inclusive range.

        Statement rows should be sorted by timestamp and should not include
        other users' unrelated activity. Row formatting is intentionally simple:

        * `"{timestamp}: CREDIT {amount} balance={balance}"`
        * `"{timestamp}: PURCHASE {amount} balance={balance}"`
        * `"{timestamp}: TRANSFER_OUT {amount} to {user} balance={balance}"`
        * `"{timestamp}: TRANSFER_IN {amount} from {user} balance={balance}"`
        """

    @abstractmethod
    def top_customers(self, timestamp: int, k: int) -> list[str]:
        """Return the top `k` users by gross purchase activity.

        Only successful purchases count. Credits and transfers do not count.
        Format each result as `"user(amount)"`.
        """

    @abstractmethod
    def transaction(self, timestamp: int, transaction_id: UUID) -> str | None:
        """Return a formatted description for one transaction.

        Return None if `transaction_id` is unknown.

        Phase 3 modeling pressure: decide whether a transaction ID identifies
        one ledger row or one business transaction. A transfer has two ledger
        rows, but it may be more useful as one conceptual transaction.
        """

    @abstractmethod
    def reverse(self, timestamp: int, transaction_id: UUID) -> bool:
        """Reverse a prior transaction if it is safe to do so.

        Return True when a reversal is recorded. Return False when the
        transaction is unknown, already reversed, or cannot be safely reversed.

        Suggested Phase 3 scenarios:
        * Reversing a purchase restores the user's balance.
        * Reversing a transfer moves money back from destination to source.
        * Reversing a transfer fails if the destination no longer has enough
          balance to return the funds.
        * Reversing the same transaction twice fails cleanly.
        """
