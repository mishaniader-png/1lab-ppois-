from __future__ import annotations
import math
from src.app.domain.RulesVector import BaseVector
from src.app.domain.exceptions import ZeroVectorError


class Vector(BaseVector):
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def from_string(cls, data: str) -> Vector:
        return cls(*map(float, data.split()))

    def get_coordinates(self) -> list[float]:
        return [self.x, self.y, self.z]

    def length(self) -> float:
        return math.sqrt(
            self.x * self.x
            + self.y * self.y
            + self.z * self.z
        )

    def __add__(self, other: Vector) -> Vector:
        return Vector(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __iadd__(self, other: Vector) -> Vector:
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other: Vector) -> Vector:
        return Vector(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    def __isub__(self, other: Vector) -> Vector:
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __mul__(self, other: Vector | float | int) -> Vector:
        if isinstance(other, Vector):
            return Vector(
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x
            )

        if isinstance(other, (int, float)):
            return Vector(
                self.x * other,
                self.y * other,
                self.z * other
            )

        return NotImplemented

    def __imul__(self, other: Vector | float | int) -> Vector:
        if isinstance(other, Vector):
            new_x = self.y * other.z - self.z * other.y
            new_y = self.z * other.x - self.x * other.z
            new_z = self.x * other.y - self.y * other.x

            self.x = new_x
            self.y = new_y
            self.z = new_z
            return self

        if isinstance(other, (int, float)):
            self.x *= other
            self.y *= other
            self.z *= other
            return self

        return NotImplemented

    def __truediv__(self, number: float | int) -> Vector:
        if number == 0:
            raise ZeroDivisionError("Vector cannot be divided by zero")

        return Vector(
            self.x / number,
            self.y / number,
            self.z / number
        )

    def __itruediv__(self, number: float | int) -> Vector:
        if number == 0:
            raise ZeroDivisionError("Vector cannot be divided by zero")

        self.x /= number
        self.y /= number
        self.z /= number
        return self

    def cosine(self, other: Vector) -> float:
        self_length = self.length()
        other_length = other.length()

        if self_length == 0 or other_length == 0:
            raise ZeroVectorError(
                "Cosine cannot be calculated for a zero vector"
            )

        dot_product = (
            self.x * other.x
            + self.y * other.y
            + self.z * other.z
        )

        return dot_product / (self_length * other_length)

    def __lt__(self, other: Vector) -> bool:
        return self.length() < other.length()

    def __le__(self, other: Vector) -> bool:
        return self.length() <= other.length()

    def __gt__(self, other: Vector) -> bool:
        return self.length() > other.length()

    def __ge__(self, other: Vector) -> bool:
        return self.length() >= other.length()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return False

        return (
            self.x == other.x
            and self.y == other.y
            and self.z == other.z
        )

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __str__(self) -> str:
        return f"{self.x} {self.y} {self.z}"