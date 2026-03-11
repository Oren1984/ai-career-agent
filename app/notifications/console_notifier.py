# app/notifications/console_notifier.py
"""
Console/log notifier — ACTIVE.

Writes job notifications to stdout and the Python logger.
Always available, zero dependencies.
"""
import logging
from typing import Any

from app.notifications.base_notifier import BaseNotifier

logger = logging.getLogger(__name__)

_CONSOLE_TEMPLATE = """\
========================================
  NEW HIGH-MATCH JOB FOUND
========================================
  Title   : {title}
  Company : {company}
  Location: {location}
  Score   : {score:.1f} ({level})
  Source  : {source}
  URL     : {url}
========================================"""


class ConsoleNotifier(BaseNotifier):
    """
    Outputs job notifications to the console and Python logger.

    STATUS: ACTIVE — always enabled, no configuration required.

    Usage:
        notifier = ConsoleNotifier()
        notifier.notify(job_dict)
    """

    notifier_name = "console"
    enabled = True

    def is_ready(self) -> bool:
        return True

    def notify(self, job: dict[str, Any]) -> bool:
        score = float(job.get("match_score") or job.get("final_score") or 0.0)
        level = (job.get("match_level") or job.get("final_level") or "unknown").upper()

        message = _CONSOLE_TEMPLATE.format(
            title=job.get("title", "Unknown Title"),
            company=job.get("company", "Unknown Company"),
            location=job.get("location", ""),
            score=score,
            level=level,
            source=job.get("source", "unknown"),
            url=job.get("url", ""),
        )

        print(message)
        logger.info(
            "[ConsoleNotifier] Job: %s @ %s — score %.1f (%s)",
            job.get("title", "?"),
            job.get("company", "?"),
            score,
            level,
        )
        return True
