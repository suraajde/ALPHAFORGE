from services.fundamental_score_service import (
    calculate_fundamental_score,
)


def _weighted_available_score(items):

    total = 0.0
    total_weight = 0.0

    for score, weight in items:

        if score is None:
            continue

        total += score * weight
        total_weight += weight

    if total_weight == 0:
        return None

    return round(
        total / total_weight,
        1,
    )


def _score_higher_better(
    value,
    levels,
):

    if value is None:
        return None

    for threshold, score in levels:

        if value >= threshold:
            return score

    return 20


def _score_lower_better(
    value,
    levels,
):

    if value is None:
        return None

    if value < 0:
        return 20

    for threshold, score in levels:

        if value <= threshold:
            return score

    return 20


def _growth_score(data):

    revenue_score = _score_higher_better(
        data.get(
            "revenue_growth"
        ),
        [
            (0.20, 100),
            (0.15, 90),
            (0.10, 80),
            (0.05, 60),
            (0.00, 40),
        ],
    )

    earnings_score = _score_higher_better(
        data.get(
            "earnings_growth"
        ),
        [
            (0.25, 100),
            (0.20, 90),
            (0.15, 80),
            (0.10, 70),
            (0.05, 55),
            (0.00, 40),
        ],
    )

    return _weighted_available_score(
        [
            (revenue_score, 45),
            (earnings_score, 55),
        ]
    )


def _financial_valuation_score(data):
    """
    Financial businesses are evaluated more
    heavily using PE and PB.

    Conventional industrial-company liquidity
    ratios are deliberately excluded.
    """

    pe_score = _score_lower_better(
        data.get(
            "pe"
        ),
        [
            (12, 100),
            (18, 90),
            (25, 75),
            (35, 60),
            (50, 40),
        ],
    )

    pb_score = _score_lower_better(
        data.get(
            "pb"
        ),
        [
            (1.5, 100),
            (2.5, 90),
            (4.0, 75),
            (6.0, 55),
            (10.0, 35),
        ],
    )

    return _weighted_available_score(
        [
            (pe_score, 55),
            (pb_score, 45),
        ]
    )


def _calculate_bank_score(data):
    """
    BANK PROFILE

    Important:
    Debt/Equity, Current Ratio, Quick Ratio,
    industrial ROCE and industrial cash-flow
    rules are not used as hard scoring factors.

    Later versions will add banking-specific
    metrics such as:
    NPA, CASA, NIM, capital adequacy,
    loan growth and asset quality.
    """

    roe_score = _score_higher_better(
        data.get(
            "roe"
        ),
        [
            (0.20, 100),
            (0.17, 90),
            (0.14, 80),
            (0.11, 65),
            (0.08, 45),
        ],
    )

    roa_score = _score_higher_better(
        data.get(
            "roa"
        ),
        [
            (0.020, 100),
            (0.017, 90),
            (0.014, 80),
            (0.010, 65),
            (0.007, 45),
        ],
    )

    profitability_score = (
        _weighted_available_score(
            [
                (roe_score, 55),
                (roa_score, 45),
            ]
        )
    )

    growth_score = _growth_score(
        data
    )

    valuation_score = (
        _financial_valuation_score(
            data
        )
    )

    overall_score = (
        _weighted_available_score(
            [
                (
                    profitability_score,
                    45,
                ),
                (
                    growth_score,
                    30,
                ),
                (
                    valuation_score,
                    25,
                ),
            ]
        )
    )

    return {

        "profitability_score":
            profitability_score,

        "growth_score":
            growth_score,

        # None means not yet measured with
        # proper bank-specific metrics.
        "financial_strength_score":
            None,

        "valuation_score":
            valuation_score,

        "fundamental_score":
            overall_score,

        "scoring_profile":
            "BANK",

        "profile_maturity":
            "PROVISIONAL",
    }


def _calculate_financial_services_score(
    data,
):
    """
    NBFC / FINANCIAL SERVICES PROFILE

    Avoids treating normal financial leverage
    as if it were industrial-company debt.

    Later versions will add:
    AUM growth, asset quality, borrowing cost,
    capital adequacy and business-specific KPIs.
    """

    roe_score = _score_higher_better(
        data.get(
            "roe"
        ),
        [
            (0.22, 100),
            (0.18, 90),
            (0.15, 80),
            (0.10, 60),
            (0.07, 40),
        ],
    )

    roa_score = _score_higher_better(
        data.get(
            "roa"
        ),
        [
            (0.05, 100),
            (0.035, 90),
            (0.025, 80),
            (0.015, 60),
            (0.008, 40),
        ],
    )

    profitability_score = (
        _weighted_available_score(
            [
                (roe_score, 60),
                (roa_score, 40),
            ]
        )
    )

    growth_score = _growth_score(
        data
    )

    valuation_score = (
        _financial_valuation_score(
            data
        )
    )

    overall_score = (
        _weighted_available_score(
            [
                (
                    profitability_score,
                    45,
                ),
                (
                    growth_score,
                    30,
                ),
                (
                    valuation_score,
                    25,
                ),
            ]
        )
    )

    return {

        "profitability_score":
            profitability_score,

        "growth_score":
            growth_score,

        "financial_strength_score":
            None,

        "valuation_score":
            valuation_score,

        "fundamental_score":
            overall_score,

        "scoring_profile":
            "FINANCIAL_SERVICES",

        "profile_maturity":
            "PROVISIONAL",
    }


def calculate_sector_aware_fundamental_score(
    data,
    profile="GENERAL",
):

    profile = (
        str(
            profile
            or "GENERAL"
        )
        .strip()
        .upper()
    )

    if profile == "BANK":

        return _calculate_bank_score(
            data
        )

    if profile == "FINANCIAL_SERVICES":

        return (
            _calculate_financial_services_score(
                data
            )
        )

    # IT_SOFTWARE currently uses the mature
    # general model.
    #
    # Sector-relative IT valuation can be added
    # later without disturbing this interface.

    result = calculate_fundamental_score(
        data
    )

    result["scoring_profile"] = (
        profile
    )

    result["profile_maturity"] = (
        "BASELINE"
    )

    return result