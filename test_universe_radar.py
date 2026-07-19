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
print("=" * 110)
print("ALPHAFORGE UNIVERSE → RESEARCH RADAR TEST")
print("=" * 110)

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
print("=" * 110)
print("ALPHAFORGE RESEARCH RADAR - ELIGIBLE POOL")
print("=" * 110)

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
        f"{stock['classification']}"
    )


# --------------------------------------------------
# REVIEW / PROVISIONAL POOL
# --------------------------------------------------

print()
print("=" * 110)
print("REVIEW / PROVISIONAL POOL")
print("=" * 110)


for stock in result["review"]:

    print(
        f"{stock['symbol']:12} | "
        f"{stock['scoring_profile']:18} | "
        f"{stock['profile_maturity']:12} | "
        f"Composite: "
        f"{stock['composite_score']:5.1f} | "
        f"{stock['classification']} | "
        f"{stock['ranking_notes']}"
    )


# --------------------------------------------------
# ERRORS
# --------------------------------------------------

if result["errors"]:

    print()
    print("=" * 110)
    print("ANALYSIS ERRORS")
    print("=" * 110)

    for item in result["errors"]:

        print(
            item.get("symbol"),
            ":",
            item.get("error"),
        )