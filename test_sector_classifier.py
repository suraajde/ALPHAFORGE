from services.stock_service import (
    get_stock_data,
)

from services.sector_classifier_service import (
    classify_sector,
)


# --------------------------------------------------
# STOCKS TO TEST
# --------------------------------------------------

symbols = [
    "INFY",
    "TCS",
    "DIXON",
    "KAYNES",
    "HDFCBANK",
    "BAJFINANCE",
    "RELIANCE",
    "SUNPHARMA",
    "BSE",
]


# --------------------------------------------------
# RUN SECTOR CLASSIFICATION TEST
# --------------------------------------------------

for symbol in symbols:

    print()
    print("=" * 70)

    print(
        f"SECTOR CLASSIFICATION: {symbol}"
    )

    print("=" * 70)

    # ----------------------------------------------
    # GET COMPANY DATA
    # ----------------------------------------------

    data = get_stock_data(
        symbol
    )

    # ----------------------------------------------
    # HANDLE DATA ERROR
    # ----------------------------------------------

    if (
        not data
        or "error" in data
    ):

        print(
            "ERROR:",
            data.get(
                "error",
                "Unknown error",
            )
            if data
            else "No data returned",
        )

        continue

    # ----------------------------------------------
    # CLASSIFY COMPANY
    # ----------------------------------------------

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

    # ----------------------------------------------
    # DISPLAY RESULTS
    # ----------------------------------------------

    print(
        "Company  :",
        data.get(
            "name"
        ),
    )

    print(
        "Sector   :",
        data.get(
            "sector"
        ),
    )

    print(
        "Industry :",
        data.get(
            "industry"
        ),
    )

    print(
        "Profile  :",
        result.get(
            "profile"
        ),
    )