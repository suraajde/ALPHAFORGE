from services.research_radar_service import (
    build_research_radar,
)


symbols = [
    "INFY",
    "KPITTECH",
    "BSE",
    "TCS",
    "RELIANCE",
    "HDFCBANK",
]


result = build_research_radar(
    symbols,
    limit=30,
)


print()
print("=" * 100)
print("ALPHAFORGE RESEARCH RADAR")
print("=" * 100)

print(
    f"Analyzed: "
    f"{result['analyzed_count']}"
)

print(
    f"Successful: "
    f"{result['successful_count']}"
)

print()

for stock in result["ranked"]:

    print(
        f"#{stock['rank']:02d} "
        f"{stock['symbol']:12} | "
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


if result["errors"]:

    print()
    print("ERRORS")
    print("-" * 100)

    for item in result["errors"]:

        print(
            item.get("symbol"),
            ":",
            item.get("error"),
        )