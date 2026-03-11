# app/collectors/israel/jobnet_collector.py
# This file defines the JobNetCollector class for scraping jobs from JobNet.co.il, an Israeli job board.

"""
JobNet.co.il collector — DISABLED / PLANNED.

STATUS: DISABLED — not yet implemented.
This file is a placeholder to reserve the module structure.

JobNet is a mid-size Israeli job board focused on mid-to-senior roles.
Real implementation would require HTTP scraping.
"""
import logging
from typing import Any

from app.collectors.base import RawJob
from app.collectors.israel.base_israel_collector import BaseIsraeliCollector

logger = logging.getLogger(__name__)


class JobNetCollector(BaseIsraeliCollector):
    """
    Placeholder collector for JobNet.co.il.

    STATUS: DISABLED — returns empty list until implemented.

    TODO (when implementing):
        1. Scrape https://www.jobnet.co.il/Jobs/Search?keyword={query}
        2. Parse job cards from HTML
        3. Extract title, company, city, description, URL
        4. Handle pagination
    """

    source_name = "jobnet"
    supports_apply_link = True
    requires_auth = False

    ENABLED = False  # Set to True when real scraping is implemented

    def fetch_jobs(self) -> list[dict[str, Any]]:
        logger.debug("[jobnet] collector is DISABLED — returning empty list")
        return []

    def normalize_job(self, raw: dict[str, Any]) -> RawJob:
        raise NotImplementedError("JobNetCollector.normalize_job() not yet implemented")
