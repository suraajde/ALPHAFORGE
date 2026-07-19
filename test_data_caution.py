from services.stock_service import (
    get_stock_data,
)

from services.fundamental_service import (
    get_fundamental_metrics,
)

from services.sector_classifier_service import (
    classify_sector,
)

from services.data_quality_service import (
    calculate_data_quality,
)

from services.data_completeness_service import (
    analyze_data_completeness,
)

from services.data_caution_service import (
    evaluate_data_caution,
)


# --------------------------------------------------
# STOCKS TO TEST
# --------------------------------------------------

symbols = [
    "CUMMINSIND",
    "POLYCAB",
    "DIXON",
    "KAYNES",
]


# --------------------------------------------------
# RUN DATA CAUTION TEST
# --------------------------------------------------

for symbol in symbols:

    print()
    print("=" * 80)

    print(
        f"DATA CAUTION TEST: {symbol}"
    )

    print("=" * 80)

    # --------------------------------------------------
    # COMPANY DATA
    # --------------------------------------------------

    stock_data = get_stock_data(
        symbol
    )

    if (
        not stock_data
        or "error" in stock_data
    ):

        print(
            "ERROR: Company data unavailable"
        )

        continue

    # --------------------------------------------------
    # SECTOR CLASSIFICATION
    # --------------------------------------------------

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
        "profile",
        "GENERAL",
    )

    # --------------------------------------------------
    # FUNDAMENTAL DATA
    # --------------------------------------------------

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
            "ERROR: Fundamental data unavailable"
        )

        continue

    # --------------------------------------------------
    # RAW DATA QUALITY
    # --------------------------------------------------

    data_quality = (
        calculate_data_quality(
            fundamental_data
        )
    )

    # --------------------------------------------------
    # DATA COMPLETENESS
    # --------------------------------------------------

    completeness = (
        analyze_data_completeness(
            fundamental_data,
            profile,
        )
    )

    # --------------------------------------------------
    # DATA CAUTION STATUS
    # --------------------------------------------------

    caution = (
        evaluate_data_caution(
            data_quality=data_quality,
            completeness=completeness,
        )
    )

    # --------------------------------------------------
    # DISPLAY RESULT
    # --------------------------------------------------

    print(
        f"{'Company':25} : "
        f"{stock_data.get('name')}"
    )

    print(
        f"{'Profile':25} : "
        f"{profile}"
    )

    print(
        f"{'Raw Confidence':25} : "
        f"{caution.get('raw_confidence')}"
    )

    print(
        f"{'Coverage Score':25} : "
        f"{caution.get('coverage_score')}"
    )

    print(
        f"{'Coverage Level':25} : "
        f"{caution.get('coverage_level')}"
    )

    print(
        f"{'Ranking Data Ready':25} : "
        f"{completeness.get('ranking_data_ready')}"
    )

    print(
        f"{'DATA STATUS':25} : "
        f"{caution.get('data_status')}"
    )

    print(
        f"{'Data Caution':25} : "
        f"{caution.get('data_caution')}"
    )

    print(
        f"{'Reasons':25} : "
        f"{caution.get('reasons')}"
    )