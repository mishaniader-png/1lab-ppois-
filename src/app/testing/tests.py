import pytest

from src.app.domain.vector import Vector
from src.app.domain.exceptions import ZeroVectorError

from src.app.domain.set import SetBase


# первая часть
def test_create_vector():
    vector = Vector(1, 2, 3)

    assert vector.x == 1
    assert vector.y == 2
    assert vector.z == 3


@pytest.mark.parametrize("data, expected", [
    ("1 2 3", Vector(1, 2, 3)),
    ("0 0 0", Vector(0, 0, 0)),
    ("-1 5 2", Vector(-1, 5, 2)),
])
def test_from_string(data, expected):
    vector = Vector.from_string(data)

    assert vector == expected


def test_get_coordinates():
    vector = Vector(1, 2, 3)

    assert vector.get_coordinates() == [1, 2, 3]


@pytest.mark.parametrize("vector, expected", [
    (Vector(3, 4, 0), 5),
    (Vector(0, 0, 0), 0),
    (Vector(1, 0, 0), 1),
])
def test_length(vector, expected):
    assert vector.length() == expected


def test_add():
    first = Vector(1, 2, 3)
    second = Vector(4, 5, 6)

    result = first + second

    assert result == Vector(5, 7, 9)


def test_iadd():
    vector = Vector(1, 2, 3)

    vector += Vector(4, 5, 6)

    assert vector == Vector(5, 7, 9)


def test_sub():
    first = Vector(5, 7, 9)
    second = Vector(1, 2, 3)

    result = first - second

    assert result == Vector(4, 5, 6)


def test_isub():
    vector = Vector(5, 7, 9)

    vector -= Vector(1, 2, 3)

    assert vector == Vector(4, 5, 6)


@pytest.mark.parametrize("number, expected", [
    (2, Vector(2, 4, 6)),
    (0, Vector(0, 0, 0)),
    (-1, Vector(-1, -2, -3)),
])
def test_multiply_by_number(number, expected):
    vector = Vector(1, 2, 3)

    result = vector * number

    assert result == expected


def test_imultiply_by_number():
    vector = Vector(1, 2, 3)

    vector *= 2

    assert vector == Vector(2, 4, 6)


def test_cross_product():
    first = Vector(1, 0, 0)
    second = Vector(0, 1, 0)

    result = first * second

    assert result == Vector(0, 0, 1)


def test_icross_product():
    vector = Vector(1, 0, 0)

    vector *= Vector(0, 1, 0)

    assert vector == Vector(0, 0, 1)


@pytest.mark.parametrize("number, expected", [
    (2, Vector(1, 2, 3)),
    (-2, Vector(-1, -2, -3)),
])
def test_division(number, expected):
    vector = Vector(2, 4, 6)

    result = vector / number

    assert result == expected


def test_idivision():
    vector = Vector(2, 4, 6)

    vector /= 2

    assert vector == Vector(1, 2, 3)


def test_division_by_zero():
    vector = Vector(1, 2, 3)

    with pytest.raises(ZeroDivisionError):
        vector / 0


def test_cosine_same_direction():
    first = Vector(1, 0, 0)
    second = Vector(1, 0, 0)

    assert first.cosine(second) == pytest.approx(1)


def test_cosine_perpendicular():
    first = Vector(1, 0, 0)
    second = Vector(0, 1, 0)

    assert first.cosine(second) == pytest.approx(0)


def test_cosine_with_zero_vector():
    first = Vector(0, 0, 0)
    second = Vector(1, 0, 0)

    with pytest.raises(ZeroVectorError):
        first.cosine(second)


def test_equal():
    assert Vector(1, 2, 3) == Vector(1, 2, 3)


def test_not_equal():
    assert Vector(1, 2, 3) != Vector(3, 2, 1)


def test_less():
    assert Vector(1, 0, 0) < Vector(2, 0, 0)


def test_less_or_equal():
    assert Vector(1, 0, 0) <= Vector(1, 0, 0)


def test_greater():
    assert Vector(2, 0, 0) > Vector(1, 0, 0)


