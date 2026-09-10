from src.app.presentation.cli.vector_menu import run_vector_menu
from src.app.presentation.cli.set_menu import run_set_menu

while True:
    choice = input(
        "=======MENU=======\n"
        "1. Vector\n"
        "2. Set\n"
        "0. Exit\n"
        "Choose: "
    )

    if choice == "1":
        run_vector_menu()
    elif choice == "2":
        run_set_menu()
    elif choice == "0":
        break
    else:
        print("Invalid choice")