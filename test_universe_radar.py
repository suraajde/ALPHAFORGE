from services.universe_service import (
    UniverseService,
)

from services.research_radar_service import (
    build_research_radar,
)


# ==================================================
# SCAN SETTINGS
# ==================================================

# False:
# Use fresh cache when available.
# This is the normal/default mode.
#
# True:
# Ignore existing cache and perform fresh live
# analysis for every stock, then update the cache.

FORCE_REFRESH = False

TOP_LIMIT = 30


# ==================================================
# LOAD STOCK UNIVERSE
# ==================================================

universe_service = (
    UniverseService()
)

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
    f"Force refresh          : "
    f"{FORCE_REFRESH}"
)

print(
    f"Top ranking limit      : "
    f"{TOP_LIMIT}"
)

print(
    f"Symbols                : "
    f"{symbols}"
)


# ==================================================
# UNIVERSE ERRORS
# ==================================================

if universe_result.get(
    "errors"
):

    print()
    print(
        "UNIVERSE ERRORS"
    )
    print(
        "-" * 125
    )

    for error in universe_result[
        "errors"
    ]:

        print(
            error
        )


# ==================================================
# RUN RESEARCH RADAR
# ==================================================

print()
print(
    "Starting Research Radar analysis..."
)
print()

result = (
    build_research_radar(

        symbols,

        limit=TOP_LIMIT,

        force_refresh=
            FORCE_REFRESH,
    )
)


# ==================================================
# SCAN / CACHE SUMMARY
# ==================================================

print()
print("=" * 125)
print(
    "ALPHAFORGE SCAN SUMMARY"
)
print("=" * 125)

print(
    f"Stocks requested       : "
    f"{len(symbols)}"
)

print(
    f"Stocks analyzed        : "
    f"{result.get('analyzed_count', 0)}"
)

print(
    f"Successful             : "
    f"{result.get('successful_count', 0)}"
)

print(
    f"Errors                 : "
    f"{len(result.get('errors', []))}"
)

print(
    f"Cache hits             : "
    f"{result.get('cache_hits', 0)}"
)

print(
    f"Live analyses          : "
    f"{result.get('live_analyses', 0)}"
)

print(
    f"Cache saves            : "
    f"{result.get('cache_saves', 0)}"
)

print(
    f"Cache save failures    : "
    f"{result.get('cache_save_failures', 0)}"
)

print(
    f"Force refresh          : "
    f"{result.get('force_refresh', False)}"
)


# ==================================================
# ELIGIBLE RANKED POOL
# ==================================================

print()
print("=" * 125)
print(
    "ALPHAFORGE RESEARCH RADAR - ELIGIBLE POOL"
)
print("=" * 125)

print(
    f"Analyzed   : "
    f"{result.get('analyzed_count', 0)}"
)

print(
    f"Successful : "
    f"{result.get('successful_count', 0)}"
)

print(
    f"Eligible   : "
    f"{result.get('eligible_count', 0)}"
)

print(
    f"Review     : "
    f"{result.get('review_count', 0)}"
)

print()


for stock in result.get(
    "ranked",
    [],
):

    data_status = (
        stock.get(
            "data_status",
            "UNKNOWN",
        )
    )

    print(
        f"#{stock.get('rank', 0):02d} "
        f"{stock.get('symbol', ''):12} | "
        f"{stock.get('scoring_profile', ''):18} | "
        f"Composite: "
        f"{stock.get('composite_score', 0):5.1f} | "
        f"Fund: "
        f"{stock.get('fundamental_score', 0):5.1f} | "
        f"Tech: "
        f"{stock.get('technical_score', 0):5.1f} | "
        f"Ready: "
        f"{stock.get('readiness_score', 0):5.1f} | "
        f"Data: "
        f"{data_status:12} | "
        f"{stock.get('classification', '')}"
    )

    # ----------------------------------------------
    # DATA CAUTION DETAILS
    # ----------------------------------------------

    if (
        data_status
        == "CAUTION"
    ):

        reasons = (
            stock.get(
                "data_caution_reasons",
                [],
            )
        )

        if reasons:

            print(
                "     DATA CAUTION:"
            )

            for reason in reasons:

                print(
                    f"       - {reason}"
                )


# ==================================================
# REVIEW / PROVISIONAL POOL
# ==================================================

print()
print("=" * 125)
print(
    "REVIEW / PROVISIONAL POOL"
)
print("=" * 125)


review_items = result.get(
    "review",
    [],
)


if not review_items:

    print(
        "No stocks currently in review pool."
    )


for stock in review_items:

    data_status = (
        stock.get(
            "data_status",
            "UNKNOWN",
        )
    )

    print(
        f"{stock.get('symbol', ''):12} | "
        f"{stock.get('scoring_profile', ''):18} | "
        f"{stock.get('profile_maturity', ''):12} | "
        f"Composite: "
        f"{stock.get('composite_score', 0):5.1f} | "
        f"Data: "
        f"{data_status:12} | "
        f"{stock.get('classification', '')} | "
        f"{stock.get('ranking_notes', [])}"
    )

    # ----------------------------------------------
    # DATA STATUS DETAILS
    # ----------------------------------------------

    if data_status in {
        "CAUTION",
        "INSUFFICIENT",
    }:

        reasons = (
            stock.get(
                "data_caution_reasons",
                [],
            )
        )

        if reasons:

            print(
                "     DATA STATUS DETAILS:"
            )

            for reason in reasons:

                print(
                    f"       - {reason}"
                )


# ==================================================
# ANALYSIS ERRORS
# ==================================================

errors = result.get(
    "errors",
    [],
)


if errors:

    print()
    print("=" * 125)
    print(
        "ANALYSIS ERRORS"
    )
    print("=" * 125)

    for item in errors:

        print(
            f"{item.get('symbol', 'UNKNOWN'):12} | "
            f"{item.get('error', 'Unknown error')}"
        )


# ==================================================
# FINAL VALIDATION
# ==================================================

print()
print("=" * 125)
print(
    "SCAN VALIDATION"
)
print("=" * 125)

accounted_for = (

    result.get(
        "cache_hits",
        0,
    )

    + result.get(
        "live_analyses",
        0,
    )
)

analyzed_count = (
    result.get(
        "analyzed_count",
        0,
    )
)

print(
    f"Cache + Live           : "
    f"{accounted_for}"
)

print(
    f"Analyzed Count         : "
    f"{analyzed_count}"
)


if (
    accounted_for
    == analyzed_count
):

    print(
        "Cache accounting       : PASS"
    )

else:

    print(
        "Cache accounting       : CHECK REQUIRED"
    )


print("=" * 125)