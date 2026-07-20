from collections import Counter


class Alpha12SelectionService:

    """
    AlphaForge Alpha 12 Selection Engine

    Purpose
    -------
    Convert the production Research Radar Top candidates into
    a concentrated but diversified Alpha 12 research portfolio.

    Architecture
    ------------
    Production Universe
        -> Production Pre-Screen
        -> Research Radar
        -> Top 30
        -> Alpha 12 Selection Engine

    IMPORTANT
    ---------
    - Research Radar rank is preserved.
    - Alpha 12 rank is separate.
    - The engine does not modify upstream scoring.
    - Diversification is applied after stock-quality ranking.
    - Portfolio weighting is intentionally NOT handled here.
    """

    DEFAULT_TARGET_COUNT = 12

    DEFAULT_RESERVE_COUNT = 8

    DEFAULT_NORMAL_SECTOR_LIMIT = 2

    # A third stock from the same sector is allowed only when
    # it is materially stronger than the next diversification
    # alternative.

    DEFAULT_SECTOR_OVERRIDE_GAP = 6.0

    def __init__(
        self,
        target_count=12,
        reserve_count=8,
        normal_sector_limit=2,
        sector_override_gap=6.0,
    ):

        self.target_count = max(
            1,
            int(target_count),
        )

        self.reserve_count = max(
            0,
            int(reserve_count),
        )

        self.normal_sector_limit = max(
            1,
            int(normal_sector_limit),
        )

        self.sector_override_gap = max(
            0.0,
            float(sector_override_gap),
        )

    # ======================================================
    # SAFE NUMERIC CONVERSION
    # ======================================================

    @staticmethod
    def _number(
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

    # ======================================================
    # CLEAN TEXT
    # ======================================================

    @staticmethod
    def _text(
        value,
        default="UNKNOWN",
    ):

        if value is None:

            return default

        value = str(
            value
        ).strip()

        if not value:

            return default

        return value

    # ======================================================
    # DATA CONFIDENCE NORMALIZER
    # ======================================================

    def _confidence_score(
        self,
        item,
    ):

        value = item.get(
            "data_confidence"
        )

        if isinstance(
            value,
            str,
        ):

            text = (
                value
                .strip()
                .upper()
            )

            mapping = {

                "HIGH":
                    90.0,

                "MEDIUM":
                    70.0,

                "MODERATE":
                    70.0,

                "LOW":
                    45.0,

            }

            if text in mapping:

                return mapping[
                    text
                ]

        return self._number(
            value,
            50.0,
        )

    # ======================================================
    # CAUTION PENALTY
    # ======================================================

    def _caution_penalty(
        self,
        item,
    ):

        penalty = 0.0

        if item.get(
            "data_caution"
        ):

            penalty += 4.0

        data_status = (

            self._text(
                item.get(
                    "data_status"
                ),
                "",
            )
            .upper()

        )

        if data_status not in {
            "",
            "CLEAN",
        }:

            penalty += 2.0

        classification = (

            self._text(
                item.get(
                    "classification"
                ),
                "",
            )
            .upper()

        )

        if (
            "PROVISIONAL"
            in classification
        ):

            penalty += 3.0

        ranking_notes = item.get(
            "ranking_notes",
            [],
        )

        if isinstance(
            ranking_notes,
            list,
        ):

            penalty += min(
                len(
                    ranking_notes
                )
                * 0.5,
                2.0,
            )

        return penalty

    # ======================================================
    # ALPHA 12 BASE SCORE
    # ======================================================

    def _calculate_base_score(
        self,
        item,
        radar_position,
    ):

        composite = self._number(
            item.get(
                "composite_score"
            )
        )

        fundamental = self._number(
            item.get(
                "fundamental_score"
            )
        )

        readiness = self._number(
            item.get(
                "readiness_score"
            )
        )

        market_health = self._number(
            item.get(
                "market_health_score"
            )
        )

        confidence = (
            self._confidence_score(
                item
            )
        )

        coverage = self._number(
            item.get(
                "coverage_score"
            ),
            50.0,
        )

        # --------------------------------------------------
        # QUALITY-LED PORTFOLIO SELECTION SCORE
        #
        # Composite remains dominant because it already
        # combines AlphaForge fundamental + technical logic.
        #
        # Fundamental quality receives additional emphasis
        # because Alpha 12 is an investment portfolio rather
        # than a short-term trading list.
        # --------------------------------------------------

        score = (

            composite
            * 0.40

            + fundamental
            * 0.20

            + readiness
            * 0.12

            + market_health
            * 0.10

            + confidence
            * 0.10

            + coverage
            * 0.08

        )

        # --------------------------------------------------
        # SMALL RADAR-RANK PRESERVATION BONUS
        #
        # Prevents diversification logic from unnecessarily
        # overturning the upstream Research Radar ordering.
        # --------------------------------------------------

        rank_bonus = max(

            0.0,

            3.0
            - (
                max(
                    radar_position - 1,
                    0,
                )
                * 0.10
            ),

        )

        score += rank_bonus

        score -= (
            self._caution_penalty(
                item
            )
        )

        return round(
            score,
            4,
        )

    # ======================================================
    # PREPARE CANDIDATES
    # ======================================================

    def _prepare_candidates(
        self,
        ranked,
    ):

        candidates = []

        seen_symbols = set()

        for position, raw in enumerate(
            ranked,
            start=1,
        ):

            if not isinstance(
                raw,
                dict,
            ):

                continue

            symbol = (

                self._text(
                    raw.get(
                        "symbol"
                    ),
                    "",
                )
                .upper()

            )

            if not symbol:

                continue

            if symbol in seen_symbols:

                continue

            seen_symbols.add(
                symbol
            )

            # Alpha 12 must never promote a stock explicitly
            # marked non-production-eligible.

            if (
                raw.get(
                    "production_eligible"
                )
                is False
            ):

                continue

            item = dict(
                raw
            )

            radar_rank = item.get(
                "rank"
            )

            try:

                radar_rank = int(
                    radar_rank
                )

            except (
                TypeError,
                ValueError,
            ):

                radar_rank = position

            item[
                "radar_rank"
            ] = radar_rank

            item[
                "alpha12_base_score"
            ] = (
                self._calculate_base_score(
                    item,
                    position,
                )
            )

            item[
                "alpha12_selection_score"
            ] = item[
                "alpha12_base_score"
            ]

            item[
                "sector"
            ] = self._text(
                item.get(
                    "sector"
                )
            )

            item[
                "category"
            ] = (

                self._text(
                    item.get(
                        "category"
                    )
                )
                .upper()

            )

            candidates.append(
                item
            )

        candidates.sort(

            key=lambda item: (

                item.get(
                    "alpha12_base_score",
                    0,
                ),

                item.get(
                    "composite_score",
                    0,
                ),

                -item.get(
                    "radar_rank",
                    9999,
                ),

            ),

            reverse=True,

        )

        return candidates

    # ======================================================
    # FIND BEST DIVERSIFICATION ALTERNATIVE
    # ======================================================

    def _best_sector_alternative_score(
        self,
        candidates,
        selected_symbols,
        sector_counts,
    ):

        for candidate in candidates:

            symbol = candidate[
                "symbol"
            ]

            if symbol in selected_symbols:

                continue

            sector = candidate[
                "sector"
            ]

            if (
                sector_counts[
                    sector
                ]
                < self.normal_sector_limit
            ):

                return candidate[
                    "alpha12_base_score"
                ]

        return None

    # ======================================================
    # SELECT ALPHA 12
    # ======================================================

    def select(
        self,
        ranked,
    ):

        candidates = (
            self._prepare_candidates(
                ranked
            )
        )

        selected = []

        deferred = []

        sector_counts = Counter()

        selected_symbols = set()

        # ==================================================
        # QUALITY-AWARE DIVERSIFICATION
        #
        # Selection is iterative because sector concentration
        # changes after every stock is selected.
        #
        # First two stocks from a sector:
        #     No concentration penalty
        #
        # Third stock:
        #     Moderate penalty
        #
        # Fourth stock:
        #     Strong penalty
        #
        # Fifth and later:
        #     Very strong penalty
        #
        # This allows an exceptional third stock from a strong
        # sector to remain competitive without allowing one
        # sector to dominate Alpha 12 automatically.
        # ==================================================

        def sector_penalty(
            existing_count,
        ):

            if existing_count < 2:

                return 0.0

            if existing_count == 2:

                return 3.0

            if existing_count == 3:

                return 7.0

            return 12.0

        remaining = [

            dict(
                candidate
            )

            for candidate in candidates

        ]

        while (
            remaining
            and len(
                selected
            )
            < self.target_count
        ):

            scored_candidates = []

            for candidate in remaining:

                sector = candidate[
                    "sector"
                ]

                existing_count = (
                    sector_counts[
                        sector
                    ]
                )

                concentration_penalty = (
                    sector_penalty(
                        existing_count
                    )
                )

                adjusted_score = (

                    candidate[
                        "alpha12_base_score"
                    ]

                    - concentration_penalty

                )

                scored_candidates.append((

                    adjusted_score,

                    candidate[
                        "alpha12_base_score"
                    ],

                    -candidate.get(
                        "radar_rank",
                        9999,
                    ),

                    concentration_penalty,

                    candidate,

                ))

            scored_candidates.sort(
                key=lambda row: (
                    row[0],
                    row[1],
                    row[2],
                ),
                reverse=True,
            )

            (
                adjusted_score,
                base_score,
                _,
                concentration_penalty,
                candidate,
            ) = scored_candidates[0]

            chosen = dict(
                candidate
            )

            chosen[
                "alpha12_selection_score"
            ] = round(
                adjusted_score,
                4,
            )

            chosen[
                "sector_concentration_penalty"
            ] = concentration_penalty

            existing_sector_count = (
                sector_counts[
                    chosen[
                        "sector"
                    ]
                ]
            )

            if concentration_penalty == 0:

                chosen[
                    "selection_reason"
                ] = (

                    "Selected on Alpha 12 quality score "
                    "with no sector concentration penalty"

                )

            else:

                chosen[
                    "selection_reason"
                ] = (

                    "Selected after quality-aware sector "
                    "diversification adjustment"

                )

            if existing_sector_count >= 2:

                chosen[
                    "sector_override"
                ] = True

            selected.append(
                chosen
            )

            selected_symbols.add(
                chosen[
                    "symbol"
                ]
            )

            sector_counts[
                chosen[
                    "sector"
                ]
            ] += 1

            remaining = [

                item

                for item in remaining

                if item[
                    "symbol"
                ]
                != chosen[
                    "symbol"
                ]

            ]

        # ==================================================
        # RECORD NON-SELECTED CANDIDATES
        # ==================================================

        for candidate in remaining:

            deferred_item = dict(
                candidate
            )

            sector = deferred_item[
                "sector"
            ]

            concentration_penalty = (
                sector_penalty(
                    sector_counts[
                        sector
                    ]
                )
            )

            deferred_item[
                "sector_concentration_penalty"
            ] = concentration_penalty

            deferred_item[
                "alpha12_selection_score"
            ] = round(

                deferred_item[
                    "alpha12_base_score"
                ]
                - concentration_penalty,

                4,

            )

            if concentration_penalty > 0:

                deferred_item[
                    "defer_reason"
                ] = (

                    "Not selected after sector "
                    "concentration adjustment"

                )

            else:

                deferred_item[
                    "defer_reason"
                ] = (

                    "Outside current Alpha 12 "
                    "selection cutoff"

                )

            deferred.append(
                deferred_item
            )

        # ==================================================
        # FINAL ALPHA 12 ORDER
        # ==================================================

        selected.sort(

            key=lambda item: (

                item.get(
                    "alpha12_base_score",
                    0,
                ),

                item.get(
                    "composite_score",
                    0,
                ),

            ),

            reverse=True,

        )

        for index, item in enumerate(
            selected,
            start=1,
        ):

            item[
                "alpha12_rank"
            ] = index

        # ==================================================
        # RESERVE POOL
        #
        # Reserve candidates are evaluated against the FINAL
        # Alpha 12 sector composition.
        #
        # This prevents a heavily represented sector from
        # showing an artificially high unadjusted reserve
        # score.
        #
        # IMPORTANT:
        # Reserve scoring does not alter Alpha 12 selection.
        # It only improves replacement-pool ranking.
        # ==================================================

        remaining = [

            dict(
                item
            )

            for item in candidates

            if item[
                "symbol"
            ]
            not in selected_symbols

        ]

        reserve_candidates = []

        for item in remaining:

            sector = item[
                "sector"
            ]

            existing_sector_count = (
                sector_counts[
                    sector
                ]
            )

            concentration_penalty = (
                sector_penalty(
                    existing_sector_count
                )
            )

            item[
                "sector_concentration_penalty"
            ] = concentration_penalty

            item[
                "alpha12_selection_score"
            ] = round(

                item[
                    "alpha12_base_score"
                ]
                - concentration_penalty,

                4,

            )

            if concentration_penalty > 0:

                item[
                    "reserve_reason"
                ] = (

                    "Reserve score adjusted for current "
                    "Alpha 12 sector concentration"

                )

            else:

                item[
                    "reserve_reason"
                ] = (

                    "Reserve candidate with no current "
                    "sector concentration penalty"

                )

            reserve_candidates.append(
                item
            )

        reserve_candidates.sort(

            key=lambda item: (

                item.get(
                    "alpha12_selection_score",
                    0,
                ),

                item.get(
                    "alpha12_base_score",
                    0,
                ),

                -item.get(
                    "radar_rank",
                    9999,
                ),

            ),

            reverse=True,

        )

        reserves = reserve_candidates[
            :self.reserve_count
        ]

        reserve_symbols = {

            item[
                "symbol"
            ]

            for item in reserves

        }

        for index, item in enumerate(
            reserves,
            start=1,
        ):

            item[
                "reserve_rank"
            ] = index

            item[
                "selection_reason"
            ] = item.get(

                "reserve_reason",

                "Reserve candidate for Alpha 12 "
                "replacement consideration",

            )

        # ==================================================
        # DEFERRED / EXCLUDED
        # ==================================================

        excluded = [

            item

            for item in remaining

            if item[
                "symbol"
            ]
            not in reserve_symbols

        ]

        for item in excluded:

            if not item.get(
                "defer_reason"
            ):

                item[
                    "defer_reason"
                ] = (

                    "Outside current Alpha 12 "
                    "and reserve selection range"

                )

        # ==================================================
        # CATEGORY / SECTOR DIAGNOSTICS
        # ==================================================

        midcap_count = sum(

            1

            for item in selected

            if item.get(
                "category"
            )
            == "MIDCAP"

        )

        smallcap_count = sum(

            1

            for item in selected

            if item.get(
                "category"
            )
            == "SMALLCAP"

        )

        final_sector_counts = dict(

            Counter(

                item[
                    "sector"
                ]

                for item in selected

            )

        )

        return {

            "status":
                "OK",

            "input_count":
                len(
                    ranked
                ),

            "prepared_count":
                len(
                    candidates
                ),

            "selected_count":
                len(
                    selected
                ),

            "reserve_count":
                len(
                    reserves
                ),

            "excluded_count":
                len(
                    excluded
                ),

            "selected_midcap_count":
                midcap_count,

            "selected_smallcap_count":
                smallcap_count,

            "sector_counts":
                final_sector_counts,

            "selected":
                selected,

            "reserves":
                reserves,

            "excluded":
                excluded,

        }


# ==========================================================
# PUBLIC HELPER
# ==========================================================

def select_alpha12(
    ranked,
    target_count=12,
    reserve_count=8,
):

    service = Alpha12SelectionService(

        target_count=
            target_count,

        reserve_count=
            reserve_count,

    )

    return service.select(
        ranked
    )
