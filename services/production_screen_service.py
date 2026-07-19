from __future__ import annotations

import math

import pandas as pd
import yfinance as yf


class ProductionScreenService:
    """
    AlphaForge Production Screening Funnel

    Purpose:
        Reduce the broad MIDCAP + SMALLCAP universe before
        expensive deep Research Radar analysis.

    Design:
        - Batch-download market history.
        - Reject symbols with unusable market data.
        - Calculate lightweight market-health metrics.
        - Rank candidates rather than using aggressive
          short-term trading filters.
        - Preserve MIDCAP / SMALLCAP metadata.
        - Return a manageable candidate pool for the
          full Research Radar engine.

    This is an INVESTMENT pre-screen, not a trading system.
    """

    def __init__(
        self,
        period="1y",
        batch_size=100,
        target_pool=120,
    ):

        self.period = period
        self.batch_size = batch_size
        self.target_pool = target_pool

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _safe_float(value):

        try:

            value = float(value)

            if math.isnan(value):

                return None

            return value

        except Exception:

            return None

    @staticmethod
    def _yf_symbol(symbol):

        symbol = str(
            symbol
        ).strip().upper()

        if not symbol.endswith(
            ".NS"
        ):

            symbol += ".NS"

        return symbol

    @staticmethod
    def _base_symbol(symbol):

        symbol = str(
            symbol
        ).strip().upper()

        if symbol.endswith(
            ".NS"
        ):

            symbol = symbol[:-3]

        return symbol

    # ======================================================
    # DOWNLOAD BATCH
    # ======================================================

    def _download_batch(
        self,
        symbols,
    ):

        yf_symbols = [

            self._yf_symbol(
                symbol
            )

            for symbol in symbols

        ]

        return yf.download(

            tickers=yf_symbols,

            period=self.period,

            interval="1d",

            group_by="ticker",

            auto_adjust=False,

            progress=False,

            threads=True,

        )

    # ======================================================
    # EXTRACT SINGLE SYMBOL HISTORY
    # ======================================================

    def _extract_history(
        self,
        data,
        yf_symbol,
        batch_count,
    ):

        try:

            if batch_count == 1:

                frame = data.copy()

            else:

                if not isinstance(
                    data.columns,
                    pd.MultiIndex,
                ):

                    return None

                level_zero = (
                    data.columns
                    .get_level_values(0)
                )

                if yf_symbol in level_zero:

                    frame = data[
                        yf_symbol
                    ].copy()

                else:

                    return None

            if frame is None:

                return None

            if frame.empty:

                return None

            frame = frame.dropna(
                how="all"
            )

            if frame.empty:

                return None

            return frame

        except Exception:

            return None

    # ======================================================
    # CALCULATE LIGHTWEIGHT MARKET METRICS
    # ======================================================

    def _calculate_metrics(
        self,
        frame,
    ):

        if frame is None:

            return None

        close_column = None

        if "Adj Close" in frame.columns:

            adjusted = frame[
                "Adj Close"
            ].dropna()

            if not adjusted.empty:

                close_column = (
                    "Adj Close"
                )

        if close_column is None:

            if "Close" not in frame.columns:

                return None

            close_column = "Close"

        close = frame[
            close_column
        ].dropna()

        if len(close) < 60:

            return None

        latest_price = self._safe_float(
            close.iloc[-1]
        )

        if (
            latest_price is None
            or latest_price <= 0
        ):

            return None

        trading_days = len(
            close
        )

        # --------------------------------------------------
        # RETURNS
        # --------------------------------------------------

        return_3m = None
        return_6m = None
        return_1y = None

        if trading_days >= 63:

            base = self._safe_float(
                close.iloc[-63]
            )

            if base and base > 0:

                return_3m = (
                    latest_price / base - 1
                ) * 100

        if trading_days >= 126:

            base = self._safe_float(
                close.iloc[-126]
            )

            if base and base > 0:

                return_6m = (
                    latest_price / base - 1
                ) * 100

        if trading_days >= 200:

            base = self._safe_float(
                close.iloc[0]
            )

            if base and base > 0:

                return_1y = (
                    latest_price / base - 1
                ) * 100

        # --------------------------------------------------
        # MOVING AVERAGES
        # --------------------------------------------------

        ma50 = None
        ma200 = None

        if trading_days >= 50:

            ma50 = self._safe_float(
                close.tail(50).mean()
            )

        if trading_days >= 200:

            ma200 = self._safe_float(
                close.tail(200).mean()
            )

        # --------------------------------------------------
        # DRAWDOWN
        # --------------------------------------------------

        running_high = (
            close.cummax()
        )

        drawdown_series = (
            close / running_high - 1
        ) * 100

        max_drawdown = (
            self._safe_float(
                drawdown_series.min()
            )
        )

        # --------------------------------------------------
        # VOLATILITY
        # --------------------------------------------------

        daily_returns = (
            close.pct_change()
            .dropna()
        )

        volatility = None

        if not daily_returns.empty:

            volatility = (
                self._safe_float(
                    daily_returns.std()
                    * math.sqrt(252)
                    * 100
                )
            )

        # --------------------------------------------------
        # LIQUIDITY PROXY
        # --------------------------------------------------

        avg_volume_20d = None

        if "Volume" in frame.columns:

            volume = frame[
                "Volume"
            ].dropna()

            if not volume.empty:

                avg_volume_20d = (
                    self._safe_float(
                        volume.tail(20).mean()
                    )
                )

        return {

            "latest_price":
                latest_price,

            "trading_days":
                trading_days,

            "return_3m":
                return_3m,

            "return_6m":
                return_6m,

            "return_1y":
                return_1y,

            "ma50":
                ma50,

            "ma200":
                ma200,

            "max_drawdown":
                max_drawdown,

            "volatility":
                volatility,

            "avg_volume_20d":
                avg_volume_20d,

        }

    # ======================================================
    # MARKET HEALTH SCORE
    # ======================================================

    def _market_health_score(
        self,
        metrics,
    ):

        score = 50.0
        reasons = []

        price = metrics.get(
            "latest_price"
        )

        ma50 = metrics.get(
            "ma50"
        )

        ma200 = metrics.get(
            "ma200"
        )

        return_3m = metrics.get(
            "return_3m"
        )

        return_6m = metrics.get(
            "return_6m"
        )

        drawdown = metrics.get(
            "max_drawdown"
        )

        volatility = metrics.get(
            "volatility"
        )

        volume = metrics.get(
            "avg_volume_20d"
        )

        # --------------------------------------------------
        # LONG-TERM TREND
        # --------------------------------------------------

        if (
            price is not None
            and ma200 is not None
        ):

            if price >= ma200:

                score += 12

                reasons.append(
                    "Price above 200-day average"
                )

            else:

                score -= 6

        # --------------------------------------------------
        # MEDIUM-TERM TREND
        # --------------------------------------------------

        if (
            price is not None
            and ma50 is not None
        ):

            if price >= ma50:

                score += 8

            else:

                score -= 3

        # --------------------------------------------------
        # MOMENTUM
        # --------------------------------------------------

        if return_6m is not None:

            if return_6m > 20:

                score += 10

            elif return_6m > 0:

                score += 6

            elif return_6m < -25:

                score -= 10

        if return_3m is not None:

            if return_3m > 10:

                score += 5

            elif return_3m < -20:

                score -= 5

        # --------------------------------------------------
        # DRAWDOWN RESILIENCE
        # --------------------------------------------------

        if drawdown is not None:

            if drawdown >= -20:

                score += 8

                reasons.append(
                    "Strong drawdown resilience"
                )

            elif drawdown < -50:

                score -= 10

        # --------------------------------------------------
        # VOLATILITY
        # --------------------------------------------------

        if volatility is not None:

            if volatility <= 35:

                score += 5

            elif volatility > 65:

                score -= 7

        # --------------------------------------------------
        # LIQUIDITY PROXY
        # --------------------------------------------------

        if volume is not None:

            if volume >= 100000:

                score += 5

            elif volume < 10000:

                score -= 10

        score = max(
            0,
            min(
                100,
                score,
            ),
        )

        return (
            round(
                score,
                2,
            ),
            reasons,
        )

    # ======================================================
    # SCREEN UNIVERSE
    # ======================================================

    def screen(
        self,
        stocks,
        target_pool=None,
    ):

        if target_pool is None:

            target_pool = (
                self.target_pool
            )

        clean_stocks = []

        seen = set()

        for stock in stocks:

            if isinstance(
                stock,
                dict,
            ):

                symbol = str(
                    stock.get(
                        "symbol",
                        "",
                    )
                ).strip().upper()

                category = str(
                    stock.get(
                        "category",
                        "",
                    )
                ).strip().upper()

                company = str(
                    stock.get(
                        "company",
                        "",
                    )
                ).strip()

            else:

                symbol = str(
                    stock
                ).strip().upper()

                category = ""

                company = ""

            if not symbol:

                continue

            if symbol in seen:

                continue

            seen.add(
                symbol
            )

            clean_stocks.append({

                "symbol":
                    symbol,

                "company":
                    company,

                "category":
                    category,

            })

        screened = []
        rejected = []

        # --------------------------------------------------
        # PROCESS IN BATCHES
        # --------------------------------------------------

        for start in range(
            0,
            len(clean_stocks),
            self.batch_size,
        ):

            batch = clean_stocks[
                start:
                start + self.batch_size
            ]

            batch_symbols = [

                stock["symbol"]

                for stock in batch

            ]

            try:

                data = self._download_batch(
                    batch_symbols
                )

            except Exception as exc:

                for stock in batch:

                    rejected.append({

                        **stock,

                        "reason":
                            "Batch download failed",

                        "error":
                            str(exc),

                    })

                continue

            for stock in batch:

                symbol = stock[
                    "symbol"
                ]

                yf_symbol = (
                    self._yf_symbol(
                        symbol
                    )
                )

                frame = (
                    self._extract_history(

                        data,

                        yf_symbol,

                        len(batch),

                    )
                )

                metrics = (
                    self._calculate_metrics(
                        frame
                    )
                )

                if metrics is None:

                    rejected.append({

                        **stock,

                        "reason":
                            "Insufficient market history",

                    })

                    continue

                score, reasons = (
                    self._market_health_score(
                        metrics
                    )
                )

                screened.append({

                    **stock,

                    **metrics,

                    "market_health_score":
                        score,

                    "screen_notes":
                        reasons,

                })

        # --------------------------------------------------
        # CONTINUOUS PRE-SCREEN RANKING
        #
        # market_health_score remains the interpretable
        # absolute 0-100 market-health score.
        #
        # screen_rank_score provides continuous ranking
        # discrimination when multiple stocks share the
        # same capped market_health_score.
        #
        # This score is used only for the research funnel.
        # It is NOT the final AlphaForge investment score.
        # --------------------------------------------------

        for item in screened:

            health = (
                self._safe_float(
                    item.get(
                        "market_health_score"
                    )
                )
                or 0
            )

            return_3m = (
                self._safe_float(
                    item.get(
                        "return_3m"
                    )
                )
                or 0
            )

            return_6m = (
                self._safe_float(
                    item.get(
                        "return_6m"
                    )
                )
                or 0
            )

            return_1y = (
                self._safe_float(
                    item.get(
                        "return_1y"
                    )
                )
                or 0
            )

            drawdown = (
                self._safe_float(
                    item.get(
                        "max_drawdown"
                    )
                )
            )

            volatility = (
                self._safe_float(
                    item.get(
                        "volatility"
                    )
                )
            )

            price = (
                self._safe_float(
                    item.get(
                        "latest_price"
                    )
                )
            )

            ma200 = (
                self._safe_float(
                    item.get(
                        "ma200"
                    )
                )
            )

            # ----------------------------------------------
            # BASE MARKET HEALTH
            # ----------------------------------------------

            rank_score = (
                health * 1.00
            )

            # ----------------------------------------------
            # CONTINUOUS MOMENTUM CONTRIBUTION
            #
            # Contributions are deliberately capped so
            # extreme momentum cannot dominate the funnel.
            # ----------------------------------------------

            rank_score += max(
                -8,
                min(
                    8,
                    return_3m * 0.12,
                ),
            )

            rank_score += max(
                -10,
                min(
                    10,
                    return_6m * 0.10,
                ),
            )

            rank_score += max(
                -8,
                min(
                    8,
                    return_1y * 0.04,
                ),
            )

            # ----------------------------------------------
            # DRAWDOWN RESILIENCE
            # ----------------------------------------------

            if drawdown is not None:

                drawdown_component = (
                    6
                    + (
                        drawdown
                        * 0.12
                    )
                )

                rank_score += max(
                    -6,
                    min(
                        6,
                        drawdown_component,
                    ),
                )

            # ----------------------------------------------
            # VOLATILITY DISCIPLINE
            #
            # This is only a modest influence. We do not
            # want to automatically reject quality growth
            # stocks simply because they are more volatile.
            # ----------------------------------------------

            if volatility is not None:

                volatility_component = (
                    5
                    - (
                        volatility
                        * 0.08
                    )
                )

                rank_score += max(
                    -5,
                    min(
                        5,
                        volatility_component,
                    ),
                )

            # ----------------------------------------------
            # 200-DAY TREND POSITION
            # ----------------------------------------------

            if (
                price is not None
                and ma200 is not None
                and ma200 > 0
            ):

                distance_200 = (
                    (
                        price
                        / ma200
                    )
                    - 1
                ) * 100

                rank_score += max(
                    -6,
                    min(
                        6,
                        distance_200
                        * 0.12,
                    ),
                )

            item[
                "screen_rank_score"
            ] = round(
                rank_score,
                4,
            )

        # --------------------------------------------------
        # FINAL PRE-SCREEN SORT
        #
        # Primary:
        #   Continuous screen_rank_score
        #
        # Tie-breakers:
        #   Market health
        #   6-month return
        #   Symbol for deterministic ordering
        # --------------------------------------------------

        screened.sort(

            key=lambda item: (

                item.get(
                    "screen_rank_score",
                    0,
                ),

                item.get(
                    "market_health_score",
                    0,
                ),

                (
                    item.get(
                        "return_6m"
                    )
                    if item.get(
                        "return_6m"
                    ) is not None
                    else -999
                ),

                item.get(
                    "symbol",
                    "",
                ),

            ),

            reverse=True,

        )

        selected = screened[
            :target_pool
        ]

        selected_symbols = {

            item["symbol"]

            for item in selected

        }

        not_selected = [

            {

                **item,

                "reason":
                    "Below pre-screen selection cutoff",

            }

            for item in screened

            if item["symbol"]
            not in selected_symbols

        ]

        rejected.extend(
            not_selected
        )

        # --------------------------------------------------
        # CATEGORY COUNTS
        # --------------------------------------------------

        selected_midcap = sum(

            1

            for item in selected

            if item.get(
                "category"
            ) == "MIDCAP"

        )

        selected_smallcap = sum(

            1

            for item in selected

            if item.get(
                "category"
            ) == "SMALLCAP"

        )

        return {

            "input_count":
                len(clean_stocks),

            "market_data_valid_count":
                len(screened),

            "selected_count":
                len(selected),

            "rejected_count":
                len(rejected),

            "selected_midcap_count":
                selected_midcap,

            "selected_smallcap_count":
                selected_smallcap,

            "selected":
                selected,

            "selected_symbols": [

                item["symbol"]

                for item in selected

            ],

            "rejected":
                rejected,

        }


# ==========================================================
# PUBLIC FUNCTION
# ==========================================================

def screen_production_universe(
    stocks,
    target_pool=120,
):

    service = ProductionScreenService(
        target_pool=target_pool
    )

    return service.screen(
        stocks,
        target_pool=target_pool,
    )