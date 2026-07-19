import math
import yfinance as yf


BENCHMARK_SYMBOL = "^CRSLDX"


def _safe_float(value):

    if value is None:
        return None

    try:

        value = float(value)

        if math.isnan(value) or math.isinf(value):
            return None

        return value

    except (TypeError, ValueError):

        return None


def _percentage_return(
    current_price,
    old_price,
):

    current_price = _safe_float(
        current_price
    )

    old_price = _safe_float(
        old_price
    )

    if (
        current_price is None
        or old_price is None
        or old_price <= 0
    ):

        return None

    return round(
        (
            current_price
            / old_price
            - 1
        ) * 100,
        2,
    )


def _period_return(
    close,
    trading_days,
):

    if len(close) <= trading_days:
        return None

    return _percentage_return(
        close.iloc[-1],
        close.iloc[
            -(trading_days + 1)
        ],
    )


def _relative_strength(
    stock_return,
    benchmark_return,
):

    if (
        stock_return is None
        or benchmark_return is None
    ):

        return None

    return round(
        stock_return
        - benchmark_return,
        2,
    )


def _get_benchmark_returns():

    try:

        benchmark = yf.Ticker(
            BENCHMARK_SYMBOL
        )

        history = benchmark.history(
            period="2y",
            auto_adjust=True,
        )

        if (
            history is None
            or history.empty
            or "Close" not in history.columns
        ):

            return {}

        close = (
            history["Close"]
            .dropna()
        )

        return {
            "benchmark_return_3m":
                _period_return(
                    close,
                    63,
                ),

            "benchmark_return_6m":
                _period_return(
                    close,
                    126,
                ),

            "benchmark_return_12m":
                _period_return(
                    close,
                    252,
                ),
        }

    except Exception:

        return {}


def get_technical_metrics(symbol):

    symbol = symbol.strip().upper()

    if not symbol.endswith(".NS"):

        symbol += ".NS"

    try:

        stock = yf.Ticker(
            symbol
        )

        history = stock.history(
            period="2y",
            auto_adjust=True,
        )

        if (
            history is None
            or history.empty
            or "Close" not in history.columns
        ):

            return {
                "error":
                    "No price history available"
            }

        close = (
            history["Close"]
            .dropna()
        )

        if len(close) < 2:

            return {
                "error":
                    "Insufficient price history"
            }

        current_price = _safe_float(
            close.iloc[-1]
        )

        # --------------------------------------
        # Moving Averages
        # --------------------------------------

        dma_50 = None
        dma_200 = None

        if len(close) >= 50:

            dma_50 = _safe_float(
                close
                .rolling(50)
                .mean()
                .iloc[-1]
            )

        if len(close) >= 200:

            dma_200 = _safe_float(
                close
                .rolling(200)
                .mean()
                .iloc[-1]
            )

        # --------------------------------------
        # Absolute Momentum
        # --------------------------------------

        return_3m = _period_return(
            close,
            63,
        )

        return_6m = _period_return(
            close,
            126,
        )

        return_12m = _period_return(
            close,
            252,
        )

        # --------------------------------------
        # Benchmark Relative Strength
        # --------------------------------------

        benchmark = (
            _get_benchmark_returns()
        )

        benchmark_return_3m = (
            benchmark.get(
                "benchmark_return_3m"
            )
        )

        benchmark_return_6m = (
            benchmark.get(
                "benchmark_return_6m"
            )
        )

        benchmark_return_12m = (
            benchmark.get(
                "benchmark_return_12m"
            )
        )

        relative_strength_3m = (
            _relative_strength(
                return_3m,
                benchmark_return_3m,
            )
        )

        relative_strength_6m = (
            _relative_strength(
                return_6m,
                benchmark_return_6m,
            )
        )

        relative_strength_12m = (
            _relative_strength(
                return_12m,
                benchmark_return_12m,
            )
        )

        # --------------------------------------
        # 52-Week Range
        # --------------------------------------

        lookback_52w = close.tail(
            min(
                252,
                len(close),
            )
        )

        high_52w = _safe_float(
            lookback_52w.max()
        )

        low_52w = _safe_float(
            lookback_52w.min()
        )

        distance_from_52w_high = None

        if (
            current_price is not None
            and high_52w is not None
            and high_52w > 0
        ):

            distance_from_52w_high = round(
                (
                    current_price
                    / high_52w
                    - 1
                ) * 100,
                2,
            )

        # --------------------------------------
        # Volatility
        # --------------------------------------

        daily_returns = (
            close
            .pct_change()
            .dropna()
        )

        volatility = None

        if not daily_returns.empty:

            volatility = (
                daily_returns.std()
                * math.sqrt(252)
                * 100
            )

            volatility = round(
                float(volatility),
                2,
            )

        # --------------------------------------
        # 1-Year Maximum Drawdown
        # --------------------------------------

        risk_window = close.tail(
            min(
                252,
                len(close),
            )
        )

        running_peak = (
            risk_window.cummax()
        )

        drawdown = (
            risk_window
            / running_peak
            - 1
        )

        max_drawdown_1y = None

        if not drawdown.empty:

            max_drawdown_1y = round(
                float(
                    drawdown.min()
                    * 100
                ),
                2,
            )

        # --------------------------------------
        # Trend Flags
        # --------------------------------------

        above_50dma = None

        if (
            current_price is not None
            and dma_50 is not None
        ):

            above_50dma = (
                current_price > dma_50
            )

        above_200dma = None

        if (
            current_price is not None
            and dma_200 is not None
        ):

            above_200dma = (
                current_price > dma_200
            )

        golden_trend = None

        if (
            dma_50 is not None
            and dma_200 is not None
        ):

            golden_trend = (
                dma_50 > dma_200
            )

        return {

            "current_price":
                current_price,

            "dma_50":
                round(dma_50, 2)
                if dma_50 is not None
                else None,

            "dma_200":
                round(dma_200, 2)
                if dma_200 is not None
                else None,

            "above_50dma":
                above_50dma,

            "above_200dma":
                above_200dma,

            "golden_trend":
                golden_trend,

            "return_3m":
                return_3m,

            "return_6m":
                return_6m,

            "return_12m":
                return_12m,

            "benchmark_return_3m":
                benchmark_return_3m,

            "benchmark_return_6m":
                benchmark_return_6m,

            "benchmark_return_12m":
                benchmark_return_12m,

            "relative_strength_3m":
                relative_strength_3m,

            "relative_strength_6m":
                relative_strength_6m,

            "relative_strength_12m":
                relative_strength_12m,

            "high_52w":
                round(high_52w, 2)
                if high_52w is not None
                else None,

            "low_52w":
                round(low_52w, 2)
                if low_52w is not None
                else None,

            "distance_from_52w_high":
                distance_from_52w_high,

            "volatility":
                volatility,

            "max_drawdown":
                max_drawdown_1y,
        }

    except Exception as error:

        return {
            "error": str(error)
        }