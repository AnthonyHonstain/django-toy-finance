from abc import ABC, abstractmethod


class WalletInterface(ABC):
    """Contract for a wallet practice implementation.

    Timestamps are included to mimic interview-style APIs where operations are
    ordered externally. The starter scenarios do not require historical balance
    lookups; treating operations as happening in call order is enough for phase 1.

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
    def balance(self, timestamp: int, user: str) -> int:
        """Return the user's current available balance.

        Scenario:
        * `balance(1, "missing")` returns 0.
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
