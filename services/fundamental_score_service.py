def _score_higher_better(value, levels):
    """
    Score metrics where a higher value is generally better.

    levels:
    [
        (excellent_threshold, 100),
        (good_threshold, 80),
        ...
    ]
    """

    if value is None:
        return None

    for threshold, score in levels:
        if value >= threshold:
            return score

    return 20


def _score_lower_better(value, levels):
    """
    Score metrics where a lower positive value is generally better.
    """

    if value is None:
        return None

    if value < 0:
        return 20

    for threshold, score in levels:
        if value <= threshold:
            return score

    return 20


def _weighted_available_score(items):
    """
    Calculate a weighted score using only available metrics.

    Missing data is excluded rather than incorrectly
    receiving a score of zero.
    """

    total = 0
    total_weight = 0

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


def calculate_fundamental_score(data):

    # --------------------------------------------------
    # PROFITABILITY / CAPITAL EFFICIENCY
    # --------------------------------------------------

    roe_score = _score_higher_better(
        data.get("roe"),
        [
            (0.25, 100),
            (0.20, 90),
            (0.15, 80),
            (0.10, 60),
            (0.05, 40),
        ],
    )

    roa_score = _score_higher_better(
        data.get("roa"),
        [
            (0.15, 100),
            (0.10, 85),
            (0.07, 70),
            (0.04, 50),
            (0.02, 35),
        ],
    )

    roce = data.get("roce")

    if roce is not None:

        roce_score = _score_higher_better(
            roce,
            [
                (25, 100),
                (20, 90),
                (15, 80),
                (12, 65),
                (8, 45),
            ],
        )

    else:
        roce_score = None

    operating_margin_score = _score_higher_better(
        data.get("operating_margin"),
        [
            (0.25, 100),
            (0.20, 90),
            (0.15, 75),
            (0.10, 60),
            (0.05, 40),
        ],
    )

    profit_margin_score = _score_higher_better(
        data.get("profit_margin"),
        [
            (0.20, 100),
            (0.15, 90),
            (0.10, 75),
            (0.05, 55),
            (0.02, 35),
        ],
    )

    profitability_score = _weighted_available_score(
        [
            (roce_score, 30),
            (roe_score, 25),
            (roa_score, 15),
            (operating_margin_score, 15),
            (profit_margin_score, 15),
        ]
    )

    # --------------------------------------------------
    # GROWTH
    # --------------------------------------------------

    revenue_growth_score = _score_higher_better(
        data.get("revenue_growth"),
        [
            (0.20, 100),
            (0.15, 90),
            (0.10, 80),
            (0.05, 60),
            (0.00, 40),
        ],
    )

    earnings_growth_score = _score_higher_better(
        data.get("earnings_growth"),
        [
            (0.25, 100),
            (0.20, 90),
            (0.15, 80),
            (0.10, 70),
            (0.05, 55),
            (0.00, 40),
        ],
    )

    growth_score = _weighted_available_score(
        [
            (revenue_growth_score, 45),
            (earnings_growth_score, 55),
        ]
    )

    # --------------------------------------------------
    # FINANCIAL STRENGTH
    # --------------------------------------------------

    debt_equity = data.get("debt_equity")

    # Yahoo commonly reports debtToEquity as a percentage.
    # Example: 9.827 means approximately 0.09827 D/E.
    if debt_equity is not None:
        debt_equity = debt_equity / 100

    debt_score = _score_lower_better(
        debt_equity,
        [
            (0.10, 100),
            (0.30, 90),
            (0.50, 80),
            (1.00, 60),
            (1.50, 40),
        ],
    )

    current_ratio_score = None

    current_ratio = data.get("current_ratio")

    if current_ratio is not None:

        if 1.5 <= current_ratio <= 3.0:
            current_ratio_score = 100

        elif 1.2 <= current_ratio < 1.5:
            current_ratio_score = 80

        elif 1.0 <= current_ratio < 1.2:
            current_ratio_score = 60

        elif current_ratio > 3.0:
            current_ratio_score = 75

        else:
            current_ratio_score = 30

    cash_flow_score = None

    operating_cash_flow = data.get(
        "operating_cash_flow"
    )

    free_cash_flow = data.get(
        "free_cash_flow"
    )

    if (
        operating_cash_flow is not None
        and free_cash_flow is not None
    ):

        if (
            operating_cash_flow > 0
            and free_cash_flow > 0
        ):
            cash_flow_score = 100

        elif operating_cash_flow > 0:
            cash_flow_score = 65

        else:
            cash_flow_score = 20

    financial_strength_score = (
        _weighted_available_score(
            [
                (debt_score, 40),
                (current_ratio_score, 25),
                (cash_flow_score, 35),
            ]
        )
    )

    # --------------------------------------------------
    # VALUATION
    #
    # This is deliberately conservative.
    # Sector-relative valuation will be added later.
    # --------------------------------------------------

    pe_score = _score_lower_better(
        data.get("pe"),
        [
            (15, 100),
            (20, 85),
            (25, 70),
            (35, 55),
            (50, 40),
        ],
    )

    peg_score = _score_lower_better(
        data.get("peg"),
        [
            (1.0, 100),
            (1.5, 85),
            (2.0, 70),
            (3.0, 50),
            (4.0, 35),
        ],
    )

    valuation_score = _weighted_available_score(
        [
            (pe_score, 55),
            (peg_score, 45),
        ]
    )

    # --------------------------------------------------
    # OVERALL FUNDAMENTAL SCORE
    # --------------------------------------------------

    overall_score = _weighted_available_score(
        [
            (profitability_score, 40),
            (growth_score, 25),
            (financial_strength_score, 20),
            (valuation_score, 15),
        ]
    )

    return {

        "profitability_score":
            profitability_score,

        "growth_score":
            growth_score,

        "financial_strength_score":
            financial_strength_score,

        "valuation_score":
            valuation_score,

        "fundamental_score":
            overall_score,
    }