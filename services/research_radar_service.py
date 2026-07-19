from services.stock_service import (
    get_stock_data,
)

from services.fundamental_service import (
    get_fundamental_metrics,
)

from services.sector_classifier_service import (
    classify_sector,
)

from services.sector_fundamental_score_service import (
    calculate_sector_aware_fundamental_score,
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
            str(symbol)
            .strip()
            .upper()
        )

        result = {
            "symbol": symbol,
        }

        try:

            # ----------------------------------
            # Company Metadata
            # ----------------------------------

            stock_data = get_stock_data(
                symbol
            )

            if (
                not stock_data
                or "error" in stock_data
            ):

                result.update({
                    "status": "ERROR",
                    "error":
                        "Company data unavailable",
                })

                return result

            company_name = stock_data.get(
                "name"
            )

            sector = stock_data.get(
                "sector"
            )

            industry = stock_data.get(
                "industry"
            )

            # ----------------------------------
            # Sector Classification
            # ----------------------------------

            classification = classify_sector(
                sector=sector,
                industry=industry,
                company_name=company_name,
            )

            scoring_profile = (
                classification.get(
                    "profile",
                    "GENERAL",
                )
            )

            # ----------------------------------
            # Fundamental Data
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

            # ----------------------------------
            # Sector-Aware Fundamental Score
            # ----------------------------------

            fundamental_scores = (
                calculate_sector_aware_fundamental_score(
                    fundamental_data,
                    scoring_profile,
                )
            )

            profile_maturity = (
                fundamental_scores.get(
                    "profile_maturity",
                    "BASELINE",
                )
            )

            # ----------------------------------
            # Data Quality
            # ----------------------------------

            data_quality = (
                calculate_data_quality(
                    fundamental_data
                )
            )

            # ----------------------------------
            # Technical Data
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

            # ----------------------------------
            # Production Ranking Eligibility
            #
            # Provisional sector profiles may be
            # analyzed and displayed, but must not
            # automatically enter the future
            # production Top-30/Top-12 pool.
            # ----------------------------------

            hard_gate_pass = bool(
                alpha.get(
                    "hard_gate_pass"
                )
            )

            production_eligible = (
                hard_gate_pass
                and profile_maturity
                != "PROVISIONAL"
            )

            ranking_notes = []

            if not hard_gate_pass:

                ranking_notes.extend(
                    alpha.get(
                        "gate_reasons",
                        [],
                    )
                )

            if (
                profile_maturity
                == "PROVISIONAL"
            ):

                ranking_notes.append(
                    "Sector scoring profile is provisional"
                )

            # ----------------------------------
            # Final Result
            # ----------------------------------

            result.update({

                "status":
                    "OK",

                "company_name":
                    company_name,

                "sector":
                    sector,

                "industry":
                    industry,

                "scoring_profile":
                    scoring_profile,

                "profile_maturity":
                    profile_maturity,

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
                    hard_gate_pass,

                "production_eligible":
                    production_eligible,

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

                "ranking_notes":
                    ranking_notes,
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
        # Successful Analyses
        # ----------------------------------

        successful = [
            item
            for item in results
            if item.get(
                "status"
            ) == "OK"
        ]

        # ----------------------------------
        # Production-Eligible Pool
        # ----------------------------------

        eligible = [
            item
            for item in successful
            if item.get(
                "production_eligible"
            )
        ]

        # ----------------------------------
        # Review Pool
        #
        # Includes provisional sector profiles
        # and stocks failing hard gates.
        # ----------------------------------

        review = [
            item
            for item in successful
            if not item.get(
                "production_eligible"
            )
        ]

        # ----------------------------------
        # Ranking Function
        # ----------------------------------

        def ranking_key(item):

            return (
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
            )

        eligible.sort(
            key=ranking_key,
            reverse=True,
        )

        review.sort(
            key=ranking_key,
            reverse=True,
        )

        ranked = eligible[
            :limit
        ]

        for index, item in enumerate(
            ranked,
            start=1,
        ):

            item["rank"] = index

        errors = [
            item
            for item in results
            if item.get(
                "status"
            ) != "OK"
        ]

        return {

            "ranked":
                ranked,

            "review":
                review,

            "errors":
                errors,

            "analyzed_count":
                len(results),

            "successful_count":
                len(successful),

            "eligible_count":
                len(eligible),

            "review_count":
                len(review),
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