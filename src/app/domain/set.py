from typing import List
from itertools import combinations
from src.app.domain.RulesSet import BaseSet


class SetBase(BaseSet):
    def __init__(self, elements: List[object] | None = None) -> None:
        self.elements = list(elements) if elements else []

    @classmethod
    def from_string(cls, data: str) -> BaseSet:
        data = data.strip()
        content = data[1:-1]

        elements = []
        cursor = 0

        while cursor < len(content):
            while (
                cursor < len(content)
                and (
                    content[cursor].isspace()
                    or content[cursor] == ","
                )
            ):
                cursor += 1

            if cursor >= len(content):
                break

            if content[cursor] == "{":
                start = cursor
                opened = 1
                cursor += 1

                while opened > 0:
                    if content[cursor] == "{":
                        opened += 1
                    elif content[cursor] == "}":
                        opened -= 1

                    cursor += 1

                nested_data = content[start:cursor]
                nested_set = cls.from_string(nested_data)
                elements.append(nested_set)

            else:
                start = cursor

                while (
                    cursor < len(content)
                    and content[cursor] not in ",{}"
                ):
                    cursor += 1

                element = content[start:cursor].strip()

                if element:
                    elements.append(element)

        return cls(elements)

    def is_empty(self) -> bool:
        return len(self.elements) == 0

    def add(self, element: object) -> None:
        if self.is_empty():
            self.elements.append(element)
        else:
            if element in self.elements:
                print("ALREADY EXISTS")
                return

            self.elements.append(element)

    def remove(self, element: object) -> None:
        self.elements.remove(element)

    def cardinality(self) -> int:
        return len(self.elements)

    def __getitem__(self, element: object) -> bool:
        return element in self.elements

    def __add__(self, other: "SetBase") -> "SetBase":#обиеденинеи
        result = SetBase(self.elements)

        for element in other.elements:
            result.add(element)

        return result

    def __iadd__(self, other: "SetBase") -> "SetBase":# обьедиение но рез в А
        for element in other.elements:
            self.add(element)

        return self

    def __mul__(self, other: "SetBase") -> "SetBase": #пересечние
        result = SetBase()

        for element in self.elements:
            if element in other.elements:
                result.add(element)

        return result

    def __imul__(self, other: "SetBase") -> "SetBase":
        new_elements = []

        for element in self.elements:
            if element in other.elements:
                new_elements.append(element)

        self.elements = new_elements
        return self

    def __sub__(self, other: "SetBase") -> "SetBase":
        result = SetBase()

        for element in self.elements:
            if element not in other.elements:
                result.add(element)

        return result

    def __isub__(self, other: "SetBase") -> "SetBase":
        new_elements = []

        for element in self.elements:
            if element not in other.elements:
                new_elements.append(element)

        self.elements = new_elements
        return self

    def power_set(self) ->list[BaseSet]:
        subsets = []
        new_length = len(self.elements)+1
        for size in range(0, new_length):
            for combination in combinations(self.elements, size):
                subsets.append(SetBase(list(combination)))
        return subsets


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SetBase):
            return False

        if len(self.elements) != len(other.elements):
            return False

        for element in self.elements:
            if element not in other.elements:
                return False

        return True

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __str__(self) -> str:
        return "{" + ", ".join(
            str(element) for element in self.elements
        ) + "}"