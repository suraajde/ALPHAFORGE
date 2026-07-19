import json
import os
import tempfile

from datetime import (
    datetime,
    timezone,
    timedelta,
)


class ScanCacheService:

    """
    AlphaForge Scan Cache Service

    Purpose:
    Store completed stock-analysis results locally so
    repeated Research Radar scans do not need to fetch
    and recalculate every stock unnecessarily.

    Features:
    - Per-symbol JSON cache
    - Timestamp tracking
    - Freshness / expiry checking
    - Safe atomic file replacement
    - Corrupted-cache handling
    - Force-refresh support
    - Automatic cache-folder creation

    IMPORTANT:
    This service does not decide investment eligibility.
    It only stores and retrieves analysis results.
    """

    DEFAULT_CACHE_HOURS = 12

    def __init__(
        self,
        cache_dir=None,
        cache_hours=None,
    ):

        # --------------------------------------------------
        # PROJECT ROOT
        #
        # services/scan_cache_service.py
        #        ↓
        # ALPHAFORGE/
        # --------------------------------------------------

        project_root = os.path.dirname(
            os.path.dirname(
                os.path.abspath(
                    __file__
                )
            )
        )

        if cache_dir is None:

            cache_dir = os.path.join(
                project_root,
                "data",
                "cache",
                "research_radar",
            )

        self.cache_dir = os.path.abspath(
            cache_dir
        )

        if cache_hours is None:

            cache_hours = (
                self.DEFAULT_CACHE_HOURS
            )

        self.cache_hours = float(
            cache_hours
        )

        # --------------------------------------------------
        # CREATE CACHE DIRECTORY
        # --------------------------------------------------

        os.makedirs(
            self.cache_dir,
            exist_ok=True,
        )

    # --------------------------------------------------
    # SYMBOL CLEANER
    # --------------------------------------------------

    def _clean_symbol(
        self,
        symbol,
    ):

        symbol = str(
            symbol
            or ""
        ).strip().upper()

        # Prevent path characters from entering filenames.

        safe_symbol = "".join(

            character

            for character in symbol

            if (
                character.isalnum()
                or character
                in {
                    "-",
                    "_",
                }
            )
        )

        return safe_symbol

    # --------------------------------------------------
    # CACHE FILE PATH
    # --------------------------------------------------

    def get_cache_path(
        self,
        symbol,
    ):

        safe_symbol = (
            self._clean_symbol(
                symbol
            )
        )

        if not safe_symbol:

            return None

        return os.path.join(
            self.cache_dir,
            f"{safe_symbol}.json",
        )

    # --------------------------------------------------
    # CURRENT UTC TIME
    # --------------------------------------------------

    def _utc_now(self):

        return datetime.now(
            timezone.utc
        )

    # --------------------------------------------------
    # TIMESTAMP PARSER
    # --------------------------------------------------

    def _parse_timestamp(
        self,
        timestamp,
    ):

        if not timestamp:

            return None

        try:

            parsed = (
                datetime.fromisoformat(
                    str(
                        timestamp
                    )
                )
            )

            # Older timestamp formats may not contain
            # timezone information.

            if parsed.tzinfo is None:

                parsed = parsed.replace(
                    tzinfo=timezone.utc
                )

            return parsed.astimezone(
                timezone.utc
            )

        except (
            TypeError,
            ValueError,
        ):

            return None

    # --------------------------------------------------
    # READ RAW CACHE FILE
    # --------------------------------------------------

    def _read_cache_file(
        self,
        symbol,
    ):

        cache_path = (
            self.get_cache_path(
                symbol
            )
        )

        if (
            not cache_path
            or not os.path.exists(
                cache_path
            )
        ):

            return {
                "status":
                    "MISS",

                "reason":
                    "Cache file not found",

                "payload":
                    None,
            }

        try:

            with open(
                cache_path,
                "r",
                encoding="utf-8",
            ) as file:

                payload = json.load(
                    file
                )

        except (
            json.JSONDecodeError,
            OSError,
            UnicodeDecodeError,
        ) as error:

            return {
                "status":
                    "CORRUPT",

                "reason":
                    str(
                        error
                    ),

                "payload":
                    None,
            }

        if not isinstance(
            payload,
            dict,
        ):

            return {
                "status":
                    "CORRUPT",

                "reason":
                    "Cache payload is not a dictionary",

                "payload":
                    None,
            }

        return {
            "status":
                "FOUND",

            "reason":
                None,

            "payload":
                payload,
        }

    # --------------------------------------------------
    # CHECK FRESHNESS
    # --------------------------------------------------

    def is_fresh(
        self,
        payload,
    ):

        if not isinstance(
            payload,
            dict,
        ):

            return False

        cached_at = (
            self._parse_timestamp(
                payload.get(
                    "cached_at"
                )
            )
        )

        if cached_at is None:

            return False

        expiry_time = (

            cached_at

            + timedelta(
                hours=self.cache_hours
            )
        )

        return (
            self._utc_now()
            <= expiry_time
        )

    # --------------------------------------------------
    # GET CACHE STATUS
    # --------------------------------------------------

    def get_status(
        self,
        symbol,
    ):

        raw = (
            self._read_cache_file(
                symbol
            )
        )

        if raw[
            "status"
        ] != "FOUND":

            return {
                "symbol":
                    self._clean_symbol(
                        symbol
                    ),

                "cache_status":
                    raw[
                        "status"
                    ],

                "fresh":
                    False,

                "cached_at":
                    None,

                "reason":
                    raw[
                        "reason"
                    ],
            }

        payload = raw[
            "payload"
        ]

        fresh = (
            self.is_fresh(
                payload
            )
        )

        return {
            "symbol":
                self._clean_symbol(
                    symbol
                ),

            "cache_status":
                (
                    "FRESH"
                    if fresh
                    else "EXPIRED"
                ),

            "fresh":
                fresh,

            "cached_at":
                payload.get(
                    "cached_at"
                ),

            "reason":
                None,
        }

    # --------------------------------------------------
    # LOAD CACHED ANALYSIS
    # --------------------------------------------------

    def load(
        self,
        symbol,
        force_refresh=False,
    ):

        clean_symbol = (
            self._clean_symbol(
                symbol
            )
        )

        if not clean_symbol:

            return {
                "cache_hit":
                    False,

                "cache_status":
                    "INVALID_SYMBOL",

                "analysis":
                    None,

                "cached_at":
                    None,
            }

        # --------------------------------------------------
        # FORCE REFRESH
        #
        # Caller explicitly requests fresh analysis.
        # Existing cache is ignored but not deleted.
        # --------------------------------------------------

        if force_refresh:

            return {
                "cache_hit":
                    False,

                "cache_status":
                    "FORCE_REFRESH",

                "analysis":
                    None,

                "cached_at":
                    None,
            }

        raw = (
            self._read_cache_file(
                clean_symbol
            )
        )

        if raw[
            "status"
        ] != "FOUND":

            return {
                "cache_hit":
                    False,

                "cache_status":
                    raw[
                        "status"
                    ],

                "analysis":
                    None,

                "cached_at":
                    None,
            }

        payload = raw[
            "payload"
        ]

        if not self.is_fresh(
            payload
        ):

            return {
                "cache_hit":
                    False,

                "cache_status":
                    "EXPIRED",

                "analysis":
                    None,

                "cached_at":
                    payload.get(
                        "cached_at"
                    ),
            }

        analysis = payload.get(
            "analysis"
        )

        # --------------------------------------------------
        # CACHE VALIDATION
        #
        # Only successful analysis results are treated
        # as valid cache hits.
        # --------------------------------------------------

        if (
            not isinstance(
                analysis,
                dict,
            )
            or analysis.get(
                "status"
            ) != "OK"
        ):

            return {
                "cache_hit":
                    False,

                "cache_status":
                    "INVALID",

                "analysis":
                    None,

                "cached_at":
                    payload.get(
                        "cached_at"
                    ),
            }

        return {
            "cache_hit":
                True,

            "cache_status":
                "FRESH",

            "analysis":
                analysis,

            "cached_at":
                payload.get(
                    "cached_at"
                ),
        }

    # --------------------------------------------------
    # SAVE ANALYSIS
    # --------------------------------------------------

    def save(
        self,
        symbol,
        analysis,
    ):

        clean_symbol = (
            self._clean_symbol(
                symbol
            )
        )

        if not clean_symbol:

            return {
                "saved":
                    False,

                "reason":
                    "Invalid symbol",
            }

        # --------------------------------------------------
        # DO NOT CACHE FAILED ANALYSES
        # --------------------------------------------------

        if (
            not isinstance(
                analysis,
                dict,
            )
            or analysis.get(
                "status"
            ) != "OK"
        ):

            return {
                "saved":
                    False,

                "reason":
                    "Only successful analysis can be cached",
            }

        cache_path = (
            self.get_cache_path(
                clean_symbol
            )
        )

        payload = {

            "cache_version":
                1,

            "symbol":
                clean_symbol,

            "cached_at":
                self._utc_now().isoformat(),

            "analysis":
                analysis,
        }

        temp_path = None

        try:

            # --------------------------------------------------
            # SAFE WRITE
            #
            # Write to a temporary file first.
            # Replace the real cache only after JSON writing
            # succeeds completely.
            # --------------------------------------------------

            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                suffix=".tmp",
                prefix=(
                    f"{clean_symbol}_"
                ),
                dir=self.cache_dir,
                delete=False,
            ) as temp_file:

                temp_path = (
                    temp_file.name
                )

                json.dump(
                    payload,
                    temp_file,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )

                temp_file.flush()

                os.fsync(
                    temp_file.fileno()
                )

            os.replace(
                temp_path,
                cache_path,
            )

            return {
                "saved":
                    True,

                "reason":
                    None,

                "cache_path":
                    cache_path,

                "cached_at":
                    payload[
                        "cached_at"
                    ],
            }

        except (
            OSError,
            TypeError,
            ValueError,
        ) as error:

            # Remove abandoned temporary file.

            if (
                temp_path
                and os.path.exists(
                    temp_path
                )
            ):

                try:

                    os.remove(
                        temp_path
                    )

                except OSError:

                    pass

            return {
                "saved":
                    False,

                "reason":
                    str(
                        error
                    ),
            }

    # --------------------------------------------------
    # DELETE ONE SYMBOL CACHE
    # --------------------------------------------------

    def delete(
        self,
        symbol,
    ):

        cache_path = (
            self.get_cache_path(
                symbol
            )
        )

        if (
            not cache_path
            or not os.path.exists(
                cache_path
            )
        ):

            return False

        try:

            os.remove(
                cache_path
            )

            return True

        except OSError:

            return False

    # --------------------------------------------------
    # CLEAR ALL CACHE FILES
    # --------------------------------------------------

    def clear_all(self):

        deleted = 0

        failed = 0

        try:

            filenames = os.listdir(
                self.cache_dir
            )

        except OSError:

            return {
                "deleted":
                    0,

                "failed":
                    0,
            }

        for filename in filenames:

            if not filename.lower().endswith(
                ".json"
            ):

                continue

            path = os.path.join(
                self.cache_dir,
                filename,
            )

            try:

                os.remove(
                    path
                )

                deleted += 1

            except OSError:

                failed += 1

        return {
            "deleted":
                deleted,

            "failed":
                failed,
        }


# --------------------------------------------------
# DEFAULT SERVICE
# --------------------------------------------------

_default_cache_service = (
    ScanCacheService()
)


# --------------------------------------------------
# CONVENIENCE FUNCTIONS
# --------------------------------------------------

def load_cached_analysis(
    symbol,
    force_refresh=False,
):

    return (
        _default_cache_service.load(
            symbol,
            force_refresh=force_refresh,
        )
    )


def save_cached_analysis(
    symbol,
    analysis,
):

    return (
        _default_cache_service.save(
            symbol,
            analysis,
        )
    )


def get_cache_status(
    symbol,
):

    return (
        _default_cache_service.get_status(
            symbol
        )
    )


def delete_cached_analysis(
    symbol,
):

    return (
        _default_cache_service.delete(
            symbol
        )
    )


def clear_scan_cache():

    return (
        _default_cache_service.clear_all()
    )