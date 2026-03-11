# app/collectors/israel/jobkarov_collector.py
# This file defines the JobKarovCollector class for scraping jobs from JobKarov, an Israeli job board.

"""
JobKarov collector — DISABLED / PLANNED.

STATUS: DISABLED — not yet implemented.

JobKarov ("near job") focuses on local jobs in Israel.
"""
import logging
from typing import Any

from app.collectors.base import RawJob
from app.collectors.israel.base_israel_collector import BaseIsraeliCollector

logger = logging.getLogger(__name__)


class JobKarovCollector(BaseIsraeliCollector):
    """
    Placeholder collector for JobKarov.

    STATUS: DISABLED — returns empty list until implemented.

    TODO (when implementing):
        1. Identify scraping endpoint or API for JobKarov
        2. Implement fetch_jobs() and normalize_job()
        3. Set ENABLED = True and add to sources.yaml
    """

    source_name = "jobkarov"
    supports_apply_link = False
    requires_auth = False

    ENABLED = False

    def fetch_jobs(self) -> list[dict[str, Any]]:
        logger.debug("[jobkarov] collector is DISABLED — returning empty list")
        return []

    def normalize_job(self, raw: dict[str, Any]) -> RawJob:
        raise NotImplementedError("JobKarovCollector.normalize_job() not yet implemented")
