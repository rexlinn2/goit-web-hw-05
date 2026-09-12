from datetime import date, timedelta
import asyncio

from api import PrivatBankAPI


DEFAULT_CURRENCIES = ["EUR", "USD"]


class ExchangeService:

    def __init__(self, api: PrivatBankAPI):
        self.api = api

    async def get_rates(
        self,
        days: int,
        currencies: list[str] | None = None,
    ) -> list[dict]:

        if days < 1 or days > 10:
            raise ValueError(
                "Кількість днів повинна бути від 1 до 10."
            )

        if currencies is None:
            currencies = DEFAULT_CURRENCIES

        currencies = [
            currency.upper()
            for currency in currencies
        ]

        result = []

        current_date = date.today()

        checked_days = 0

        while len(result) < days and checked_days < 20:

            dates = [
                current_date - timedelta(days=checked_days)
            ]

            tasks = [
                self.api.get_exchange_rates(
                    current_date.strftime("%d.%m.%Y")
                )
                for current_date in dates
            ]

            responses = await asyncio.gather(
                *tasks,
                return_exceptions=True,
            )

            for current_date, response in zip(
                dates,
                responses,
            ):

                formatted_date = current_date.strftime(
                    "%d.%m.%Y"
                )

                if isinstance(response, Exception):
                    result.append({
                        formatted_date: {
                            "error": str(response)
                        }
                    })

                    checked_days += 1
                    break

                rates = self._parse_rates(
                    response,
                    currencies,
                )

                if rates:
                    result.append({
                        formatted_date: rates
                    })

                checked_days += 1

                if len(result) >= days:
                    break

        return result

    @staticmethod
    def _parse_rates(
        data: dict,
        currencies: list[str],
    ) -> dict:

        result = {}

        exchange_rates = data.get(
            "exchangeRate",
            [],
        )

        for item in exchange_rates:

            currency = item.get("currency")

            if currency not in currencies:
                continue

            purchase = item.get(
                "purchaseRate"
            )

            sale = item.get(
                "saleRate"
            )

            if purchase is None:
                purchase = item.get(
                    "purchaseRateNB"
                )

            if sale is None:
                sale = item.get(
                    "saleRateNB"
                )

            result[currency] = {
                "purchase": purchase,
                "sale": sale,
            }

        return result