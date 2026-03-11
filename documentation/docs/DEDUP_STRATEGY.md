# Deduplication Strategy

## Overview

The dedup engine (`app/dedup/dedup_engine.py`) applies multiple layers of deduplication to prevent the same job from appearing multiple times in the database.

This is important because:
- Multiple sources (Drushim, AllJobs, RSS feeds) may list the same job
- The same source may return overlapping results across scraping runs
- Job titles can vary slightly for the same role

## Dedup Layers

The engine applies layers in order. The first match wins; subsequent layers are not evaluated.

### Layer 1: URL Match (fastest)
- Normalize URL: lowercase, strip trailing slash
- If two jobs have the same URL, they are duplicates
- This catches the most obvious cases with O(1) lookup

### Layer 2: Source Job ID
- Composite key: `source_name::job_id`
- Prevents the same job appearing twice from the same source
- Useful when re-scraping a source that returns overlapping batches
- Only active when `source_job_id` is set on the job object (optional field)

### Layer 3: Title + Company + City Fingerprint
- Normalized fingerprint: `normalize(title)|normalize(company)|normalize(city)`
- Normalization: lowercase, strip punctuation, collapse whitespace
- Catches cross-source duplicates where URLs differ but the job is the same

### Layer 4: Fuzzy Title Match (optional)
- Requires: `pip install rapidfuzz`
- Compares normalized title strings using `token_sort_ratio`
- Threshold: 88/100 (configurable)
- Handles titles with minor wording differences: "Python Dev" vs "Python Developer"
- Gracefully disabled if `rapidfuzz` is not installed

## Usage

```python
from app.dedup.dedup_engine import DedupEngine

engine = DedupEngine()
unique_jobs, result = engine.deduplicate(raw_jobs)

print(f"Input: {result.total_input}")
print(f"Unique: {result.unique_count}")
print(f"Duplicates: {result.duplicate_count}")
print(f"  by URL: {result.duplicates_by_url}")
print(f"  by source_id: {result.duplicates_by_source_id}")
print(f"  by fingerprint: {result.duplicates_by_fingerprint}")
print(f"  by fuzzy: {result.duplicates_by_fuzzy}")
```

## Integration with DB Normalizer

The existing `app/db/normalizer.py` (`insert_jobs_dedup`) handles DB-level deduplication via the `unique_hash` column (SHA-256 of title+company+description).

The `DedupEngine` is designed for **pre-DB deduplication**: clean the batch before inserting, reducing unnecessary DB round-trips.

For a full pipeline:
```python
engine = DedupEngine()
unique_jobs, _ = engine.deduplicate(raw_jobs)
insert_jobs_dedup(session, unique_jobs)   # DB-level final guard
```

## Performance

| Layer | Complexity | Dependency |
|-------|-----------|------------|
| URL | O(1) | None |
| Source ID | O(1) | None |
| Fingerprint | O(1) | None |
| Fuzzy | O(n) per job | rapidfuzz (optional) |

For large batches (1000+ jobs), consider disabling fuzzy dedup or increasing the threshold.
