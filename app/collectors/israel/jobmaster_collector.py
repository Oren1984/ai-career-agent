# app/collectors/israel/jobmaster_collector.py
# This file defines the JobMasterCollector class for scraping jobs from JobMaster, an Israeli job board.

"""
JobMaster.co.il collector — DISABLED / PLANNED.

STATUS: DISABLED — not yet implemented.

JobMaster is a significant Israeli job board, particularly strong
in tech and engineering roles.
"""
import logging
from typing import Any

from app.collectors.base import RawJob
from app.collectors.israel.base_israel_collector import BaseIsraeliCollector

logger = logging.getLogger(__name__)


class JobMasterCollector(BaseIsraeliCollector):
    """
    Placeholder collector for JobMaster.co.il.

    STATUS: DISABLED — returns empty list until implemented.

    TODO (when implementing):
        1. Scrape https://www.jobmaster.co.il/jobs/?q={query}
        2. Parse listing HTML with BeautifulSoup
        3. Implement fetch_jobs() and normalize_job()
        4. Set ENABLED = True and add to sources.yaml
    """

    source_name = "jobmaster"
    supports_apply_link = True
    requires_auth = False

    ENABLED = False

    def fetch_jobs(self) -> list[dict[str, Any]]:
        logger.debug("[jobmaster] collector is DISABLED — returning empty list")
        return []

    def normalize_job(self, raw: dict[str, Any]) -> RawJob:
        raise NotImplementedError("JobMasterCollector.normalize_job() not yet implemented")
