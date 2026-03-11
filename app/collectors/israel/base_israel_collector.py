# app/collectors/israel/base_israel_collector.py
# This file defines the BaseIsraeliCollector abstract class, 
# which provides a common interface and shared logic for all Israeli job board collectors.

"""Base class for all Israeli job board collectors."""
from abc import abstractmethod
from typing import Any

from app.collectors.base import BaseCollector, RawJob


class BaseIsraeliCollector(BaseCollector):
    """
    Base class for Israeli job board collectors.

    Extends BaseCollector with Israel-specific interface elements:
      - source_name     : unique identifier for the source (str)
      - supports_apply_link : whether the source exposes a direct apply URL
      - requires_auth   : whether the source requires login/session cookies
      - country         : always "IL" for Israeli sources

    Concrete subclasses implement:
      - fetch_jobs()    : raw HTTP / scraping call → returns list of raw dicts
      - normalize_job() : converts one raw dict into a RawJob
      - collect()       : orchestrates fetch → normalize (inherited pattern)
    """

    source_name: str = "israel_base"
    supports_apply_link: bool = False
    requires_auth: bool = False
    country: str = "IL"

    @abstractmethod
    def fetch_jobs(self) -> list[dict[str, Any]]:
        """
        Fetch raw job data from the source.

        Returns a list of dicts — the raw representation from the site
        before any normalization. Each implementation defines its own schema.

        TODO (real implementation): make HTTP requests, parse HTML/JSON here.
        """
        ...

    @abstractmethod
    def normalize_job(self, raw: dict[str, Any]) -> RawJob:
        """
        Convert a single raw job dict into a standardized RawJob.

        Args:
            raw: One item from the list returned by fetch_jobs().

        Returns:
            A RawJob ready for DB insertion.
        """
        ...

    def collect(self) -> list[RawJob]:
        """
        Orchestrate fetch → normalize for all raw job records.

        Skips individual items that fail normalization so one bad record
        does not abort the entire batch.
        """
        import logging
        logger = logging.getLogger(__name__)

        raw_items = self.fetch_jobs()
        jobs: list[RawJob] = []

        for item in raw_items:
            try:
                job = self.normalize_job(item)
                jobs.append(job)
            except Exception as exc:
                logger.warning(
                    "[%s] Failed to normalize job item: %s — %s",
                    self.source_name,
                    item.get("title", "?"),
                    exc,
                )

        return jobs
