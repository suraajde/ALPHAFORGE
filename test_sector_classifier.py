from services.stock_service import (
    get_stock_data,
)

from services.sector_classifier_service import (
    classify_sector,
)


symbols = [
    "INFY",
    "TCS",
    "HDFCBANK",
    "BAJFINANCE",
    "RELIANCE",
    "SUNPHARMA",
    "BSE",
]


for symbol in symbols:

    print()
    print("=" * 70)

    print(
        f"SECTOR CLASSIFICATION: {symbol}"
    )

    print("=" * 70)

    data = get_stock_data(
        symbol
    )

    if "error" in data:

        print(
            "ERROR:",
            data["error"],
        )

        continue

    result = classify_sector(
        sector=data.get(
            "sector"
        ),
        industry=data.get(
            "industry"
        ),
        company_name=data.get(
            "name"
        ),
    )

    print(
        "Company  :",
        data.get("name"),
    )

    print(
        "Sector   :",
        data.get("sector"),
    )

    print(
        "Industry :",
        data.get("industry"),
    )

    print(
        "Profile  :",
        result.get("profile"),
    )