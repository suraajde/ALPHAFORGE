from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from services.research_radar_service import ResearchRadarService
from services.scan_cache_service import ScanCacheService


class ProductionScanOrchestrator:
    """
    AlphaForge Production Deep-Scan Orchestrator.

    Responsibilities:
    - Inspect existing Research Radar cache.
    - Process candidate symbols in controlled batches.
    - Preserve checkpoint/progress state.
    - Resume interrupted scans.
    - Reuse the existing ResearchRadarService and ScanCacheService.
    - Produce one correct GLOBAL Top-N ranking.

    This service does not duplicate fundamental, technical,
    composite, eligibility, or cache logic.
    """

    def __init__(
        self,
        checkpoint_file=None,
        batch_size=10,
    ):

        project_root = (
            Path(__file__).resolve().parent.parent
        )

        if checkpoint_file is None:

            checkpoint_file = (
                project_root
                / "data"
                / "cache"
                / "production_scan_checkpoint.json"
            )

        self.checkpoint_file = Path(
            checkpoint_file
        )

        self.checkpoint_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.batch_size = max(
            1,
            int(batch_size),
        )

        self.cache_service = (
            ScanCacheService()
        )

        self.radar_service = (
            ResearchRadarService()
        )

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _utc_now():

        return (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

    @staticmethod
    def _clean_symbols(
        symbols,
    ):

        cleaned = []
        seen = set()

        for symbol in symbols:

            symbol = str(
                symbol
            ).strip().upper()

            if not symbol:

                continue

            if symbol in seen:

                continue

            seen.add(
                symbol
            )

            cleaned.append(
                symbol
            )

        return cleaned

    # ======================================================
    # CACHE INSPECTION
    # ======================================================

    def inspect_cache(
        self,
        symbols,
    ):

        symbols = self._clean_symbols(
            symbols
        )

        fresh = []
        expired = []
        missing = []

        details = []

        for symbol in symbols:

            status = (
                self.cache_service.get_status(
                    symbol
                )
            )

            details.append(
                status
            )

            cache_status = status.get(
                "cache_status"
            )

            if cache_status == "FRESH":

                fresh.append(
                    symbol
                )

            elif cache_status == "EXPIRED":

                expired.append(
                    symbol
                )

            else:

                missing.append(
                    symbol
                )

        return {

            "total":
                len(symbols),

            "fresh_count":
                len(fresh),

            "expired_count":
                len(expired),

            "missing_count":
                len(missing),

            "fresh":
                fresh,

            "expired":
                expired,

            "missing":
                missing,

            "details":
                details,

        }

    # ======================================================
    # CHECKPOINT
    # ======================================================

    def save_checkpoint(
        self,
        state,
    ):

        payload = dict(
            state
        )

        payload[
            "updated_at"
        ] = self._utc_now()

        temporary_file = (
            self.checkpoint_file.with_suffix(
                ".tmp"
            )
        )

        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as handle:

            json.dump(
                payload,
                handle,
                indent=2,
            )

        temporary_file.replace(
            self.checkpoint_file
        )

    def load_checkpoint(
        self,
    ):

        if not self.checkpoint_file.exists():

            return None

        try:

            with self.checkpoint_file.open(
                "r",
                encoding="utf-8",
            ) as handle:

                payload = json.load(
                    handle
                )

            if not isinstance(
                payload,
                dict,
            ):

                return None

            return payload

        except Exception:

            return None

    def clear_checkpoint(
        self,
    ):

        if self.checkpoint_file.exists():

            self.checkpoint_file.unlink()

    # ======================================================
    # GLOBAL RANKING
    # ======================================================

    @staticmethod
    def _ranking_key(
        item,
    ):

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

    def _build_final_result(
        self,
        analyses,
        limit=30,
    ):

        successful = [

            item

            for item in analyses

            if (
                isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "status"
                ) == "OK"
            )

        ]

        eligible = [

            item

            for item in successful

            if item.get(
                "production_eligible"
            )

        ]

        review = [

            item

            for item in successful

            if not item.get(
                "production_eligible"
            )

        ]

        errors = [

            item

            for item in analyses

            if (
                not isinstance(
                    item,
                    dict,
                )
                or item.get(
                    "status"
                ) != "OK"
            )

        ]

        eligible.sort(
            key=self._ranking_key,
            reverse=True,
        )

        review.sort(
            key=self._ranking_key,
            reverse=True,
        )

        ranked = eligible[
            :limit
        ]

        for index, item in enumerate(
            ranked,
            start=1,
        ):

            item[
                "rank"
            ] = index

        return {

            "ranked":
                ranked,

            "review":
                review,

            "errors":
                errors,

            "successful_count":
                len(successful),

            "eligible_count":
                len(eligible),

            "review_count":
                len(review),

            "error_count":
                len(errors),

        }

    # ======================================================
    # RUN DEEP SCAN
    # ======================================================

    def run(
        self,
        symbols,
        limit=30,
        force_refresh=False,
        resume=True,
        progress_callback=None,
    ):

        symbols = self._clean_symbols(
            symbols
        )

        # --------------------------------------------------
        # RESUME STATE
        # --------------------------------------------------

        completed_symbols = []
        analyses = []

        if resume:

            checkpoint = (
                self.load_checkpoint()
            )

            if checkpoint:

                checkpoint_symbols = (
                    checkpoint.get(
                        "requested_symbols",
                        [],
                    )
                )

                if (
                    checkpoint_symbols
                    == symbols
                ):

                    completed_symbols = (
                        checkpoint.get(
                            "completed_symbols",
                            [],
                        )
                    )

        completed_set = set(
            completed_symbols
        )

        # --------------------------------------------------
        # IMPORTANT:
        # Completed analyses are reloaded through the normal
        # Radar cache path. We do not duplicate cached payloads
        # inside the checkpoint.
        # --------------------------------------------------

        if completed_symbols:

            completed_result = (
                self.radar_service.rank_symbols(

                    completed_symbols,

                    limit=len(
                        completed_symbols
                    ),

                    force_refresh=False,

                )
            )

            analyses.extend(
                completed_result.get(
                    "ranked",
                    []
                )
            )

            analyses.extend(
                completed_result.get(
                    "review",
                    []
                )
            )

            analyses.extend(
                completed_result.get(
                    "errors",
                    []
                )
            )

        remaining = [

            symbol

            for symbol in symbols

            if symbol not in completed_set

        ]

        total = len(
            symbols
        )

        # --------------------------------------------------
        # PROCESS CONTROLLED BATCHES
        # --------------------------------------------------

        for start in range(
            0,
            len(remaining),
            self.batch_size,
        ):

            batch = remaining[
                start:
                start + self.batch_size
            ]

            batch_result = (
                self.radar_service.rank_symbols(

                    batch,

                    limit=len(
                        batch
                    ),

                    force_refresh=
                        force_refresh,

                )
            )

            batch_analyses = []

            batch_analyses.extend(
                batch_result.get(
                    "ranked",
                    []
                )
            )

            batch_analyses.extend(
                batch_result.get(
                    "review",
                    []
                )
            )

            batch_analyses.extend(
                batch_result.get(
                    "errors",
                    []
                )
            )

            analyses.extend(
                batch_analyses
            )

            completed_symbols.extend(
                batch
            )

            completed_set.update(
                batch
            )

            # ----------------------------------------------
            # SAVE CHECKPOINT AFTER EVERY BATCH
            # ----------------------------------------------

            state = {

                "requested_symbols":
                    symbols,

                "completed_symbols":
                    completed_symbols,

                "processed_count":
                    len(
                        completed_symbols
                    ),

                "remaining_count":
                    total
                    - len(
                        completed_symbols
                    ),

                "total_count":
                    total,

                "force_refresh":
                    force_refresh,

            }

            self.save_checkpoint(
                state
            )

            if progress_callback:

                progress_callback(
                    state
                )

        # --------------------------------------------------
        # FINAL GLOBAL RANK
        # --------------------------------------------------

        final_result = (
            self._build_final_result(

                analyses,

                limit=limit,

            )
        )

        final_result.update({

            "requested_count":
                total,

            "processed_count":
                len(
                    completed_symbols
                ),

            "remaining_count":
                0,

            "force_refresh":
                force_refresh,

            "completed":
                True,

        })

        # Successful completed scan no longer needs
        # an active resume checkpoint.

        self.clear_checkpoint()

        return final_result