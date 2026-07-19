class DataCompletenessService:

    """
    AlphaForge Data Completeness Resolver

    Purpose:
    Separate raw data availability from
    ranking eligibility.

    A missing field should not automatically
    reject a stock when sufficient independent
    evidence exists elsewhere.

    IMPORTANT:
    This service never invents financial values.
    """

    # --------------------------------------------------
    # PROFITABILITY GROUP
    # --------------------------------------------------

    PROFITABILITY_FIELDS = [
        "roe",
        "roa",
        "roce",
        "operating_margin",
        "profit_margin",
    ]

    # --------------------------------------------------
    # GROWTH GROUP
    # --------------------------------------------------

    GROWTH_FIELDS = [
        "revenue_growth",
        "earnings_growth",
    ]

    # --------------------------------------------------
    # BALANCE SHEET / LIQUIDITY GROUP
    # --------------------------------------------------

    BALANCE_SHEET_FIELDS = [
        "debt_equity",
        "current_ratio",
        "quick_ratio",
        "total_cash",
        "total_debt",
    ]

    # --------------------------------------------------
    # CASH FLOW GROUP
    # --------------------------------------------------

    CASH_FLOW_FIELDS = [
        "free_cash_flow",
        "operating_cash_flow",
    ]

    # --------------------------------------------------
    # VALUATION GROUP
    # --------------------------------------------------

    VALUATION_FIELDS = [
        "pe",
        "forward_pe",
        "pb",
        "peg",
    ]

    # --------------------------------------------------
    # VALUE CHECK
    # --------------------------------------------------

    def _is_available(
        self,
        value,
    ):

        return value is not None

    # --------------------------------------------------
    # GROUP COVERAGE
    # --------------------------------------------------

    def _group_coverage(
        self,
        data,
        fields,
    ):

        available = []

        missing = []

        for field in fields:

            value = data.get(
                field
            )

            if self._is_available(
                value
            ):

                available.append(
                    field
                )

            else:

                missing.append(
                    field
                )

        total = len(
            fields
        )

        available_count = len(
            available
        )

        if total == 0:

            coverage = 0.0

        else:

            coverage = round(
                (
                    available_count
                    / total
                )
                * 100,
                1,
            )

        return {

            "available":
                available,

            "missing":
                missing,

            "available_count":
                available_count,

            "total_count":
                total,

            "coverage":
                coverage,
        }

    # --------------------------------------------------
    # MAIN ANALYSIS
    # --------------------------------------------------

    def analyze(
        self,
        data,
        profile="GENERAL",
    ):

        if not data:

            return {

                "coverage_score":
                    0.0,

                "coverage_level":
                    "INSUFFICIENT",

                "ranking_data_ready":
                    False,

                "blocking_reasons":
                    [
                        "No fundamental data available"
                    ],

                "metric_status":
                    {},

                "groups":
                    {},
            }

        profile = (
            str(
                profile
                or "GENERAL"
            )
            .strip()
            .upper()
        )

        # ----------------------------------------------
        # METRIC STATUS
        #
        # At this stage:
        #
        # DIRECT  = returned by data source
        # MISSING = unavailable
        #
        # DERIVED support will be added only when
        # AlphaForge has reliable underlying inputs.
        # ----------------------------------------------

        all_fields = list(
            dict.fromkeys(
                self.PROFITABILITY_FIELDS
                + self.GROWTH_FIELDS
                + self.BALANCE_SHEET_FIELDS
                + self.CASH_FLOW_FIELDS
                + self.VALUATION_FIELDS
            )
        )

        metric_status = {}

        for field in all_fields:

            if self._is_available(
                data.get(
                    field
                )
            ):

                metric_status[
                    field
                ] = "DIRECT"

            else:

                metric_status[
                    field
                ] = "MISSING"

        # ----------------------------------------------
        # GROUP COVERAGE
        # ----------------------------------------------

        profitability = (
            self._group_coverage(
                data,
                self.PROFITABILITY_FIELDS,
            )
        )

        growth = (
            self._group_coverage(
                data,
                self.GROWTH_FIELDS,
            )
        )

        balance_sheet = (
            self._group_coverage(
                data,
                self.BALANCE_SHEET_FIELDS,
            )
        )

        cash_flow = (
            self._group_coverage(
                data,
                self.CASH_FLOW_FIELDS,
            )
        )

        valuation = (
            self._group_coverage(
                data,
                self.VALUATION_FIELDS,
            )
        )

        groups = {

            "profitability":
                profitability,

            "growth":
                growth,

            "balance_sheet":
                balance_sheet,

            "cash_flow":
                cash_flow,

            "valuation":
                valuation,
        }

        # ----------------------------------------------
        # OVERALL COVERAGE
        #
        # Different evidence groups receive different
        # importance.
        #
        # Missing PEG, for example, should not carry
        # the same importance as having no growth data.
        # ----------------------------------------------

        if profile in {
            "BANK",
            "FINANCIAL_SERVICES",
        }:

            # Industrial liquidity and cash-flow fields
            # are less appropriate for financial firms.
            #
            # This remains provisional until specialized
            # financial-sector data models are built.

            coverage_score = round(

                (
                    profitability[
                        "coverage"
                    ]
                    * 0.40

                    + growth[
                        "coverage"
                    ]
                    * 0.30

                    + valuation[
                        "coverage"
                    ]
                    * 0.30
                ),

                1,
            )

        else:

            coverage_score = round(

                (
                    profitability[
                        "coverage"
                    ]
                    * 0.30

                    + growth[
                        "coverage"
                    ]
                    * 0.25

                    + balance_sheet[
                        "coverage"
                    ]
                    * 0.20

                    + cash_flow[
                        "coverage"
                    ]
                    * 0.15

                    + valuation[
                        "coverage"
                    ]
                    * 0.10
                ),

                1,
            )

        # ----------------------------------------------
        # EVIDENCE GATES
        #
        # These gates check whether enough independent
        # evidence exists to calculate a meaningful
        # investment-quality assessment.
        # ----------------------------------------------

        blocking_reasons = []

        # Profitability:
        # At least two independent profitability
        # indicators should be available.

        if (
            profitability[
                "available_count"
            ]
            < 2
        ):

            blocking_reasons.append(
                "Insufficient profitability evidence"
            )

        # Growth:
        # At least one growth indicator required.

        if (
            growth[
                "available_count"
            ]
            < 1
        ):

            blocking_reasons.append(
                "Insufficient growth evidence"
            )

        # Valuation:
        # At least one valuation measure required.

        if (
            valuation[
                "available_count"
            ]
            < 1
        ):

            blocking_reasons.append(
                "Insufficient valuation evidence"
            )

        # General companies require some
        # balance-sheet evidence.

        if profile not in {
            "BANK",
            "FINANCIAL_SERVICES",
        }:

            if (
                balance_sheet[
                    "available_count"
                ]
                < 2
            ):

                blocking_reasons.append(
                    "Insufficient balance-sheet evidence"
                )

        # ----------------------------------------------
        # CASH FLOW HANDLING
        #
        # Missing cash flow is flagged, but does not
        # automatically reject an otherwise sufficiently
        # covered company.
        #
        # This is important for cases where a data vendor
        # temporarily omits cash-flow fields.
        # ----------------------------------------------

        warnings = []

        if (
            cash_flow[
                "available_count"
            ]
            == 0
            and profile not in {
                "BANK",
                "FINANCIAL_SERVICES",
            }
        ):

            warnings.append(
                "Cash-flow data unavailable"
            )

        # ----------------------------------------------
        # COVERAGE LEVEL
        # ----------------------------------------------

        if coverage_score >= 90:

            coverage_level = (
                "EXCELLENT"
            )

        elif coverage_score >= 75:

            coverage_level = (
                "HIGH"
            )

        elif coverage_score >= 60:

            coverage_level = (
                "MODERATE"
            )

        else:

            coverage_level = (
                "LOW"
            )

        # ----------------------------------------------
        # RANKING DATA READINESS
        #
        # This means:
        # enough data exists for scoring consideration.
        #
        # It does NOT mean the stock automatically passes
        # fundamental, technical or portfolio gates.
        # ----------------------------------------------

        ranking_data_ready = (

            len(
                blocking_reasons
            )
            == 0

            and coverage_score
            >= 60
        )

        return {

            "profile":
                profile,

            "coverage_score":
                coverage_score,

            "coverage_level":
                coverage_level,

            "ranking_data_ready":
                ranking_data_ready,

            "blocking_reasons":
                blocking_reasons,

            "warnings":
                warnings,

            "metric_status":
                metric_status,

            "groups":
                groups,
        }


def analyze_data_completeness(
    data,
    profile="GENERAL",
):

    service = (
        DataCompletenessService()
    )

    return service.analyze(
        data,
        profile,
    )