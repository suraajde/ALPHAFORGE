from __future__ import annotations

from services.capital_deployment_service import (
    CapitalDeploymentService,
)


class SmartSIPService:
    """
    AlphaForge Portfolio State & Smart SIP Engine.

    Purpose:
    - Compare current Alpha 12 holdings with target weights.
    - Allocate fresh SIP capital toward portfolio deficits.
    - Use post-SIP portfolio value for target calculations.
    - Buy whole shares only.
    - Avoid selling during normal SIP rebalancing.
    - Preserve residual cash when no sensible purchase exists.

    This service does NOT:
    - Select Alpha 12.
    - Calculate strategic target weights.
    - Fetch live prices.
    - Sell overweight holdings.
    - Perform Alpha 12 replacement decisions.
    """

    def __init__(
        self,
        overshoot_tolerance_pct=0.75,
    ):

        self.overshoot_tolerance_pct = max(
            0.0,
            float(
                overshoot_tolerance_pct
            ),
        )

    @staticmethod
    def _safe_float(
        value,
        default=0.0,
    ):

        try:

            if value is None:
                return float(
                    default
                )

            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return float(
                default
            )

    @staticmethod
    def _normalize_symbol(
        value,
    ):

        return str(
            value
            or ""
        ).strip().upper()

    def _prepare_portfolio(
        self,
        portfolio,
    ):

        if not isinstance(
            portfolio,
            list,
        ):

            raise TypeError(
                "portfolio must be a list"
            )

        clean = []

        seen = set()

        for item in portfolio:

            if not isinstance(
                item,
                dict,
            ):

                continue

            symbol = (
                self._normalize_symbol(
                    item.get(
                        "symbol"
                    )
                )
            )

            if not symbol:

                continue

            if symbol in seen:

                raise ValueError(
                    f"Duplicate portfolio symbol: {symbol}"
                )

            target_weight = (
                self._safe_float(
                    item.get(
                        "target_weight"
                    ),
                    0.0,
                )
            )

            if target_weight < 0:

                raise ValueError(
                    f"Negative target weight for {symbol}"
                )

            row = dict(
                item
            )

            row[
                "symbol"
            ] = symbol

            row[
                "target_weight"
            ] = target_weight

            clean.append(
                row
            )

            seen.add(
                symbol
            )

        if not clean:

            return []

        total_weight = sum(

            row[
                "target_weight"
            ]

            for row in clean

        )

        if total_weight <= 0:

            raise ValueError(
                "Portfolio target weights must total above zero"
            )

        # Normalize weights to exactly 100 internally.

        for row in clean:

            row[
                "target_weight"
            ] = (

                row[
                    "target_weight"
                ]
                / total_weight
                * 100.0

            )

        return clean

    def _prepare_prices(
        self,
        portfolio,
        price_map,
    ):

        if not isinstance(
            price_map,
            dict,
        ):

            raise TypeError(
                "price_map must be a dictionary"
            )

        normalized = {

            self._normalize_symbol(
                symbol
            ):
                self._safe_float(
                    price,
                    0.0,
                )

            for (
                symbol,
                price,
            )
            in price_map.items()

        }

        missing = []

        invalid = []

        prices = {}

        for row in portfolio:

            symbol = row[
                "symbol"
            ]

            if symbol not in normalized:

                missing.append(
                    symbol
                )

                continue

            price = normalized[
                symbol
            ]

            if price <= 0:

                invalid.append(
                    symbol
                )

                continue

            prices[
                symbol
            ] = price

        if missing or invalid:

            messages = []

            if missing:

                messages.append(

                    "Missing prices: "
                    + ", ".join(
                        missing
                    )

                )

            if invalid:

                messages.append(

                    "Invalid prices: "
                    + ", ".join(
                        invalid
                    )

                )

            raise ValueError(
                " | ".join(
                    messages
                )
            )

        return prices

    def _prepare_holdings(
        self,
        portfolio,
        holdings,
    ):

        if holdings is None:

            holdings = {}

        if isinstance(
            holdings,
            list,
        ):

            converted = {}

            for item in holdings:

                if not isinstance(
                    item,
                    dict,
                ):

                    continue

                symbol = (
                    self._normalize_symbol(
                        item.get(
                            "symbol"
                        )
                    )
                )

                if not symbol:

                    continue

                quantity = (
                    self._safe_float(

                        item.get(
                            "quantity",
                            item.get(
                                "current_quantity",
                                0,
                            ),
                        ),

                        0.0,

                    )
                )

                converted[
                    symbol
                ] = quantity

            holdings = converted

        if not isinstance(
            holdings,
            dict,
        ):

            raise TypeError(
                "holdings must be a dictionary or list"
            )

        normalized = {

            self._normalize_symbol(
                symbol
            ):
                self._safe_float(
                    quantity,
                    0.0,
                )

            for (
                symbol,
                quantity,
            )
            in holdings.items()

        }

        result = {}

        for row in portfolio:

            symbol = row[
                "symbol"
            ]

            quantity = normalized.get(
                symbol,
                0.0,
            )

            if quantity < 0:

                raise ValueError(
                    f"Negative holding quantity for {symbol}"
                )

            result[
                symbol
            ] = quantity

        return result

    @staticmethod
    def _quality_score(
        row,
    ):

        for field in (

            "portfolio_quality_score",
            "alpha12_selection_score",
            "alpha12_score",
            "composite_score",

        ):

            value = row.get(
                field
            )

            if isinstance(
                value,
                (
                    int,
                    float,
                ),
            ):

                return float(
                    value
                )

        return 0.0

    def allocate(
        self,
        portfolio,
        holdings,
        sip_amount,
        price_map,
        carry_forward_cash=0.0,
    ):

        sip_amount = self._safe_float(
            sip_amount,
            0.0,
        )

        carry_forward_cash = (
            self._safe_float(
                carry_forward_cash,
                0.0,
            )
        )

        if sip_amount < 0:

            raise ValueError(
                "sip_amount cannot be negative"
            )

        if carry_forward_cash < 0:

            raise ValueError(
                "carry_forward_cash cannot be negative"
            )

        available_cash = (

            sip_amount
            + carry_forward_cash

        )

        if available_cash <= 0:

            raise ValueError(
                "Total SIP capital must be greater than zero"
            )

        clean = (
            self._prepare_portfolio(
                portfolio
            )
        )

        if not clean:

            return {

                "status":
                    "EMPTY",

                "allocations":
                    [],

                "sip_amount":
                    round(
                        sip_amount,
                        2,
                    ),

                "carry_forward_in":
                    round(
                        carry_forward_cash,
                        2,
                    ),

                "available_cash":
                    round(
                        available_cash,
                        2,
                    ),

            }

        prices = (
            self._prepare_prices(
                clean,
                price_map,
            )
        )

        current_holdings = (
            self._prepare_holdings(
                clean,
                holdings,
            )
        )

        rows = []

        current_portfolio_value = 0.0

        # ==================================================
        # CURRENT PORTFOLIO STATE
        # ==================================================

        for item in clean:

            symbol = item[
                "symbol"
            ]

            price = prices[
                symbol
            ]

            current_quantity = (
                current_holdings[
                    symbol
                ]
            )

            current_value = (

                current_quantity
                * price

            )

            current_portfolio_value += (
                current_value
            )

            row = dict(
                item
            )

            row[
                "price"
            ] = price

            row[
                "current_quantity"
            ] = current_quantity

            row[
                "current_value"
            ] = current_value

            row[
                "sip_quantity"
            ] = 0

            row[
                "sip_amount"
            ] = 0.0

            rows.append(
                row
            )

        # ==================================================
        # INITIAL PORTFOLIO ROUTING
        #
        # Empty portfolios use the proven CapitalDeployment
        # engine for initial whole-share construction.
        #
        # Existing invested portfolios continue through the
        # Smart SIP funding-gap algorithm below.
        # ==================================================

        if current_portfolio_value <= 0:

            deployment_service = (
                CapitalDeploymentService(
                    overshoot_tolerance_pct=
                        self.overshoot_tolerance_pct,
                )
            )

            initial = (
                deployment_service.deploy(

                    portfolio=
                        clean,

                    capital=
                        available_cash,

                    price_map=
                        prices,

                )
            )

            allocations = []

            for item in initial.get(
                "allocations",
                [],
            ):

                row = dict(
                    item
                )

                quantity = int(
                    row.get(
                        "quantity",
                        0,
                    )
                    or 0
                )

                actual_amount = (
                    self._safe_float(
                        row.get(
                            "actual_amount",
                            0.0,
                        ),
                        0.0,
                    )
                )

                target_weight = (
                    self._safe_float(
                        row.get(
                            "target_weight",
                            0.0,
                        ),
                        0.0,
                    )
                )

                price = (
                    self._safe_float(
                        row.get(
                            "price",
                            0.0,
                        ),
                        0.0,
                    )
                )

                row[
                    "current_quantity"
                ] = 0

                row[
                    "current_value"
                ] = 0.0

                row[
                    "initial_funding_gap"
                ] = round(

                    available_cash
                    * target_weight
                    / 100.0,

                    2,

                )

                row[
                    "sip_quantity"
                ] = quantity

                row[
                    "sip_amount"
                ] = round(
                    actual_amount,
                    2,
                )

                row[
                    "final_quantity"
                ] = quantity

                row[
                    "final_value"
                ] = round(
                    actual_amount,
                    2,
                )

                row[
                    "final_weight"
                ] = self._safe_float(
                    row.get(
                        "actual_weight",
                        0.0,
                    ),
                    0.0,
                )

                row[
                    "drift_pct"
                ] = round(

                    row[
                        "final_weight"
                    ]
                    - target_weight,

                    2,

                )

                if quantity > 0:

                    row[
                        "action"
                    ] = "BUY"

                elif (
                    price > 0
                    and price
                    > initial.get(
                        "cash_remaining",
                        0.0,
                    )
                ):

                    row[
                        "action"
                    ] = "WAIT_FOR_CASH"

                else:

                    row[
                        "action"
                    ] = "HOLD_NO_SIP"

                allocations.append(
                    row
                )

            return {

                "status":
                    "OK",

                "mode":
                    "INITIAL_DEPLOYMENT",

                "current_portfolio_value":
                    0.0,

                "sip_amount":
                    round(
                        sip_amount,
                        2,
                    ),

                "carry_forward_in":
                    round(
                        carry_forward_cash,
                        2,
                    ),

                "available_cash":
                    round(
                        available_cash,
                        2,
                    ),

                "sip_invested":
                    initial.get(
                        "invested_amount",
                        0.0,
                    ),

                "cash_remaining":
                    initial.get(
                        "cash_remaining",
                        0.0,
                    ),

                "deployment_pct":
                    initial.get(
                        "deployment_pct",
                        0.0,
                    ),

                "buy_count":
                    sum(

                        1

                        for row in allocations

                        if row.get(
                            "sip_quantity",
                            0,
                        )
                        > 0

                    ),

                "allocations":
                    allocations,

            }


        # ==================================================
        # POST-SIP TARGET CAPITAL
        #
        # Carry-forward cash is deployable portfolio capital,
        # so both new SIP and carried cash are included.
        # ==================================================

        post_sip_capital = (

            current_portfolio_value
            + available_cash

        )

        for row in rows:

            target_value = (

                post_sip_capital
                * row[
                    "target_weight"
                ]
                / 100.0

            )

            funding_gap = (

                target_value
                - row[
                    "current_value"
                ]

            )

            current_weight = (

                row[
                    "current_value"
                ]
                / current_portfolio_value
                * 100.0

                if current_portfolio_value > 0

                else 0.0

            )

            row[
                "current_weight"
            ] = current_weight

            row[
                "post_sip_target_value"
            ] = target_value

            row[
                "funding_gap"
            ] = funding_gap

            row[
                "initial_funding_gap"
            ] = funding_gap

            row[
                "is_underweight"
            ] = (
                funding_gap > 0
            )

        cash_remaining = (
            available_cash
        )

        # ==================================================
        # SMART WHOLE-SHARE SIP ALLOCATION
        #
        # One share is allocated at a time.
        #
        # Priority:
        # 1. Largest percentage deficit vs post-SIP target.
        # 2. Largest rupee funding gap.
        # 3. Higher portfolio quality.
        #
        # Overweight stocks receive no SIP unless their
        # target deficit becomes positive.
        # ==================================================

        while True:

            candidates = []

            for index, row in enumerate(
                rows
            ):

                price = row[
                    "price"
                ]

                if price > (
                    cash_remaining
                    + 1e-9
                ):

                    continue

                current_plus_sip = (

                    row[
                        "current_value"
                    ]
                    + row[
                        "sip_amount"
                    ]

                )

                current_gap = (

                    row[
                        "post_sip_target_value"
                    ]
                    - current_plus_sip

                )

                if current_gap <= 0:

                    continue

                next_value = (

                    current_plus_sip
                    + price

                )

                next_weight = (

                    next_value
                    / post_sip_capital
                    * 100.0

                )

                max_allowed_weight = (

                    row[
                        "target_weight"
                    ]
                    + self.overshoot_tolerance_pct

                )

                if (
                    next_weight
                    > max_allowed_weight
                    + 1e-9
                ):

                    continue

                gap_pct = (

                    current_gap
                    / post_sip_capital
                    * 100.0

                )

                candidates.append((

                    gap_pct,

                    current_gap,

                    self._quality_score(
                        row
                    ),

                    -price,

                    index,

                ))

            if not candidates:

                break

            candidates.sort(
                reverse=True
            )

            selected_index = (
                candidates[
                    0
                ][
                    -1
                ]
            )

            selected = rows[
                selected_index
            ]

            selected[
                "sip_quantity"
            ] += 1

            selected[
                "sip_amount"
            ] += selected[
                "price"
            ]

            cash_remaining -= (
                selected[
                    "price"
                ]
            )

        # ==================================================
        # FINAL PORTFOLIO STATE
        # ==================================================

        total_sip_invested = sum(

            row[
                "sip_amount"
            ]

            for row in rows

        )

        final_invested_value = (

            current_portfolio_value
            + total_sip_invested

        )

        for row in rows:

            final_quantity = (

                row[
                    "current_quantity"
                ]
                + row[
                    "sip_quantity"
                ]

            )

            final_value = (

                row[
                    "current_value"
                ]
                + row[
                    "sip_amount"
                ]

            )

            final_weight = (

                final_value
                / final_invested_value
                * 100.0

                if final_invested_value > 0

                else 0.0

            )

            post_sip_gap = (

                row[
                    "post_sip_target_value"
                ]
                - final_value

            )

            if row[
                "sip_quantity"
            ] > 0:

                action = "BUY"

            elif row[
                "initial_funding_gap"
            ] <= 0:

                action = "HOLD_NO_SIP"

            elif row[
                "price"
            ] > available_cash:

                action = "WAIT_FOR_CASH"

            else:

                action = "HOLD_NO_SIP"

            row[
                "final_quantity"
            ] = final_quantity

            row[
                "final_value"
            ] = final_value

            row[
                "final_weight"
            ] = final_weight

            row[
                "post_sip_gap"
            ] = post_sip_gap

            row[
                "drift_pct"
            ] = (

                final_weight
                - row[
                    "target_weight"
                ]

            )

            row[
                "action"
            ] = action

        # ==================================================
        # ROUND USER-FACING VALUES
        # ==================================================

        for row in rows:

            for field in (

                "target_weight",
                "price",
                "current_value",
                "current_weight",
                "post_sip_target_value",
                "initial_funding_gap",
                "sip_amount",
                "final_value",
                "final_weight",
                "post_sip_gap",
                "drift_pct",

            ):

                row[
                    field
                ] = round(
                    self._safe_float(
                        row.get(
                            field
                        ),
                        0.0,
                    ),
                    2,
                )

            row[
                "funding_gap"
            ] = round(
                row[
                    "initial_funding_gap"
                ],
                2,
            )

        rows.sort(

            key=lambda row: (

                row.get(
                    "alpha12_rank",
                    row.get(
                        "rank",
                        999,
                    ),
                ),

                row[
                    "symbol"
                ],

            )

        )

        buy_count = sum(

            1

            for row in rows

            if row[
                "sip_quantity"
            ] > 0

        )

        return {

            "status":
                "OK",

            "position_count":
                len(
                    rows
                ),

            "current_portfolio_value":
                round(
                    current_portfolio_value,
                    2,
                ),

            "sip_amount":
                round(
                    sip_amount,
                    2,
                ),

            "carry_forward_in":
                round(
                    carry_forward_cash,
                    2,
                ),

            "available_cash":
                round(
                    available_cash,
                    2,
                ),

            "post_sip_target_capital":
                round(
                    post_sip_capital,
                    2,
                ),

            "sip_invested":
                round(
                    total_sip_invested,
                    2,
                ),

            "cash_remaining":
                round(
                    cash_remaining,
                    2,
                ),

            "deployment_pct":
                round(

                    (
                        total_sip_invested
                        / available_cash
                        * 100.0
                    )

                    if available_cash > 0

                    else 0.0,

                    2,

                ),

            "buy_count":
                buy_count,

            "allocations":
                rows,

        }


def build_smart_sip(
    portfolio,
    holdings,
    sip_amount,
    price_map,
    carry_forward_cash=0.0,
    overshoot_tolerance_pct=0.75,
):

    service = SmartSIPService(

        overshoot_tolerance_pct=
            overshoot_tolerance_pct

    )

    return service.allocate(

        portfolio=
            portfolio,

        holdings=
            holdings,

        sip_amount=
            sip_amount,

        price_map=
            price_map,

        carry_forward_cash=
            carry_forward_cash,

    )
