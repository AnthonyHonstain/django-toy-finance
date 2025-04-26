from abc import ABC, abstractmethod


class BankInterface(ABC):

    @abstractmethod
    def add(self, timestamp: int, user_account: str, amount: int) -> int | None:
        pass

    @abstractmethod
    def transfer(
        self,
        timestamp: int,
        user_account_source: str,
        user_account_destination: str,
        amount: int,
    ) -> int | None:
        pass

    @abstractmethod
    def top_spenders(self, timestamp: int, number_of_top_spenders: int) -> list[str]:
        pass

    @abstractmethod
    def withdraw(self, timestamp: int, user_account: str, amount: int) -> int | None:
        pass

    @abstractmethod
    def check_payment_status(
        self, timestamp: int, user_account: str, payment_timestamp: int
    ) -> str | None:
        pass
