from __future__ import annotations

from abc import ABC, abstractmethod


class BaseVector(ABC):

    @abstractmethod
    def get_coordinates(self) -> list[float]:
        pass

    @abstractmethod
    def length(self) -> float:
        pass

    @abstractmethod
    def __add__(self, other: BaseVector) -> BaseVector:
        pass

    @abstractmethod
    def __iadd__(self, other: BaseVector) -> BaseVector:
        pass

    @abstractmethod
    def __sub__(self, other: BaseVector) -> BaseVector:
        pass

    @abstractmethod
    def __isub__(self, other: BaseVector) -> BaseVector:
        pass

    @abstractmethod
    def __mul__(self, other: BaseVector | float) -> BaseVector:
        pass

    @abstractmethod
    def __imul__(self, other: BaseVector | float) -> BaseVector:
        pass

    @abstractmethod
    def __truediv__(self, number: float) -> BaseVector:
        pass

    @abstractmethod
    def __itruediv__(self, number: float) -> BaseVector:
        pass

    @abstractmethod
    def cosine(self, other: BaseVector) -> float:
        pass

    @abstractmethod
    def __lt__(self, other: BaseVector) -> bool:
        pass

    @abstractmethod
    def __le__(self, other: BaseVector) -> bool:
        pass

    @abstractmethod
    def __gt__(self, other: BaseVector) -> bool:
        pass

    @abstractmethod
    def __ge__(self, other: BaseVector) -> bool:
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def from_string(cls, data: str) -> BaseVector:
        pass