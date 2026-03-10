# Test Results — AI Career Agent V2.5

**Date:** 2026-03-10
**Result:** 200 passed, 0 failed, 2 skipped
**Runtime:** ~13s

---

## Test Suite Summary

| Test File | Tests | Status | Coverage |
|---|---|---|---|
| test_collectors.py | 6 | ✅ pass | MockCollector, RSSCollector |
| test_dedup.py | 11 | ✅ pass | Hash, insert_jobs_dedup |
| test_database.py | 15 | ✅ pass | Job, Score, StatusHistory ORM |
| test_filtering.py | 11 | ✅ pass | FilterEngine keyword rules |
| test_scoring.py | 11 | ✅ pass | Scorer keyword scoring |
| test_dashboard.py | 6 | ✅ pass | Dashboard imports, service sanity |
| test_session_robustness.py | 7 | ✅ pass | Session recovery, duplicate handling |
| test_source_loader.py | 11 | ✅ pass | Source config loading |
| **test_llm_providers.py** | **20** | ✅ pass | Provider factory, fallback, all providers |
| **test_semantic_scoring.py** | **31** | ✅ pass | SemanticScorer, CombinedScorer |
| **test_candidate_profile.py** | **17** | ✅ pass | Profile loader, all file types |
| **test_scheduler.py** | **10** | ✅ pass / 2 skip | run_once, scheduler creation |
| **test_analytics.py** | **13** | ✅ pass | Source analytics, V2 score fields |
| **test_new_collectors.py** | **29** | ✅ pass | Greenhouse, Lever, HackerNews, source_loader |
| **Total** | **200** | **✅ all pass** | |

Bold = new V2 tests

---

## Skipped Tests

2 tests skipped in `test_scheduler.py`:
- `test_create_scheduler_returns_scheduler` — requires APScheduler (optional dependency)
- `test_create_scheduler_custom_cron` — requires APScheduler (optional dependency)

These skip correctly when APScheduler is not installed. Install with:
```bash
pip install apscheduler>=3.10.0
```

---

## V1.5 Regression

All 78 original V1.5 tests continue to pass without modification.

---

## How to Run

```bash
# All tests
python -m pytest tests/

# V2 tests only
python -m pytest tests/test_llm_providers.py tests/test_semantic_scoring.py \
    tests/test_candidate_profile.py tests/test_scheduler.py tests/test_analytics.py

# With verbose output
python -m pytest tests/ -v

# Fast (no external calls — all tests use mock/in-memory)
python -m pytest tests/ -q
```

All tests use in-memory SQLite and mocked external calls. No network access required.
