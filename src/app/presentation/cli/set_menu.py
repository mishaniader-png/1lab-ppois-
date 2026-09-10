from src.app.domain.set import SetBase
from src.app.data.storage import sets


def my_enumerate(elements, start=0):  # свой enumerate для практики
    index = start

    for element in elements:
        yield index, element
        index += 1


def show_sets() -> None:
    if len(sets) == 0:
        print("\nNo sets created!")
        return

    for index, element in my_enumerate(sets, start=1):
        print(f"{index}. {element}")


def get_set_by_id(set_id: int) -> SetBase | None:
    if set_id < 1 or set_id > len(sets):
        print("\nSet with this ID does not exist!")
        return None

    return sets[set_id - 1]


def choose_set() -> SetBase | None:
    show_sets()

    if len(sets) == 0:
        return None

    set_id = int(input("Enter set ID: "))
    return get_set_by_id(set_id)


def parse_element(data: str) -> object:
    data = data.strip()

    if data.startswith("{") and data.endswith("}"):
        return SetBase.from_string(data)

    return data


def run_set_menu():
    while True:
        choice = int(input(
            "\n========== SET MENU ==========\n"
            "1. Create set\n"
            "2. Show sets\n"
            "3. Check if set is empty\n"
            "4. Add element\n"
            "5. Remove element\n"
            "6. Cardinality\n"
            "7. Check element membership\n"
            "8. Union (+)\n"
            "9. Intersection (*)\n"
            "10. Difference (-)\n"
            "11. Power set\n"
            "12. Compare sets\n"
            "0. Back\n"
            "Choose: "
        ))

        if choice == 0:
            break

        elif choice == 1:
            data = input("Enter set: ")
            new_set = SetBase.from_string(data)
            sets.append(new_set)

            print(f"Created: {new_set}")
            print(f"Set ID: {len(sets)}")

        elif choice == 2:
            show_sets()

        elif choice == 3:
            current_set = choose_set()

            if current_set is None:
                continue

            print("Set is empty!" if current_set.is_empty() else "Set is not empty!")

        elif choice == 4:
            current_set = choose_set()

            if current_set is None:
                continue

            element = parse_element(input("Enter element: "))
            current_set.add(element)

            print(f"Result: {current_set}")

        elif choice == 5:
            current_set = choose_set()

            if current_set is None:
                continue

            element = parse_element(input("Enter element: "))

            if current_set[element]:
                current_set.remove(element)
                print(f"Result: {current_set}")
            else:
                print("Element does not exist!")

        elif choice == 6:
            current_set = choose_set()

            if current_set is None:
                continue

            print(f"Cardinality: {current_set.cardinality()}")

        elif choice == 7:
            current_set = choose_set()

            if current_set is None:
                continue

            element = parse_element(input("Enter element: "))
            print(f"Element exists: {current_set[element]}")

        elif choice == 8:
            first_set = choose_set()
            second_set = choose_set()

            if first_set is None or second_set is None:
                continue

            result = first_set + second_set
            sets.append(result)

            print(f"Result: {result}")

        elif choice == 9:
            first_set = choose_set()
            second_set = choose_set()

            if first_set is None or second_set is None:
                continue

            result = first_set * second_set
            sets.append(result)

            print(f"Result: {result}")

        elif choice == 10:
            first_set = choose_set()
            second_set = choose_set()

            if first_set is None or second_set is None:
                continue

            result = first_set - second_set
            sets.append(result)

            print(f"Result: {result}")

        elif choice == 11:
            current_set = choose_set()

            if current_set is None:
                continue

            subsets = current_set.power_set()

            for subset in subsets:
                print(subset)

        elif choice == 12:
            first_set = choose_set()
            second_set = choose_set()


            if first_set is None or second_set is None:
                continue

            print(f"Equal: {first_set == second_set}")

        else:
            print("Invalid choice!")