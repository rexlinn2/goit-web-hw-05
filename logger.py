from datetime import datetime

from aiofile import async_open
from aiopath import AsyncPath


LOG_FILE = "logs/exchange.log"


async def log_exchange_command(
    username: str,
    command: str,
) -> None:

    log_path = AsyncPath(LOG_FILE)

    await log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    log_message = (
        f"[{current_time}] "
        f"User: {username} | "
        f"Command: {command}\n"
    )

    async with async_open(
        LOG_FILE,
        mode="a",
        encoding="utf-8",
    ) as file:

        await file.write(
            log_message
        )