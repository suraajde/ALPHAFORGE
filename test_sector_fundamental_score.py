from services.stock_service import (
    get_stock_data,
)

from services.fundamental_service import (
    get_fundamental_metrics,
)

from services.sector_classifier_service import (
    classify_sector,
)

from services.sector_fundamental_score_service import (
    calculate_sector_aware_fundamental_score,
)


symbols = [
    "INFY",
    "HDFCBANK",
    "BAJFINANCE",
    "BSE",
    "RELIANCE",
]


for symbol in symbols:

    print()
    print("=" * 75)

    print(
        f"SECTOR-AWARE FUNDAMENTAL TEST: {symbol}"
    )

    print("=" * 75)

    stock_data = get_stock_data(
        symbol
    )

    fundamental_data = (
        get_fundamental_metrics(
            symbol
        )
    )

    classification = classify_sector(
        sector=stock_data.get(
            "sector"
        ),
        industry=stock_data.get(
            "industry"
        ),
        company_name=stock_data.get(
            "name"
        ),
    )

    profile = classification.get(
        "profile"
    )

    scores = (
        calculate_sector_aware_fundamental_score(
            fundamental_data,
            profile,
        )
    )

    print(
        "Profile                   :",
        profile,
    )

    for key, value in scores.items():

        print(
            f"{key:27} : {value}"
        )