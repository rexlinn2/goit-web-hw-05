import aiohttp


class PrivatBankAPI:

    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates"

    async def get_exchange_rates(self, date: str) -> dict:

        params = {
            "json": "",
            "date": date,
        }

        timeout = aiohttp.ClientTimeout(total=10)

        try:
            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    self.BASE_URL,
                    params=params,
                ) as response:

                    response.raise_for_status()

                    return await response.json()

        except aiohttp.ContentTypeError as error:
            raise ConnectionError(
                "API ПриватБанку повернуло некоректний JSON."
            ) from error

        except aiohttp.ClientError as error:
            raise ConnectionError(
                f"Помилка під час запиту до API ПриватБанку: {error}"
            ) from error