from __future__ import annotations

from abc import ABC, abstractmethod


class BaseSet(ABC):
    @classmethod
    @abstractmethod
    def from_string(cls, data: str) -> BaseSet:
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

    @abstractmethod
    def add(self, element: object) -> None:
        pass

    @abstractmethod
    def remove(self, element: object) -> None:
        pass

    @abstractmethod
    def cardinality(self) -> int:
        pass

    @abstractmethod
    def __getitem__(self, element: object) -> bool:
        pass

    @abstractmethod
    def __add__(self, other: BaseSet) -> BaseSet:
        pass

    @abstractmethod
    def __iadd__(self, other: BaseSet) -> BaseSet:
        pass

    @abstractmethod
    def __mul__(self, other: BaseSet) -> BaseSet:
        pass

    @abstractmethod
    def __imul__(self, other: BaseSet) -> BaseSet:
        pass

    @abstractmethod
    def __sub__(self, other: BaseSet) -> BaseSet:
        pass

    @abstractmethod
    def __isub__(self, other: BaseSet) -> BaseSet:
        pass

    @abstractmethod
    def power_set(self) -> BaseSet:
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def show(self) -> None:
        pass

