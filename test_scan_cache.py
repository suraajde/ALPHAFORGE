from services.scan_cache_service import (
    ScanCacheService,
)


# --------------------------------------------------
# CREATE ISOLATED TEST CACHE
#
# Use a short test-specific cache folder so this test
# does not interfere with future production scan cache.
# --------------------------------------------------

cache = ScanCacheService(
    cache_dir="data/cache/test_research_radar",
    cache_hours=12,
)

symbol = "TESTSTOCK"


print()
print("=" * 80)
print("ALPHAFORGE SCAN CACHE TEST")
print("=" * 80)


# --------------------------------------------------
# CLEAN OLD TEST CACHE
# --------------------------------------------------

print()
print("STEP 1 - CLEAR OLD TEST CACHE")
print("-" * 80)

clear_result = cache.clear_all()

print(
    "Deleted:",
    clear_result.get(
        "deleted"
    ),
)

print(
    "Failed :",
    clear_result.get(
        "failed"
    ),
)


# --------------------------------------------------
# TEST 1
# EXPECTED: MISS
# --------------------------------------------------

print()
print("STEP 2 - INITIAL CACHE LOOKUP")
print("-" * 80)

initial = cache.load(
    symbol
)

print(
    "Cache Hit    :",
    initial.get(
        "cache_hit"
    ),
)

print(
    "Cache Status :",
    initial.get(
        "cache_status"
    ),
)

assert (
    initial.get(
        "cache_hit"
    )
    is False
)

assert (
    initial.get(
        "cache_status"
    )
    == "MISS"
)

print(
    "RESULT       : PASS"
)


# --------------------------------------------------
# CREATE FAKE SUCCESSFUL ANALYSIS
#
# We deliberately use fake data here.
# This test checks cache mechanics only.
# No Yahoo/API calls are required.
# --------------------------------------------------

fake_analysis = {

    "status":
        "OK",

    "symbol":
        symbol,

    "company_name":
        "AlphaForge Test Company",

    "scoring_profile":
        "GENERAL",

    "profile_maturity":
        "BASELINE",

    "fundamental_score":
        80.0,

    "technical_score":
        70.0,

    "composite_score":
        76.0,

    "readiness_score":
        72.0,

    "data_status":
        "CLEAN",

    "production_eligible":
        True,

    "classification":
        "STRONG RADAR CANDIDATE",
}


# --------------------------------------------------
# TEST 2
# EXPECTED: SUCCESSFUL SAVE
# --------------------------------------------------

print()
print("STEP 3 - SAVE SUCCESSFUL ANALYSIS")
print("-" * 80)

save_result = cache.save(
    symbol,
    fake_analysis,
)

print(
    "Saved        :",
    save_result.get(
        "saved"
    ),
)

print(
    "Reason       :",
    save_result.get(
        "reason"
    ),
)

print(
    "Cached At    :",
    save_result.get(
        "cached_at"
    ),
)

assert (
    save_result.get(
        "saved"
    )
    is True
)

print(
    "RESULT       : PASS"
)


# --------------------------------------------------
# TEST 3
# EXPECTED: FRESH CACHE HIT
# --------------------------------------------------

print()
print("STEP 4 - LOAD FRESH CACHE")
print("-" * 80)

fresh = cache.load(
    symbol
)

print(
    "Cache Hit    :",
    fresh.get(
        "cache_hit"
    ),
)

print(
    "Cache Status :",
    fresh.get(
        "cache_status"
    ),
)

print(
    "Cached At    :",
    fresh.get(
        "cached_at"
    ),
)

loaded_analysis = fresh.get(
    "analysis"
)

print(
    "Loaded Symbol:",
    (
        loaded_analysis.get(
            "symbol"
        )
        if loaded_analysis
        else None
    ),
)

print(
    "Composite    :",
    (
        loaded_analysis.get(
            "composite_score"
        )
        if loaded_analysis
        else None
    ),
)

assert (
    fresh.get(
        "cache_hit"
    )
    is True
)

assert (
    fresh.get(
        "cache_status"
    )
    == "FRESH"
)

assert (
    loaded_analysis.get(
        "symbol"
    )
    == symbol
)

assert (
    loaded_analysis.get(
        "composite_score"
    )
    == 76.0
)

print(
    "RESULT       : PASS"
)


# --------------------------------------------------
# TEST 4
# EXPECTED: FORCE REFRESH BYPASSES CACHE
# --------------------------------------------------

print()
print("STEP 5 - FORCE REFRESH")
print("-" * 80)

forced = cache.load(
    symbol,
    force_refresh=True,
)

print(
    "Cache Hit    :",
    forced.get(
        "cache_hit"
    ),
)

print(
    "Cache Status :",
    forced.get(
        "cache_status"
    ),
)

assert (
    forced.get(
        "cache_hit"
    )
    is False
)

assert (
    forced.get(
        "cache_status"
    )
    == "FORCE_REFRESH"
)

print(
    "RESULT       : PASS"
)


# --------------------------------------------------
# TEST 5
# FAILED ANALYSIS MUST NOT BE CACHED
# --------------------------------------------------

print()
print("STEP 6 - REJECT FAILED ANALYSIS")
print("-" * 80)

failed_analysis = {

    "status":
        "ERROR",

    "symbol":
        "FAILEDSTOCK",

    "error":
        "Simulated data failure",
}

failed_save = cache.save(
    "FAILEDSTOCK",
    failed_analysis,
)

print(
    "Saved        :",
    failed_save.get(
        "saved"
    ),
)

print(
    "Reason       :",
    failed_save.get(
        "reason"
    ),
)

assert (
    failed_save.get(
        "saved"
    )
    is False
)

print(
    "RESULT       : PASS"
)


# --------------------------------------------------
# TEST 6
# EXPECTED: DELETE CACHE
# --------------------------------------------------

print()
print("STEP 7 - DELETE CACHE")
print("-" * 80)

deleted = cache.delete(
    symbol
)

print(
    "Deleted      :",
    deleted
)

assert (
    deleted
    is True
)

after_delete = cache.load(
    symbol
)

print(
    "Cache Hit    :",
    after_delete.get(
        "cache_hit"
    ),
)

print(
    "Cache Status :",
    after_delete.get(
        "cache_status"
    ),
)

assert (
    after_delete.get(
        "cache_hit"
    )
    is False
)

assert (
    after_delete.get(
        "cache_status"
    )
    == "MISS"
)

print(
    "RESULT       : PASS"
)


# --------------------------------------------------
# FINAL RESULT
# --------------------------------------------------

print()
print("=" * 80)
print(
    "ALL SCAN CACHE TESTS PASSED"
)
print("=" * 80)