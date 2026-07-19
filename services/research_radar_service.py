from services.fundamental_service import (
    get_fundamental_metrics,
)

from services.fundamental_score_service import (
    calculate_fundamental_score,
)

from services.data_quality_service import (
    calculate_data_quality,
)

from services.technical_service import (
    get_technical_metrics,
)

from services.technical_score_service import (
    calculate_technical_score,
)

from services.alpha_composite_service import (
    calculate_alpha_composite,
)


class ResearchRadarService:

    def analyze_stock(self, symbol):

        symbol = (
            symbol
            .strip()
            .upper()
        )

        result = {
            "symbol": symbol,
        }

        try:

            # ----------------------------------
            # Fundamental Layer
            # ----------------------------------

            fundamental_data = (
                get_fundamental_metrics(
                    symbol
                )
            )

            if (
                not fundamental_data
                or "error" in fundamental_data
            ):

                result.update({
                    "status": "ERROR",
                    "error":
                        "Fundamental data unavailable",
                })

                return result

            fundamental_scores = (
                calculate_fundamental_score(
                    fundamental_data
                )
            )

            # ----------------------------------
            # Data Quality Layer
            # ----------------------------------

            data_quality = (
                calculate_data_quality(
                    fundamental_data
                )
            )

            # ----------------------------------
            # Technical Layer
            # ----------------------------------

            technical_data = (
                get_technical_metrics(
                    symbol
                )
            )

            if (
                not technical_data
                or "error" in technical_data
            ):

                result.update({
                    "status": "ERROR",
                    "error":
                        "Technical data unavailable",
                })

                return result

            technical_scores = (
                calculate_technical_score(
                    technical_data
                )
            )

            # ----------------------------------
            # Alpha Composite Prototype
            # ----------------------------------

            alpha = (
                calculate_alpha_composite(
                    fundamental_scores,
                    technical_scores,
                    data_quality,
                )
            )

            result.update({

                "status":
                    "OK",

                "fundamental_score":
                    alpha.get(
                        "fundamental_score"
                    ),

                "technical_score":
                    alpha.get(
                        "technical_score"
                    ),

                "composite_score":
                    alpha.get(
                        "base_composite"
                    ),

                "readiness_score":
                    alpha.get(
                        "readiness_score"
                    ),

                "data_confidence":
                    alpha.get(
                        "data_confidence"
                    ),

                "hard_gate_pass":
                    alpha.get(
                        "hard_gate_pass"
                    ),

                "classification":
                    alpha.get(
                        "classification"
                    ),

                "gate_reasons":
                    alpha.get(
                        "gate_reasons",
                        [],
                    ),

                "technical_warnings":
                    alpha.get(
                        "technical_warnings",
                        [],
                    ),
            })

            return result

        except Exception as error:

            result.update({
                "status": "ERROR",
                "error": str(error),
            })

            return result

    def rank_symbols(
        self,
        symbols,
        limit=30,
    ):

        results = []

        seen = set()

        for symbol in symbols:

            clean_symbol = (
                str(symbol)
                .strip()
                .upper()
            )

            if not clean_symbol:
                continue

            if clean_symbol in seen:
                continue

            seen.add(
                clean_symbol
            )

            print(
                f"Analyzing {clean_symbol}..."
            )

            analysis = (
                self.analyze_stock(
                    clean_symbol
                )
            )

            results.append(
                analysis
            )

        # ----------------------------------
        # Keep successful analyses
        # ----------------------------------

        successful = [
            item
            for item in results
            if item.get("status") == "OK"
        ]

        # ----------------------------------
        # Ranking Logic
        #
        # 1. Hard-gate pass first
        # 2. Composite score
        # 3. Readiness score
        # 4. Fundamental score
        # ----------------------------------

        successful.sort(
            key=lambda item: (
                bool(
                    item.get(
                        "hard_gate_pass"
                    )
                ),
                item.get(
                    "composite_score"
                )
                if item.get(
                    "composite_score"
                ) is not None
                else -1,
                item.get(
                    "readiness_score"
                )
                if item.get(
                    "readiness_score"
                ) is not None
                else -1,
                item.get(
                    "fundamental_score"
                )
                if item.get(
                    "fundamental_score"
                ) is not None
                else -1,
            ),
            reverse=True,
        )

        ranked = (
            successful[:limit]
        )

        for index, item in enumerate(
            ranked,
            start=1,
        ):

            item["rank"] = index

        errors = [
            item
            for item in results
            if item.get("status") != "OK"
        ]

        return {
            "ranked": ranked,
            "errors": errors,
            "analyzed_count":
                len(results),
            "successful_count":
                len(successful),
        }


def build_research_radar(
    symbols,
    limit=30,
):

    service = (
        ResearchRadarService()
    )

    return service.rank_symbols(
        symbols,
        limit,
    )