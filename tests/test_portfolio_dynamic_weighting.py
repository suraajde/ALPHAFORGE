from services.portfolio_construction_service import (
    PortfolioConstructionService,
)


def run_tests():

    service = PortfolioConstructionService(
        max_stock_weight=10.0,
    )

    # Same selection strength for every stock.
    # Differences in target weight must therefore come from
    # investment conviction and sector adjustment, not rank alone.

    selected = []

    for index in range(12):

        selected.append(
            {
                "symbol": f"STOCK{index + 1:02d}",
                "alpha12_rank": index + 1,
                "alpha12_selection_score": 80,
                "fundamental_score": 80,
                "readiness_score": 70,
                "sector": f"SECTOR{index + 1:02d}",
                "category": (
                    "MIDCAP"
                    if index < 6
                    else "SMALLCAP"
                ),
            }
        )

    # Strong long-term investment conviction,
    # but weak current readiness.
    selected[0][
        "fundamental_score"
    ] = 95

    selected[0][
        "readiness_score"
    ] = 35

    # Hot current setup, but materially weaker fundamentals.
    selected[1][
        "fundamental_score"
    ] = 60

    selected[1][
        "readiness_score"
    ] = 95

    result = service.build(
        selected
    )

    assert result[
        "status"
    ] == "OK"

    portfolio = result[
        "portfolio"
    ]

    by_symbol = {
        row["symbol"]: row
        for row in portfolio
    }

    strong = by_symbol[
        "STOCK01"
    ]

    hot = by_symbol[
        "STOCK02"
    ]

    print(
        "Strong-investment target weight:",
        strong["target_weight"],
    )

    print(
        "Hot-but-weaker target weight:",
        hot["target_weight"],
    )

    print(
        "Strong-investment allocation score:",
        strong["portfolio_allocation_score"],
    )

    print(
        "Hot-but-weaker allocation score:",
        hot["portfolio_allocation_score"],
    )

    # Stronger investment conviction must receive
    # more target capital despite weaker readiness.
    assert (
        strong["target_weight"]
        >
        hot["target_weight"]
    ), (
        "Hot readiness incorrectly received more "
        "capital than stronger investment conviction"
    )

    # Portfolio must remain fully allocated.
    total_weight = round(
        sum(
            row["target_weight"]
            for row in portfolio
        ),
        2,
    )

    print(
        "Total target weight:",
        total_weight,
    )

    assert total_weight == 100.00

    # Construction cap applies to initial/fresh-capital
    # target allocation only.
    max_weight = max(
        row["target_weight"]
        for row in portfolio
    )

    print(
        "Maximum target weight:",
        max_weight,
    )

    assert max_weight <= 10.00

    # Rank alone must not mechanically dictate weight.
    # STOCK12 has a worse rank than STOCK03 but identical
    # conviction inputs, so their target weights should match.
    stock03 = by_symbol[
        "STOCK03"
    ]

    stock12 = by_symbol[
        "STOCK12"
    ]

    print(
        "Rank 3 target weight:",
        stock03["target_weight"],
    )

    print(
        "Rank 12 target weight:",
        stock12["target_weight"],
    )

    assert (
        stock03["target_weight"]
        ==
        stock12["target_weight"]
    ), (
        "Rank alone incorrectly changed target allocation"
    )

    print()
    print(
        "Sprint 11.5A.2 dynamic portfolio weighting: PASS"
    )


if __name__ == "__main__":
    run_tests()
