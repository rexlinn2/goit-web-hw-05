from aiohttp import web

from api import PrivatBankAPI
from exchange import (
    ExchangeService,
    DEFAULT_CURRENCIES,
)
from logger import log_exchange_command


routes = web.RouteTableDef()

api = PrivatBankAPI()

exchange_service = ExchangeService(api)

connected_users = set()


@routes.get("/")
async def index(request):

    return web.FileResponse(
        "./templates/index.html"
    )


@routes.get("/ws")
async def websocket_handler(request):

    websocket = web.WebSocketResponse()

    await websocket.prepare(request)

    connected_users.add(websocket)

    username = "Anonymous"

    try:

        await websocket.send_str(
            "Ви підключені до чату.\n"
            "\n"
            "Доступні команди:\n"
            "exchange\n"
            "exchange 2\n"
            "exchange 5 GBP PLN"
        )

        async for message in websocket:

            if message.type != web.WSMsgType.TEXT:
                continue

            text = message.data.strip()

            if not text:
                continue

            if text.lower().startswith("name "):

                username = text[5:].strip()

                await websocket.send_str(
                    f"Ваше ім'я змінено на {username}"
                )

                continue

            if text.lower().startswith("exchange"):

                await log_exchange_command(
                    username,
                    text,
                )

                response = await process_exchange_command(
                    text
                )

                await websocket.send_str(
                    response
                )

                continue

            message_text = (
                f"{username}: {text}"
            )

            for user in connected_users.copy():

                if not user.closed:

                    await user.send_str(
                        message_text
                    )

    finally:

        connected_users.discard(
            websocket
        )

    return websocket


async def process_exchange_command(
    command: str,
) -> str:

    parts = command.split()

    if not parts:

        return "Невірна команда."

    if len(parts) == 1:

        days = 1

        currencies = DEFAULT_CURRENCIES.copy()

    else:

        try:

            days = int(
                parts[1]
            )

        except ValueError:

            return (
                "Невірний формат.\n"
                "Приклад: exchange 2"
            )

        if days < 1 or days > 10:

            return (
                "Можна отримати курс "
                "максимум за 10 днів."
            )

        if len(parts) > 2:

            currencies = [
                currency.upper()
                for currency in parts[2:]
            ]

        else:

            currencies = (
                DEFAULT_CURRENCIES.copy()
            )

    try:

        rates = await exchange_service.get_rates(
            days,
            currencies,
        )

    except ConnectionError as error:

        return f"Помилка API: {error}"

    return format_exchange_result(
        rates
    )


def format_exchange_result(
    rates: list[dict],
) -> str:

    lines = []

    for day in rates:

        for date_name, currencies in day.items():

            lines.append(
                f"\n📅 {date_name}"
            )

            if "error" in currencies:

                lines.append(
                    f"Помилка: {currencies['error']}"
                )

                continue

            for currency, values in currencies.items():

                purchase = values.get(
                    "purchase"
                )

                sale = values.get(
                    "sale"
                )

                lines.append(
                    f"{currency}: "
                    f"купівля {purchase}, "
                    f"продаж {sale}"
                )

    return "\n".join(lines)


async def start_chat():

    app = web.Application()

    app.add_routes(routes)

    print(
        "WebSocket chat запущено:"
    )

    print(
        "http://localhost:8080"
    )

    await web._run_app(
        app,
        host="localhost",
        port=8080,
    )