def test_greater_or_equal():
    assert Vector(2, 0, 0) >= Vector(2, 0, 0)


def test_string():
    vector = Vector(1, 2, 3)

    assert str(vector) == "1 2 3"



# вторая часть
def test_create_empty_set():
    my_set = SetBase()

    assert my_set.is_empty()


def test_create_not_empty_set():
    my_set = SetBase(["a", "b"])

    assert not my_set.is_empty()


@pytest.mark.parametrize("data, expected", [
    ("{}", SetBase()),
    ("{a}", SetBase(["a"])),
    ("{a, b, c}", SetBase(["a", "b", "c"])),
])
def test_from_string(data, expected):
    result = SetBase.from_string(data)

    assert result == expected


def test_from_string_nested_set():
    result = SetBase.from_string("{a, {b, c}, {}}")

    expected = SetBase([
        "a",
        SetBase(["b", "c"]),
        SetBase()
    ])

    assert result == expected


def test_add():
    my_set = SetBase()

    my_set.add("a")

    assert my_set["a"]


def test_add_duplicate():
    my_set = SetBase(["a"])

    my_set.add("a")

    assert my_set.cardinality() == 1


def test_remove():
    my_set = SetBase(["a", "b"])

    my_set.remove("a")

    assert not my_set["a"]
    assert my_set["b"]


@pytest.mark.parametrize("elements, expected", [
    ([], 0),
    (["a"], 1),
    (["a", "b"], 2),
    (["a", SetBase(["b", "c"])], 2),
])
def test_cardinality(elements, expected):
    my_set = SetBase(elements)

    assert my_set.cardinality() == expected


def test_element_exists():
    my_set = SetBase(["a", "b"])

    assert my_set["a"]


def test_element_does_not_exist():
    my_set = SetBase(["a", "b"])

    assert not my_set["c"]


def test_union():
    first = SetBase(["a", "b"])
    second = SetBase(["b", "c"])

    result = first + second

    assert result == SetBase(["a", "b", "c"])


def test_iunion():
    first = SetBase(["a", "b"])
    second = SetBase(["b", "c"])

    first += second

    assert first == SetBase(["a", "b", "c"])


def test_intersection():
    first = SetBase(["a", "b"])
    second = SetBase(["b", "c"])

    result = first * second

    assert result == SetBase(["b"])


def test_iintersection():
    first = SetBase(["a", "b"])
    second = SetBase(["b", "c"])

    first *= second

    assert first == SetBase(["b"])


def test_difference():
    first = SetBase(["a", "b", "c"])
    second = SetBase(["b"])

    result = first - second

    assert result == SetBase(["a", "c"])


def test_idifference():
    first = SetBase(["a", "b", "c"])
    second = SetBase(["b"])

    first -= second

    assert first == SetBase(["a", "c"])


def test_power_set_count():
    my_set = SetBase(["a", "b"])

    result = my_set.power_set()

    assert len(result) == 4


def test_power_set_contains_empty_set():
    my_set = SetBase(["a", "b"])

    result = my_set.power_set()

    assert SetBase() in result


def test_power_set_contains_full_set():
    my_set = SetBase(["a", "b"])

    result = my_set.power_set()

    assert SetBase(["a", "b"]) in result


def test_equal_same_elements():
    first = SetBase(["a", "b"])
    second = SetBase(["a", "b"])

    assert first == second


def test_equal_different_order():
    first = SetBase(["a", "b"])
    second = SetBase(["b", "a"])

    assert first == second


def test_not_equal():
    first = SetBase(["a", "b"])
    second = SetBase(["a", "c"])

    assert first != second


def test_not_equal_different_size():
    first = SetBase(["a"])
    second = SetBase(["a", "b"])

    assert first != second


def test_nested_sets_equal():
    first = SetBase(["a", SetBase(["b", "c"])])
    second = SetBase([SetBase(["c", "b"]), "a"])

    assert first == second


def test_string():
    my_set = SetBase(["a", "b"])

    assert str(my_set) == "{a, b}"


def test_nested_string():
    my_set = SetBase(["a", SetBase(["b", "c"])])

    assert str(my_set) == "{a, {b, c}}"