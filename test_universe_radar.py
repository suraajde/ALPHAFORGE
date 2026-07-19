from services.universe_service import (
    UniverseService,
)

from services.research_radar_service import (
    build_research_radar,
)


# --------------------------------------------------
# LOAD STOCK UNIVERSE
# --------------------------------------------------

universe_service = UniverseService()

universe_result = (
    universe_service.get_symbols()
)

symbols = universe_result[
    "symbols"
]


print()
print("=" * 125)
print(
    "ALPHAFORGE UNIVERSE → RESEARCH RADAR TEST"
)
print("=" * 125)

print(
    f"Universe stocks loaded : "
    f"{len(symbols)}"
)

print(
    f"Symbols                : "
    f"{symbols}"
)


if universe_result["errors"]:

    print()
    print("UNIVERSE ERRORS")

    for error in universe_result[
        "errors"
    ]:

        print(error)


# --------------------------------------------------
# RUN RESEARCH RADAR
# --------------------------------------------------

print()
print(
    "Starting Research Radar analysis..."
)
print()

result = build_research_radar(
    symbols,
    limit=30,
)


# --------------------------------------------------
# ELIGIBLE RANKED POOL
# --------------------------------------------------

print()
print("=" * 125)
print(
    "ALPHAFORGE RESEARCH RADAR - ELIGIBLE POOL"
)
print("=" * 125)

print(
    f"Analyzed   : "
    f"{result['analyzed_count']}"
)

print(
    f"Successful : "
    f"{result['successful_count']}"
)

print(
    f"Eligible   : "
    f"{result['eligible_count']}"
)

print(
    f"Review     : "
    f"{result['review_count']}"
)

print()


for stock in result["ranked"]:

    data_status = stock.get(
        "data_status",
        "UNKNOWN",
    )

    print(
        f"#{stock['rank']:02d} "
        f"{stock['symbol']:12} | "
        f"{stock['scoring_profile']:18} | "
        f"Composite: "
        f"{stock['composite_score']:5.1f} | "
        f"Fund: "
        f"{stock['fundamental_score']:5.1f} | "
        f"Tech: "
        f"{stock['technical_score']:5.1f} | "
        f"Ready: "
        f"{stock['readiness_score']:5.1f} | "
        f"Data: "
        f"{data_status:12} | "
        f"{stock['classification']}"
    )

    # ----------------------------------------------
    # SHOW CAUTION DETAILS
    # ----------------------------------------------

    if (
        data_status
        == "CAUTION"
    ):

        reasons = stock.get(
            "data_caution_reasons",
            [],
        )

        if reasons:

            print(
                "     DATA CAUTION:"
            )

            for reason in reasons:

                print(
                    f"       - {reason}"
                )


# --------------------------------------------------
# REVIEW / PROVISIONAL POOL
# --------------------------------------------------

print()
print("=" * 125)
print(
    "REVIEW / PROVISIONAL POOL"
)
print("=" * 125)


for stock in result["review"]:

    data_status = stock.get(
        "data_status",
        "UNKNOWN",
    )

    print(
        f"{stock['symbol']:12} | "
        f"{stock['scoring_profile']:18} | "
        f"{stock['profile_maturity']:12} | "
        f"Composite: "
        f"{stock['composite_score']:5.1f} | "
        f"Data: "
        f"{data_status:12} | "
        f"{stock['classification']} | "
        f"{stock['ranking_notes']}"
    )

    # ----------------------------------------------
    # SHOW DATA CAUTION / INSUFFICIENT DETAILS
    # ----------------------------------------------

    if data_status in {
        "CAUTION",
        "INSUFFICIENT",
    }:

        reasons = stock.get(
            "data_caution_reasons",
            [],
        )

        if reasons:

            print(
                "     DATA STATUS DETAILS:"
            )

            for reason in reasons:

                print(
                    f"       - {reason}"
                )


# --------------------------------------------------
# ERRORS
# --------------------------------------------------

if result["errors"]:

    print()
    print("=" * 125)
    print(
        "ANALYSIS ERRORS"
    )
    print("=" * 125)

    for item in result["errors"]:

        print(
            item.get(
                "symbol"
            ),
            ":",
            item.get(
                "error"
            ),
        )