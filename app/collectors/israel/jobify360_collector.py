# app/collectors/israel/jobify360_collector.py
# This file defines the Jobify360Collector class for scraping jobs from Jobify360, an Israeli job board.

"""
Jobify360 collector — DISABLED / PLANNED.

STATUS: DISABLED — not yet implemented.

Jobify360 aggregates jobs from multiple Israeli sources.
Could be valuable as a meta-aggregator.
"""
import logging
from typing import Any

from app.collectors.base import RawJob
from app.collectors.israel.base_israel_collector import BaseIsraeliCollector

logger = logging.getLogger(__name__)


class Jobify360Collector(BaseIsraeliCollector):
    """
    Placeholder collector for Jobify360.

    STATUS: DISABLED — returns empty list until implemented.

    TODO (when implementing):
        1. Identify Jobify360 scraping endpoint or API
        2. Implement fetch_jobs() and normalize_job()
        3. Consider dedup against other Israeli sources (same jobs may appear)
        4. Set ENABLED = True and add to sources.yaml
    """

    source_name = "jobify360"
    supports_apply_link = False
    requires_auth = False

    ENABLED = False

    def fetch_jobs(self) -> list[dict[str, Any]]:
        logger.debug("[jobify360] collector is DISABLED — returning empty list")
        return []

    def normalize_job(self, raw: dict[str, Any]) -> RawJob:
        raise NotImplementedError("Jobify360Collector.normalize_job() not yet implemented")
