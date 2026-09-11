from src.app.domain.vector import Vector
from src.app.data.storage import vectors


def show_vectors() -> None:
    if len(vectors) == 0:
        print("\nNo vectors created!")
        return

    for index, vector in enumerate(vectors, start=1):
        print(f"{index}. {vector}")


def get_vector_by_id(vector_id: int) -> Vector | None:
    if vector_id < 1 or vector_id > len(vectors):
        print("\nVector with this ID does not exist!")
        return None

    return vectors[vector_id - 1]


def choose_vector() -> Vector | None:
    show_vectors()

    if len(vectors) == 0:
        return None

    vector_id = int(input("Enter vector ID: "))
    return get_vector_by_id(vector_id)


def run_vector_menu():
    while True:
        choice = int(input(
            "\n========== VECTOR MENU ==========\n"
            "1. Create vector\n"
            "2. Show vectors\n"
            "3. Show coordinates\n"
            "4. Vector length\n"
            "5. Add vectors (+)\n"
            "6. Subtract vectors (-)\n"
            "7. Cross product (*)\n"
            "8. Multiply by number\n"
            "9. Divide by number\n"
            "10. Cosine\n"
            "11. Compare vectors\n"
            "0. Back\n"
            "Choose: "
        ))

        if choice == 0:
            break

        elif choice == 1:
            data = input("Enter vector (x y z): ")
            vector = Vector.from_string(data)

            vectors.append(vector)

            print(f"Created: {vector}")
            print(f"Vector ID: {len(vectors)}")

        elif choice == 2:
            show_vectors()

        elif choice == 3:
            vector = choose_vector()

            if vector is None:
                continue

            print(vector.get_coordinates())

        elif choice == 4:
            vector = choose_vector()

            if vector is None:
                continue

            print(f"Length: {vector.length()}")

        elif choice == 5:
            first = choose_vector()
            second = choose_vector()

            if first is None or second is None:
                continue

            result = first + second
            vectors.append(result)

            print(f"Result: {result}")

        elif choice == 6:
            first = choose_vector()
            second = choose_vector()

            if first is None or second is None:
                continue

            result = first - second
            vectors.append(result)

            print(f"Result: {result}")

        elif choice == 7:
            first = choose_vector()
            second = choose_vector()

            if first is None or second is None:
                continue

            result = first * second
            vectors.append(result)

            print(f"Result: {result}")

        elif choice == 8:
            vector = choose_vector()

            if vector is None:
                continue

            number = float(input("Enter number: "))

            result = vector * number
            vectors.append(result)

            print(f"Result: {result}")

        elif choice == 9:
            vector = choose_vector()

            if vector is None:
                continue

            number = float(input("Enter number: "))

            result = vector / number
            vectors.append(result)

            print(f"Result: {result}")

        elif choice == 10:
            first = choose_vector()
            second = choose_vector()

            if first is None or second is None:
                continue

            print(f"Cosine: {first.cosine(second)}")

        elif choice == 11:

            first = choose_vector()
            second = choose_vector()

            if first is None or second is None:
                continue

            if first > second:
                print("First vector is longer")

            elif first < second:
                print("Second vector is longer")

            else:
                print("Vectors have equal length")