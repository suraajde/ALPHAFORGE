def _weighted_available_score(items):
    """
    Calculate a weighted score using only
    metrics that are actually available.
    """

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


def _momentum_score(value):
    """
    Score absolute percentage price return.
    """

    if value is None:
        return None

    if value >= 30:
        return 100

    if value >= 20:
        return 90

    if value >= 10:
        return 80

    if value >= 5:
        return 70

    if value >= 0:
        return 60

    if value >= -10:
        return 45

    if value >= -20:
        return 30

    if value >= -30:
        return 20

    return 10


def _relative_strength_score(value):
    """
    Score stock performance relative to benchmark.

    Positive value:
    Stock outperformed benchmark.

    Negative value:
    Stock underperformed benchmark.
    """

    if value is None:
        return None

    if value >= 30:
        return 100

    if value >= 20:
        return 95

    if value >= 10:
        return 85

    if value >= 5:
        return 75

    if value >= 0:
        return 65

    if value >= -5:
        return 55

    if value >= -10:
        return 45

    if value >= -20:
        return 30

    if value >= -30:
        return 20

    return 10


def _volatility_score(value):
    """
    Lower annualized volatility generally
    receives a better risk score.
    """

    if value is None:
        return None

    if value <= 20:
        return 100

    if value <= 25:
        return 90

    if value <= 30:
        return 80

    if value <= 35:
        return 70

    if value <= 40:
        return 60

    if value <= 50:
        return 45

    if value <= 60:
        return 30

    return 20


def _drawdown_score(value):
    """
    Smaller 1-year maximum drawdown receives
    a better risk score.
    """

    if value is None:
        return None

    drawdown = abs(value)

    if drawdown <= 15:
        return 100

    if drawdown <= 20:
        return 90

    if drawdown <= 25:
        return 80

    if drawdown <= 30:
        return 70

    if drawdown <= 40:
        return 55

    if drawdown <= 50:
        return 40

    if drawdown <= 60:
        return 25

    return 10


def _high_proximity_score(value):
    """
    Score distance from 52-week high.

    Stocks maintaining price structure closer
    to their highs generally score better.
    """

    if value is None:
        return None

    distance = abs(
        min(
            value,
            0,
        )
    )

    if distance <= 5:
        return 100

    if distance <= 10:
        return 90

    if distance <= 15:
        return 80

    if distance <= 20:
        return 70

    if distance <= 30:
        return 55

    if distance <= 40:
        return 40

    if distance <= 50:
        return 25

    return 10


def calculate_technical_score(data):
    """
    Calculate independent technical intelligence.

    Components:

    Trend
    Absolute Momentum
    Relative Strength
    Risk

    This remains separate from the
    Fundamental Score.
    """

    if not data or "error" in data:

        return {
            "trend_score": None,
            "momentum_score": None,
            "relative_strength_score": None,
            "risk_score": None,
            "technical_score": None,
        }

    # --------------------------------------------------
    # TREND
    # --------------------------------------------------

    trend_components = []

    above_50dma = data.get(
        "above_50dma"
    )

    above_200dma = data.get(
        "above_200dma"
    )

    golden_trend = data.get(
        "golden_trend"
    )

    if above_50dma is not None:

        trend_components.append(
            (
                100
                if above_50dma
                else 25,
                30,
            )
        )

    if above_200dma is not None:

        trend_components.append(
            (
                100
                if above_200dma
                else 20,
                40,
            )
        )

    if golden_trend is not None:

        trend_components.append(
            (
                100
                if golden_trend
                else 20,
                30,
            )
        )

    trend_score = (
        _weighted_available_score(
            trend_components
        )
    )

    # --------------------------------------------------
    # ABSOLUTE MOMENTUM
    # --------------------------------------------------

    momentum_3m = _momentum_score(
        data.get(
            "return_3m"
        )
    )

    momentum_6m = _momentum_score(
        data.get(
            "return_6m"
        )
    )

    momentum_12m = _momentum_score(
        data.get(
            "return_12m"
        )
    )

    momentum_score = (
        _weighted_available_score(
            [
                (momentum_3m, 20),
                (momentum_6m, 35),
                (momentum_12m, 45),
            ]
        )
    )

    # --------------------------------------------------
    # RELATIVE STRENGTH
    #
    # Longer-term relative strength receives
    # greater weight because AlphaForge is
    # designed for investment, not trading.
    # --------------------------------------------------

    rs_3m = _relative_strength_score(
        data.get(
            "relative_strength_3m"
        )
    )

    rs_6m = _relative_strength_score(
        data.get(
            "relative_strength_6m"
        )
    )

    rs_12m = _relative_strength_score(
        data.get(
            "relative_strength_12m"
        )
    )

    relative_strength_score = (
        _weighted_available_score(
            [
                (rs_3m, 20),
                (rs_6m, 35),
                (rs_12m, 45),
            ]
        )
    )

    # --------------------------------------------------
    # RISK
    # --------------------------------------------------

    volatility_score = (
        _volatility_score(
            data.get(
                "volatility"
            )
        )
    )

    drawdown_score = (
        _drawdown_score(
            data.get(
                "max_drawdown"
            )
        )
    )

    high_proximity_score = (
        _high_proximity_score(
            data.get(
                "distance_from_52w_high"
            )
        )
    )

    risk_score = (
        _weighted_available_score(
            [
                (volatility_score, 30),
                (drawdown_score, 45),
                (high_proximity_score, 25),
            ]
        )
    )

    # --------------------------------------------------
    # OVERALL TECHNICAL SCORE
    #
    # Relative strength now receives a dedicated
    # weight instead of being hidden inside momentum.
    # --------------------------------------------------

    technical_score = (
        _weighted_available_score(
            [
                (trend_score, 30),
                (momentum_score, 25),
                (relative_strength_score, 25),
                (risk_score, 20),
            ]
        )
    )

    return {
        "trend_score":
            trend_score,

        "momentum_score":
            momentum_score,

        "relative_strength_score":
            relative_strength_score,

        "risk_score":
            risk_score,

        "technical_score":
            technical_score,
    }