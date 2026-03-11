# app/dedup/dedup_engine.py
# This file implements the DedupEngine class, which provides layered deduplication for job records.

"""
Layered deduplication engine for job records.

Dedup strategy (applied in order, stopping at first match):
  Layer 1: URL match           — same URL = same job
  Layer 2: source_job_id match — same source + job ID = same job
  Layer 3: title + company + city fingerprint — normalized string match
  Layer 4: fuzzy title match   — optional, requires rapidfuzz (graceful fallback)

Usage:
    from app.dedup.dedup_engine import DedupEngine
    from app.collectors.base import RawJob

    engine = DedupEngine()
    unique_jobs = engine.deduplicate(raw_jobs)

    # Or check a single job against an existing set:
    engine.add(existing_job)
    is_dup = engine.is_duplicate(new_job)
"""
import hashlib
import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# Fuzzy match threshold (0-100). Jobs scoring >= this are considered duplicates.
_FUZZY_THRESHOLD = 88

# Whether to attempt fuzzy matching (requires rapidfuzz)
_FUZZY_ENABLED = True


def _try_import_fuzzy():
    """Return the fuzz module or None if rapidfuzz is not installed."""
    try:
        from rapidfuzz import fuzz
        return fuzz
    except ImportError:
        return None


def _normalize_text(text: str) -> str:
    """Lowercase, strip punctuation and extra whitespace for comparison."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _url_key(url: str) -> str:
    """Normalize a URL by stripping trailing slashes and lowercasing."""
    return url.lower().rstrip("/").strip()


def _title_company_city_key(title: str, company: str, city: str) -> str:
    """Build a normalized fingerprint for title + company + city."""
    parts = [_normalize_text(title), _normalize_text(company), _normalize_text(city)]
    return "|".join(parts)


def _source_id_key(source: str, source_job_id: str) -> str:
    """Composite key: source name + source-specific job ID."""
    return f"{source.lower().strip()}::{source_job_id.strip()}"


@dataclass
class DedupResult:
    """Result of a deduplication run."""
    total_input: int = 0
    unique_count: int = 0
    duplicate_count: int = 0
    duplicates_by_url: int = 0
    duplicates_by_source_id: int = 0
    duplicates_by_fingerprint: int = 0
    duplicates_by_fuzzy: int = 0


class DedupEngine:
    """
    Multi-layer deduplication for RawJob records.

    Maintains internal state (seen URL/ID/fingerprint sets) so it can
    be reused across multiple batches or incrementally fed new jobs.

    Layer descriptions:
      1. URL             : exact URL match (fast, O(1))
      2. source_job_id   : source + job-ID pair match (fast, O(1))
                           Note: source_job_id must be set on RawJob — optional field
      3. Fingerprint     : normalized(title) + normalized(company) + normalized(city)
      4. Fuzzy           : rapidfuzz token_sort_ratio on title, optional

    Call reset() to clear state between independent runs.
    """

    def __init__(self, fuzzy_threshold: int = _FUZZY_THRESHOLD, enable_fuzzy: bool = _FUZZY_ENABLED):
        self.fuzzy_threshold = fuzzy_threshold
        self.enable_fuzzy = enable_fuzzy
        self._fuzz = _try_import_fuzzy() if enable_fuzzy else None

        if enable_fuzzy and self._fuzz is None:
            logger.info(
                "DedupEngine: rapidfuzz not installed — fuzzy dedup disabled. "
                "Install with: pip install rapidfuzz"
            )

        self.reset()

    def reset(self) -> None:
        """Clear all seen-job state."""
        self._seen_urls: set[str] = set()
        self._seen_source_ids: set[str] = set()
        self._seen_fingerprints: set[str] = set()
        self._seen_titles: list[str] = []   # kept as list for fuzzy ratio scan

    def add(self, job: Any) -> None:
        """
        Register a job as 'seen' without duplicate checking.

        Use this to pre-populate the engine with already-stored jobs
        before running deduplication on a new batch.

        Args:
            job: Either a RawJob dataclass or any object with .url, .source,
                 .title, .company, .location attributes.
        """
        url = _url_key(getattr(job, "url", "") or "")
        if url:
            self._seen_urls.add(url)

        source = getattr(job, "source", "") or ""
        source_job_id = getattr(job, "source_job_id", "") or ""
        if source and source_job_id:
            self._seen_source_ids.add(_source_id_key(source, source_job_id))

        title = getattr(job, "title", "") or ""
        company = getattr(job, "company", "") or ""
        location = getattr(job, "location", "") or ""
        fp = _title_company_city_key(title, company, location)
        if fp:
            self._seen_fingerprints.add(fp)

        if self._fuzz and title:
            self._seen_titles.append(_normalize_text(title))

    def is_duplicate(self, job: Any) -> tuple[bool, str]:
        """
        Check whether a job is a duplicate of any previously seen job.

        Returns:
            (is_dup: bool, reason: str)
            reason is one of: "url", "source_id", "fingerprint", "fuzzy", ""
        """
        # Layer 1: URL
        url = _url_key(getattr(job, "url", "") or "")
        if url and url in self._seen_urls:
            return True, "url"

        # Layer 2: source_job_id
        source = getattr(job, "source", "") or ""
        source_job_id = getattr(job, "source_job_id", "") or ""
        if source and source_job_id:
            sk = _source_id_key(source, source_job_id)
            if sk in self._seen_source_ids:
                return True, "source_id"

        # Layer 3: title + company + city fingerprint
        title = getattr(job, "title", "") or ""
        company = getattr(job, "company", "") or ""
        location = getattr(job, "location", "") or ""
        fp = _title_company_city_key(title, company, location)
        if fp and fp in self._seen_fingerprints:
            return True, "fingerprint"

        # Layer 4: fuzzy title match (optional)
        if self._fuzz and title and self._seen_titles:
            norm_title = _normalize_text(title)
            for seen_title in self._seen_titles:
                score = self._fuzz.token_sort_ratio(norm_title, seen_title)
                if score >= self.fuzzy_threshold:
                    return True, "fuzzy"

        return False, ""

    def deduplicate(self, jobs: list[Any]) -> tuple[list[Any], DedupResult]:
        """
        Deduplicate a list of RawJob records.

        Processes jobs in order. First occurrence wins; subsequent duplicates
        are dropped. Also updates internal state so the engine can be reused.

        Args:
            jobs: List of RawJob (or any objects with url/source/title/company/location).

        Returns:
            (unique_jobs, DedupResult)
        """
        result = DedupResult(total_input=len(jobs))
        unique: list[Any] = []

        for job in jobs:
            is_dup, reason = self.is_duplicate(job)

            if is_dup:
                result.duplicate_count += 1
                if reason == "url":
                    result.duplicates_by_url += 1
                elif reason == "source_id":
                    result.duplicates_by_source_id += 1
                elif reason == "fingerprint":
                    result.duplicates_by_fingerprint += 1
                elif reason == "fuzzy":
                    result.duplicates_by_fuzzy += 1

                logger.debug(
                    "Duplicate [%s]: %s @ %s",
                    reason,
                    getattr(job, "title", "?"),
                    getattr(job, "company", "?"),
                )
            else:
                self.add(job)
                unique.append(job)

        result.unique_count = len(unique)
        logger.info(
            "DedupEngine: %d → %d unique (%d duplicates: url=%d, source_id=%d, fingerprint=%d, fuzzy=%d)",
            result.total_input,
            result.unique_count,
            result.duplicate_count,
            result.duplicates_by_url,
            result.duplicates_by_source_id,
            result.duplicates_by_fingerprint,
            result.duplicates_by_fuzzy,
        )
        return unique, result
