from services.stock_service import (
    get_stock_data,
)

from services.fundamental_service import (
    get_fundamental_metrics,
)

from services.sector_classifier_service import (
    classify_sector,
)

from services.data_completeness_service import (
    analyze_data_completeness,
)


symbols = [
    "POLYCAB",
    "DIXON",
    "KAYNES",
]


for symbol in symbols:

    print()
    print("=" * 75)

    print(
        f"DATA COMPLETENESS TEST: {symbol}"
    )

    print("=" * 75)

    # ----------------------------------------------
    # COMPANY METADATA
    # ----------------------------------------------

    stock_data = get_stock_data(
        symbol
    )

    if (
        not stock_data
        or "error" in stock_data
    ):

        print(
            "Company data unavailable"
        )

        continue

    # ----------------------------------------------
    # SECTOR PROFILE
    # ----------------------------------------------

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

    # ----------------------------------------------
    # FUNDAMENTAL DATA
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
            "Fundamental data unavailable"
        )

        continue

    # ----------------------------------------------
    # COMPLETENESS ANALYSIS
    # ----------------------------------------------

    result = (
        analyze_data_completeness(
            fundamental_data,
            profile,
        )
    )

    # ----------------------------------------------
    # SUMMARY
    # ----------------------------------------------

    print(
        "Profile                  :",
        result.get(
            "profile"
        ),
    )

    print(
        "Coverage Score           :",
        result.get(
            "coverage_score"
        ),
    )

    print(
        "Coverage Level           :",
        result.get(
            "coverage_level"
        ),
    )

    print(
        "Ranking Data Ready       :",
        result.get(
            "ranking_data_ready"
        ),
    )

    print(
        "Blocking Reasons         :",
        result.get(
            "blocking_reasons"
        ),
    )

    print(
        "Warnings                 :",
        result.get(
            "warnings"
        ),
    )

    # ----------------------------------------------
    # GROUP COVERAGE
    # ----------------------------------------------

    print()
    print("GROUP COVERAGE")
    print("-" * 75)

    for (
        group_name,
        group_data,
    ) in result[
        "groups"
    ].items():

        print(
            f"{group_name:20} : "
            f"{group_data['coverage']:5.1f}% | "
            f"Available "
            f"{group_data['available_count']}/"
            f"{group_data['total_count']}"
        )

    # ----------------------------------------------
    # MISSING METRICS
    # ----------------------------------------------

    print()
    print("MISSING METRICS")
    print("-" * 75)

    missing = [

        metric

        for metric, status

        in result[
            "metric_status"
        ].items()

        if status == "MISSING"
    ]

    if missing:

        for metric in missing:

            print(
                metric
            )

    else:

        print(
            "None"
        )