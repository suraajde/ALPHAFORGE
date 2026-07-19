def _clamp(value, minimum=0, maximum=100):

    if value is None:
        return None

    return max(
        minimum,
        min(
            maximum,
            float(value),
        ),
    )


def _weighted_available_score(items):

    total = 0.0
    total_weight = 0.0

    for score, weight in items:

        if score is None:
            continue

        score = _clamp(score)

        total += score * weight
        total_weight += weight

    if total_weight == 0:
        return None

    return round(
        total / total_weight,
        1,
    )


def calculate_alpha_composite(
    fundamental_scores,
    technical_scores,
    data_quality,
):
    """
    Alpha Composite Prototype.

    This is NOT the final Alpha Score and is NOT
    a buy/sell recommendation.

    It combines the currently available engines
    while enforcing eligibility and quality gates.
    """

    fundamental_score = (
        fundamental_scores.get(
            "fundamental_score"
        )
    )

    technical_score = (
        technical_scores.get(
            "technical_score"
        )
    )

    profitability_score = (
        fundamental_scores.get(
            "profitability_score"
        )
    )

    growth_score = (
        fundamental_scores.get(
            "growth_score"
        )
    )

    financial_strength_score = (
        fundamental_scores.get(
            "financial_strength_score"
        )
    )

    trend_score = (
        technical_scores.get(
            "trend_score"
        )
    )

    momentum_score = (
        technical_scores.get(
            "momentum_score"
        )
    )

    relative_strength_score = (
        technical_scores.get(
            "relative_strength_score"
        )
    )

    risk_score = (
        technical_scores.get(
            "risk_score"
        )
    )

    confidence_score = (
        data_quality.get(
            "confidence_score"
        )
    )

    eligible_for_ranking = (
        data_quality.get(
            "eligible_for_ranking",
            False,
        )
    )

    # ------------------------------------------
    # Base Composite
    #
    # Fundamentals dominate because AlphaForge
    # is an investment system, not a trading
    # system.
    # ------------------------------------------

    base_composite = (
        _weighted_available_score(
            [
                (
                    fundamental_score,
                    60,
                ),
                (
                    technical_score,
                    40,
                ),
            ]
        )
    )

    # ------------------------------------------
    # Gate Checks
    # ------------------------------------------

    gate_reasons = []

    if not eligible_for_ranking:

        gate_reasons.append(
            "Insufficient data quality"
        )

    if (
        confidence_score is not None
        and confidence_score < 75
    ):

        gate_reasons.append(
            "Low data confidence"
        )

    if (
        fundamental_score is not None
        and fundamental_score < 55
    ):

        gate_reasons.append(
            "Fundamental score below minimum"
        )

    if (
        profitability_score is not None
        and profitability_score < 50
    ):

        gate_reasons.append(
            "Weak profitability"
        )

    if (
        financial_strength_score is not None
        and financial_strength_score < 45
    ):

        gate_reasons.append(
            "Weak financial strength"
        )

    # ------------------------------------------
    # Technical Deterioration Flags
    #
    # These do not automatically reject a strong
    # company. They affect its current readiness.
    # ------------------------------------------

    technical_warnings = []

    if (
        trend_score is not None
        and trend_score < 35
    ):

        technical_warnings.append(
            "Weak price trend"
        )

    if (
        momentum_score is not None
        and momentum_score < 35
    ):

        technical_warnings.append(
            "Weak momentum"
        )

    if (
        relative_strength_score is not None
        and relative_strength_score < 35
    ):

        technical_warnings.append(
            "Benchmark underperformance"
        )

    if (
        risk_score is not None
        and risk_score < 35
    ):

        technical_warnings.append(
            "Elevated price risk"
        )

    # ------------------------------------------
    # Classification
    # ------------------------------------------

    hard_gate_pass = (
        len(gate_reasons) == 0
    )

    technical_warning_count = len(
        technical_warnings
    )

    if not hard_gate_pass:

        classification = (
            "REJECT / REVIEW"
        )

    elif (
        base_composite is not None
        and base_composite >= 80
        and technical_warning_count == 0
    ):

        classification = (
            "HIGH CONVICTION CANDIDATE"
        )

    elif (
        base_composite is not None
        and base_composite >= 70
        and technical_warning_count <= 1
    ):

        classification = (
            "STRONG RADAR CANDIDATE"
        )

    elif (
        fundamental_score is not None
        and fundamental_score >= 75
        and technical_warning_count >= 2
    ):

        classification = (
            "QUALITY WATCHLIST"
        )

    elif (
        base_composite is not None
        and base_composite >= 60
    ):

        classification = (
            "RADAR CANDIDATE"
        )

    else:

        classification = (
            "MONITOR"
        )

    # ------------------------------------------
    # Readiness Score
    #
    # Kept separate from composite so we do not
    # confuse company quality with current setup.
    # ------------------------------------------

    readiness_score = (
        _weighted_available_score(
            [
                (
                    trend_score,
                    30,
                ),
                (
                    momentum_score,
                    25,
                ),
                (
                    relative_strength_score,
                    30,
                ),
                (
                    risk_score,
                    15,
                ),
            ]
        )
    )

    return {

        "fundamental_score":
            fundamental_score,

        "technical_score":
            technical_score,

        "base_composite":
            base_composite,

        "readiness_score":
            readiness_score,

        "data_confidence":
            confidence_score,

        "hard_gate_pass":
            hard_gate_pass,

        "gate_reasons":
            gate_reasons,

        "technical_warnings":
            technical_warnings,

        "classification":
            classification,

        "prototype_only":
            True,
    }