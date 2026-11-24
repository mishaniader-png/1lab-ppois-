"""Behavioral tests for both sorting implementations."""

from dataclasses import dataclass
from random import Random

import pytest

from sorts import comb_sort, tournament_sort


@dataclass
class Student:
    name: str
    grade: int


@pytest.mark.parametrize("algorithm", [comb_sort, tournament_sort])
@pytest.mark.parametrize("values", [
    [], [1], [2, 1], [9, 3, 7, 1, 5, 3],
    [5, 4, 3, 2, 1], [1, 2, 3, 4, 5], [0, -2, 7, -2, 10],
    [3, 3, 3, 3], list(range(50, -1, -1)),
])
def test_normal_values(algorithm, values):
    original = list(values)
    returned = algorithm(values)
    assert returned is values
    assert values == sorted(original)


@pytest.mark.parametrize("algorithm", [comb_sort, tournament_sort])
def test_strings(algorithm):
    words = ["pear", "apple", "banana", "apple"]
    assert algorithm(words) == ["apple", "apple", "banana", "pear"]


@pytest.mark.parametrize("algorithm", [comb_sort, tournament_sort])
def test_students_with_key(algorithm):
    students = [Student("Misha", 8), Student("Artem", 10), Student("Dima", 6)]
    algorithm(students, key=lambda item: item.grade)
    assert [student.name for student in students] == ["Dima", "Misha", "Artem"]


@pytest.mark.parametrize("algorithm", [comb_sort, tournament_sort])
def test_random_against_builtin(algorithm):
    rng = Random(2026)
    for size in range(0, 60):
        numbers = [rng.randrange(-100, 100) for _ in range(size)]
        assert algorithm(numbers[:]) == sorted(numbers)


@pytest.mark.parametrize("algorithm", [comb_sort, tournament_sort])
def test_descending_key(algorithm):
    data = [1, 7, 2, 5]
    assert algorithm(data, key=lambda x: -x) == [7, 5, 2, 1]


def test_tournament_stable_equal_keys():
    items = [Student("A", 2), Student("B", 1), Student("C", 2), Student("D", 1)]
    tournament_sort(items, key=lambda item: item.grade)
    assert [item.name for item in items] == ["B", "D", "A", "C"]
