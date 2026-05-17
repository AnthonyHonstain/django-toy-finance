from abc import ABC, abstractmethod


class WalletInterface(ABC):
    """Contract for a wallet practice implementation.

    Timestamps are included to mimic interview-style APIs where operations are
    ordered externally. The starter scenarios do not require historical balance
    lookups; treating operations as happening in call order is enough for phase 1.
    One ambiguity in the prompt is whether a timestamp means "the balance as of
    this point in time" or "the ledger entries after this checkpoint." For this
    practice run, the implementation follows the checkpoint interpretation so a
    future compacted balance could be combined with ledger entries after the
    checkpoint timestamp.

    Practice note: if revisiting this exercise, a "balance as of timestamp"
    method makes more sense when framed as a customer support or audit scenario,
    such as explaining why a purchase was declined at a specific point in the
    account history. Plain integer timestamps are contrived, but they keep the
    interview problem small; real time handling or UUID-plus-time ordering would
    add a lot of incidental complexity.

    Reference scenarios:

    * A new user starts with balance 0.
    * `credit(1, "alice", 500)` returns 500.
    * After that, `purchase(2, "alice", 200)` returns 300.
    * `purchase(3, "alice", 400)` returns None and leaves Alice at 300.
    * `transfer(4, "alice", "bob", 100)` returns Alice's balance, 200.
    * After the transfer, `balance(5, "bob")` returns 100.
    * Top customers are ranked by total purchase amount, descending.
    * Ties in top customers are broken lexicographically by user ID.
    """

    @abstractmethod
    def credit(self, timestamp: int, user: str, amount: int) -> int:
        """Add `amount` to `user` and return the user's current balance.

        Scenario:
        * `credit(10, "u1", 0)` returns 0.
        * `credit(11, "u1", 500)` returns 500.
        """

    @abstractmethod
    def purchase(self, timestamp: int, user: str, amount: int) -> int | None:
        """Spend `amount` if the user has enough money.

        Return the remaining balance on success. Return None when funds are
        insufficient, and do not change the balance.

        Scenario:
        * Start with `credit(1, "u1", 1000)`.
        * `purchase(2, "u1", 400)` returns 600.
        * `purchase(3, "u1", 700)` returns None.
        * `balance(4, "u1")` still returns 600.
        """

    @abstractmethod
    def transfer(
        self, timestamp: int, source: str, destination: str, amount: int
    ) -> int | None:
        """Move money from `source` to `destination`.

        Return the source user's remaining balance on success. Return None when
        the source user does not exist or lacks funds. Creating the destination
        user during a successful transfer is acceptable for this practice run.

        Scenario:
        * Start with `credit(1, "a", 500)`.
        * `transfer(2, "a", "b", 200)` returns 300.
        * `balance(3, "a")` returns 300.
        * `balance(3, "b")` returns 200.
        """

    @abstractmethod
    def balance(self, timestamp: int, user: str) -> int | None:
        """Return the user's current available balance.

        Scenario:
        * `balance(1, "missing")` returns 0.
        """

    @abstractmethod
    def balance_at(self, timestamp: int, user: str, at_timestamp: int) -> int | None:
        """Return the user's balance as of `at_timestamp`.

        This is the audit/customer support version of balance: it answers what
        the wallet would have shown at a specific point in account history.
        Return None if the user did not exist yet.

        Scenario:
        * `credit(1, "u1", 500)` returns 500.
        * `purchase(3, "u1", 200)` returns 300.
        * `balance_at(10, "u1", 2)` returns 500.
        * `balance_at(10, "u1", 3)` returns 300.
        * `balance_at(10, "missing", 3)` returns None.

        UPDATE from Anthony - the timestamp was just robotically put in there, but
        unlike the other operations the mutate the wallet, it makes less sense
        to have some explicit timestamp argument for a read only operation. Its even
        more confusing since it sits adjacent to balance(timestamp, ..) where timestamp
        had a clear behavior. The API For balance and balance_at ended up in a silly place.
        I guess thats the problem with interview problems, you make try to make allowances
        for the time pressure, and in this case you see were me using an agent to
        setup and proxy the practice resulted in something confusing.
        * Not going to try and unwind all these here since I think there was value in how
          things looked when I first tackled it.
        """

    @abstractmethod
    def statement(
        self, timestamp: int, user: str, start_timestamp: int, end_timestamp: int
    ) -> list[str]:
        """Return formatted ledger entries for one user in an inclusive range.

        Statement rows should be sorted by timestamp and should not include
        other users' unrelated activity. The exact formatting is intentionally
        simple for practice and can evolve during implementation.

        Scenario:
        * `credit(1, "u1", 500)`
        * `purchase(2, "u1", 200)`
        * `credit(3, "u2", 999)`
        * `statement(10, "u1", 1, 2)` returns entries for u1's credit and
          purchase only.
        """

    @abstractmethod
    def top_customers(self, timestamp: int, k: int) -> list[str]:
        """Return the top `k` users by gross purchase activity.

        Only successful purchases count. Credits and transfers do not count.
        Format each result as `"user(amount)"`.

        Scenario:
        * If Alice has purchases totaling 600 and Bob has purchases totaling
          700, `top_customers(..., 2)` returns `["bob(700)", "alice(600)"]`.
        * If two users both have 0 purchase activity, sort them by user ID.
        """
