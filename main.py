import asyncio
import sys
from pprint import pprint

from api import PrivatBankAPI
from exchange import ExchangeService


async def console_exchange(
    days: int,
    currencies: list[str],
):

    api = PrivatBankAPI()

    service = ExchangeService(api)

    try:

        result = await service.get_rates(
            days,
            currencies,
        )

        pprint(result)

    except ValueError as error:

        print(f"Помилка: {error}")

    except ConnectionError as error:

        print(f"Помилка мережі: {error}")


def main():

    if len(sys.argv) == 1:

        print("Використання:")
        print(
            "py main.py <кількість_днів> [валюти]"
        )

        print()

        print("Приклади:")
        print("py main.py 2")
        print("py main.py 3 GBP PLN")

        print()

        print("Для запуску WebSocket-чату:")
        print("py main.py chat")

        return

    if sys.argv[1].lower() == "chat":

        try:
            from chat import start_chat

            asyncio.run(
                start_chat()
            )

        except ImportError as error:

            print(
                "Не вдалося запустити WebSocket-чат."
            )

            print(f"Помилка: {error}")

        return

    try:

        days = int(
            sys.argv[1]
        )

    except ValueError:

        print(
            "Кількість днів повинна бути числом."
        )

        return

    if days < 1 or days > 10:

        print(
            "Можна отримати курс "
            "максимум за 10 останніх днів."
        )

        return

    if len(sys.argv) > 2:

        currencies = [
            currency.upper()
            for currency in sys.argv[2:]
        ]

    else:

        currencies = [
            "EUR",
            "USD",
        ]

    asyncio.run(
        console_exchange(
            days,
            currencies,
        )
    )


if __name__ == "__main__":
    main()