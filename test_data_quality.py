from services.fundamental_service import (
    get_fundamental_metrics,
)

from services.data_quality_service import (
    calculate_data_quality,
)


# --------------------------------------------------
# STOCKS TO TEST
# --------------------------------------------------

symbols = [
    "POLYCAB",
    "DIXON",
    "KAYNES",
]


# --------------------------------------------------
# RUN DATA QUALITY TEST
# --------------------------------------------------

for symbol in symbols:

    print()
    print("=" * 70)
    print(
        f"DATA QUALITY TEST: {symbol}"
    )
    print("=" * 70)

    # ----------------------------------------------
    # GET FUNDAMENTAL DATA
    # ----------------------------------------------

    fundamental_data = (
        get_fundamental_metrics(
            symbol
        )
    )

    if (
        not fundamental_data
        or "error" in fundamental_data
    ):

        print(
            "ERROR:",
            fundamental_data.get(
                "error",
                "Fundamental data unavailable",
            )
            if fundamental_data
            else "No fundamental data returned",
        )

        continue

    # ----------------------------------------------
    # CALCULATE DATA QUALITY
    # ----------------------------------------------

    quality = (
        calculate_data_quality(
            fundamental_data
        )
    )

    # ----------------------------------------------
    # DISPLAY QUALITY RESULT
    # ----------------------------------------------

    for key, value in quality.items():

        print(
            f"{key:28} : {value}"
        )

    # ----------------------------------------------
    # SHOW ALL FUNDAMENTAL FIELDS
    #
    # This helps us identify exactly which Yahoo
    # fields are missing instead of weakening the
    # AlphaForge quality gate blindly.
    # ----------------------------------------------

    print()
    print("FUNDAMENTAL DATA")
    print("-" * 70)

    for key, value in fundamental_data.items():

        print(
            f"{key:28} : {value}"
        )