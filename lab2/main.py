
import asyncio
from asyncio import to_thread


async def main() -> None:
    print("Banking project: async CLI will be implemented here.")


if __name__ == "__main__":
    asyncio.run(main())

MENU_OPTIONS = {
    "accounts": "Показать счета",
    "deposit": "Пополнить счёт",
    "withdraw": "Снять деньги",
    "transfer": "Перевести деньги",
    "exit": "Выход"
}

def show_menu(title: str, **options: str) -> None:
    print(f"{title}:")
    for key, value in options.items():
        print(f"{key}: {value}")

async def read_choice(prompt: str, *allowed: str) -> str:
    while True:
        command = await asyncio.to_thread(input, allowed)
        if command in allowed:


