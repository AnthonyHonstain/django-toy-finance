from abc import ABC, abstractmethod


class WalletInterface(ABC):
    @abstractmethod
    def credit(self, timestamp: int, user: str, amount: int) -> int:
        """Add positive amount to user's wallet immediately and return current balance at `timestamp`."""

    @abstractmethod
    def purchase(self, timestamp: int, user: str, amount: int) -> int | None:
        """Spend amount from user's wallet if sufficient; return remaining balance; otherwise None."""

    @abstractmethod
    def transfer(
        self, timestamp: int, source: str, dest: str, amount: int
    ) -> int | None:
        """Move amount from source to dest if source has sufficient funds; return source's remaining balance; otherwise None."""

    @abstractmethod
    def balance(self, timestamp: int, user: str) -> int:
        """Return user's available balance at `timestamp`."""

    @abstractmethod
    def top_customers(self, timestamp: int, k: int) -> list[str]:
        """Return top `k` users by total *gross purchases* (sum of purchase amounts, ignoring credits/transfers),
        tie-break by lexicographic user id. Format: 'user(amount)'."""
