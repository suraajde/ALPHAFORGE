class DataQualityService:

    CORE_METRICS = [
        "roe",
        "roa",
        "roce",
        "operating_margin",
        "profit_margin",
        "revenue_growth",
        "earnings_growth",
        "debt_equity",
        "current_ratio",
        "pe",
        "pb",
        "free_cash_flow",
        "operating_cash_flow",
    ]

    OPTIONAL_METRICS = [
        "quick_ratio",
        "forward_pe",
        "peg",
        "total_cash",
        "total_debt",
    ]

    def calculate(self, data):

        if not data or "error" in data:

            return {
                "confidence_score": 0.0,
                "confidence_level": "LOW",
                "core_available": 0,
                "core_total": len(
                    self.CORE_METRICS
                ),
                "optional_available": 0,
                "optional_total": len(
                    self.OPTIONAL_METRICS
                ),
                "missing_core": list(
                    self.CORE_METRICS
                ),
                "eligible_for_ranking": False,
            }

        core_available = sum(
            1
            for metric in self.CORE_METRICS
            if data.get(metric) is not None
        )

        optional_available = sum(
            1
            for metric in self.OPTIONAL_METRICS
            if data.get(metric) is not None
        )

        core_coverage = (
            core_available
            / len(self.CORE_METRICS)
        )

        optional_coverage = (
            optional_available
            / len(self.OPTIONAL_METRICS)
        )

        # Core metrics matter much more than
        # optional supporting metrics.

        confidence_score = (
            core_coverage * 85
            + optional_coverage * 15
        )

        confidence_score = round(
            confidence_score,
            1,
        )

        missing_core = [
            metric
            for metric in self.CORE_METRICS
            if data.get(metric) is None
        ]

        if confidence_score >= 90:

            confidence_level = "HIGH"

        elif confidence_score >= 75:

            confidence_level = "GOOD"

        elif confidence_score >= 60:

            confidence_level = "MODERATE"

        else:

            confidence_level = "LOW"

        # Ranking eligibility is deliberately
        # stricter than merely calculating a score.
        #
        # A stock should have at least 80% of its
        # core fundamental dataset available before
        # entering the future 30-stock ranking engine.

        eligible_for_ranking = (
            core_coverage >= 0.80
            and confidence_score >= 75
        )

        return {
            "confidence_score":
                confidence_score,

            "confidence_level":
                confidence_level,

            "core_available":
                core_available,

            "core_total":
                len(
                    self.CORE_METRICS
                ),

            "optional_available":
                optional_available,

            "optional_total":
                len(
                    self.OPTIONAL_METRICS
                ),

            "missing_core":
                missing_core,

            "eligible_for_ranking":
                eligible_for_ranking,
        }


def calculate_data_quality(data):

    service = DataQualityService()

    return service.calculate(
        data
    )