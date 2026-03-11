# app/notifications/file_notifier.py
"""
File notifier — ACTIVE.

Appends job notifications to a local summary file.
Useful for logging, audits, or importing into other tools.

Default output: data/job_notifications.txt
"""
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.notifications.base_notifier import BaseNotifier

logger = logging.getLogger(__name__)

_DEFAULT_OUTPUT_PATH = Path(__file__).parent.parent.parent / "data" / "job_notifications.txt"

_FILE_TEMPLATE = (
    "[{timestamp}] MATCH: {title} @ {company} | Score: {score:.1f} ({level}) "
    "| Source: {source} | URL: {url}\n"
)


class FileNotifier(BaseNotifier):
    """
    Appends job notifications to a local text file.

    STATUS: ACTIVE — always enabled, writes to data/job_notifications.txt by default.

    Usage:
        notifier = FileNotifier()
        notifier.notify(job_dict)

        # Custom path:
        notifier = FileNotifier(output_path=Path("/tmp/jobs.txt"))
    """

    notifier_name = "file"
    enabled = True

    def __init__(self, output_path: Path | None = None):
        self.output_path = Path(output_path or _DEFAULT_OUTPUT_PATH)

    def is_ready(self) -> bool:
        """Always ready — will create the file and parent dirs on first write."""
        return True

    def notify(self, job: dict[str, Any]) -> bool:
        score = float(job.get("match_score") or job.get("final_score") or 0.0)
        level = (job.get("match_level") or job.get("final_level") or "unknown").upper()

        line = _FILE_TEMPLATE.format(
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
            title=job.get("title", "Unknown Title"),
            company=job.get("company", "Unknown Company"),
            score=score,
            level=level,
            source=job.get("source", "unknown"),
            url=job.get("url", ""),
        )

        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, "a", encoding="utf-8") as f:
                f.write(line)
            logger.debug("[FileNotifier] Wrote notification to %s", self.output_path)
            return True
        except Exception as exc:
            logger.error("[FileNotifier] Failed to write notification: %s", exc)
            return False
