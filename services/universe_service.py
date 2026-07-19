from pathlib import Path
import csv


class UniverseService:

    VALID_CATEGORIES = {
        "MIDCAP",
        "SMALLCAP",
    }

    def __init__(self, universe_file=None):

        project_root = (
            Path(__file__)
            .resolve()
            .parent
            .parent
        )

        if universe_file is None:
            self.universe_file = (
                project_root
                / "data"
                / "universe"
                / "stock_universe.csv"
            )
        else:
            self.universe_file = Path(
                universe_file
            )

    def _to_bool(self, value):

        return (
            str(value)
            .strip()
            .lower()
            in {
                "true",
                "1",
                "yes",
                "y",
            }
        )

    def load_universe(self):

        if not self.universe_file.exists():

            return {
                "stocks": [],
                "errors": [
                    "Universe file not found: "
                    f"{self.universe_file}"
                ],
            }

        stocks = []
        errors = []
        seen_symbols = set()

        try:

            with self.universe_file.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:

                reader = csv.DictReader(file)

                required_columns = {
                    "symbol",
                    "company",
                    "category",
                    "enabled",
                }

                actual_columns = set(
                    reader.fieldnames or []
                )

                missing_columns = (
                    required_columns
                    - actual_columns
                )

                if missing_columns:

                    return {
                        "stocks": [],
                        "errors": [
                            "Missing columns: "
                            + ", ".join(
                                sorted(
                                    missing_columns
                                )
                            )
                        ],
                    }

                for row_number, row in enumerate(
                    reader,
                    start=2,
                ):

                    symbol = (
                        str(
                            row.get(
                                "symbol",
                                ""
                            )
                        )
                        .strip()
                        .upper()
                    )

                    company = (
                        str(
                            row.get(
                                "company",
                                ""
                            )
                        )
                        .strip()
                    )

                    category = (
                        str(
                            row.get(
                                "category",
                                ""
                            )
                        )
                        .strip()
                        .upper()
                    )

                    enabled = self._to_bool(
                        row.get(
                            "enabled",
                            False,
                        )
                    )

                    if not symbol:

                        errors.append(
                            f"Row {row_number}: "
                            "missing symbol"
                        )

                        continue

                    if symbol in seen_symbols:

                        errors.append(
                            f"Row {row_number}: "
                            f"duplicate symbol "
                            f"{symbol}"
                        )

                        continue

                    if (
                        category
                        not in self.VALID_CATEGORIES
                    ):

                        errors.append(
                            f"Row {row_number}: "
                            f"invalid category "
                            f"{category}"
                        )

                        continue

                    seen_symbols.add(symbol)

                    stocks.append(
                        {
                            "symbol": symbol,
                            "company": company,
                            "category": category,
                            "enabled": enabled,
                        }
                    )

        except Exception as error:

            return {
                "stocks": [],
                "errors": [
                    str(error)
                ],
            }

        return {
            "stocks": stocks,
            "errors": errors,
        }

    def get_enabled_stocks(
        self,
        category=None,
    ):

        result = self.load_universe()

        stocks = result["stocks"]

        enabled = [
            stock
            for stock in stocks
            if stock.get("enabled")
        ]

        if category is not None:

            category = (
                str(category)
                .strip()
                .upper()
            )

            enabled = [
                stock
                for stock in enabled
                if stock.get(
                    "category"
                ) == category
            ]

        return {
            "stocks": enabled,
            "errors": result["errors"],
        }

    def get_symbols(
        self,
        category=None,
    ):

        result = self.get_enabled_stocks(
            category
        )

        symbols = [
            stock["symbol"]
            for stock in result["stocks"]
        ]

        return {
            "symbols": symbols,
            "errors": result["errors"],
        }

    def get_summary(self):

        result = self.load_universe()

        stocks = result["stocks"]

        enabled = [
            stock
            for stock in stocks
            if stock.get("enabled")
        ]

        midcap = [
            stock
            for stock in enabled
            if stock.get(
                "category"
            ) == "MIDCAP"
        ]

        smallcap = [
            stock
            for stock in enabled
            if stock.get(
                "category"
            ) == "SMALLCAP"
        ]

        return {
            "total_records":
                len(stocks),

            "enabled_records":
                len(enabled),

            "midcap_count":
                len(midcap),

            "smallcap_count":
                len(smallcap),

            "errors":
                result["errors"],
        }


def load_stock_universe(
    category=None,
):

    service = UniverseService()

    return service.get_enabled_stocks(
        category
    )


def get_universe_symbols(
    category=None,
):

    service = UniverseService()

    return service.get_symbols(
        category
    )