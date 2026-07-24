from services.portfolio_construction_service import (
    PortfolioConstructionService,
)


def run_tests():

    service = PortfolioConstructionService()

    # --------------------------------------------------
    # TEST 1
    # Stronger investment fundamentals must outweigh
    # temporary hot market readiness.
    # --------------------------------------------------

    strong_investment = {
        "alpha12_selection_score": 85,
        "fundamental_score": 90,
        "readiness_score": 40,
    }

    hot_but_weaker = {
        "alpha12_selection_score": 85,
        "fundamental_score": 65,
        "readiness_score": 95,
    }

    strong_score = service._conviction_score(
        strong_investment
    )

    hot_score = service._conviction_score(
        hot_but_weaker
    )

    print(
        "Strong fundamentals / weak readiness:",
        round(strong_score, 2),
    )

    print(
        "Weaker fundamentals / hot readiness:",
        round(hot_score, 2),
    )

    assert (
        strong_score > hot_score
    ), (
        "Hot readiness incorrectly overpowered "
        "stronger investment fundamentals"
    )

    # --------------------------------------------------
    # TEST 2
    # Historical Alpha 12 payloads containing only the
    # selection score must remain backward-compatible.
    # --------------------------------------------------

    historical = {
        "alpha12_selection_score": 80,
    }

    historical_score = (
        service._conviction_score(
            historical
        )
    )

    print(
        "Selection-only backward compatibility:",
        round(historical_score, 2),
    )

    assert round(
        historical_score,
        2,
    ) == 80.00, (
        "Backward compatibility failed"
    )

    # --------------------------------------------------
    # TEST 3
    # Readiness may influence allocation conviction,
    # but only as the intended secondary 10% component.
    # --------------------------------------------------

    lower_readiness = {
        "alpha12_selection_score": 85,
        "fundamental_score": 85,
        "readiness_score": 40,
    }

    higher_readiness = {
        "alpha12_selection_score": 85,
        "fundamental_score": 85,
        "readiness_score": 90,
    }

    difference = (
        service._conviction_score(
            higher_readiness
        )
        -
        service._conviction_score(
            lower_readiness
        )
    )

    print(
        "Readiness-only conviction difference:",
        round(difference, 2),
    )

    assert round(
        difference,
        2,
    ) == 5.00, (
        "Readiness influence is not behaving "
        "as the intended secondary component"
    )

    print()
    print(
        "Sprint 11.5A.1 conviction regression tests: PASS"
    )


if __name__ == "__main__":
    run_tests()
