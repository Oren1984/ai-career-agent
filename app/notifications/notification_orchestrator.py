# app/notifications/notification_orchestrator.py
"""
Notification orchestrator — routes job alerts to all active notifiers.

Manages a list of BaseNotifier instances and dispatches notifications
across all active channels. Tracks which jobs have already been notified
to prevent duplicate alerts.

Usage:
    from app.notifications.notification_orchestrator import NotificationOrchestrator

    orchestrator = NotificationOrchestrator()
    sent = orchestrator.notify_new_high_matches(session)
    print(f"Notified {sent} new high-match jobs")
"""
import json
import logging
from pathlib import Path
from typing import Any

from app.notifications.base_notifier import BaseNotifier
from app.notifications.console_notifier import ConsoleNotifier
from app.notifications.file_notifier import FileNotifier

logger = logging.getLogger(__name__)

_DEFAULT_SENT_LOG = Path(__file__).parent.parent.parent / "data" / "notifications_sent.json"


def _load_sent_log(path: Path) -> set[int]:
    """Load previously notified job IDs."""
    if not path.exists():
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(int(i) for i in data.get("notified_job_ids", []))
    except Exception as exc:
        logger.warning("Could not read notification log: %s", exc)
        return set()


def _save_sent_log(job_ids: set[int], path: Path) -> None:
    """Persist notified job IDs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"notified_job_ids": sorted(job_ids)}, f, indent=2)
    except Exception as exc:
        logger.error("Could not save notification log: %s", exc)


class NotificationOrchestrator:
    """
    Orchestrates notifications across multiple channels.

    Active notifiers (default):
      - ConsoleNotifier : prints to stdout/log
      - FileNotifier    : writes to data/job_notifications.txt

    Future / disabled notifiers:
      - EmailNotifier   : disabled until configured
      - GmailNotifier   : planned (see app/integrations/gmail/)

    Each job is notified at most once (tracked by job ID in data/notifications_sent.json).
    """

    def __init__(
        self,
        notifiers: list[BaseNotifier] | None = None,
        sent_log_path: Path | None = None,
    ):
        self._sent_log_path = sent_log_path or _DEFAULT_SENT_LOG
        self.sent_ids = _load_sent_log(self._sent_log_path)

        if notifiers is not None:
            self.notifiers = notifiers
        else:
            # Default active notifiers
            self.notifiers = [
                ConsoleNotifier(),
                FileNotifier(),
            ]

        active = [n.notifier_name for n in self.notifiers if n.is_ready()]
        logger.info(
            "NotificationOrchestrator ready: %d notifier(s) active: %s, %d jobs already seen",
            len(active),
            active,
            len(self.sent_ids),
        )

    def add_notifier(self, notifier: BaseNotifier) -> None:
        """Add a notifier to the active list."""
        self.notifiers.append(notifier)

    def notify_job(self, job: dict[str, Any]) -> int:
        """
        Send a notification for a single job via all ready notifiers.

        Returns the number of notifiers that successfully sent.
        """
        count = 0
        for notifier in self.notifiers:
            if not notifier.is_ready():
                continue
            try:
                if notifier.notify(job):
                    count += 1
            except Exception as exc:
                logger.error(
                    "[%s] Exception during notify: %s", notifier.notifier_name, exc
                )
        return count

    def notify_new_high_matches(self, session) -> int:
        """
        Find all high-match jobs not yet notified and dispatch alerts.

        Args:
            session: SQLAlchemy session (used to query jobs with scores).

        Returns:
            Number of jobs for which at least one notification was sent.
        """
        from app.services.job_service import JobService

        svc = JobService(session)
        all_high = svc.get_jobs_with_scores(match_level_filter="high")
        new_jobs = [j for j in all_high if j.get("id") not in self.sent_ids]

        if not new_jobs:
            logger.info("No new high-match jobs to notify")
            return 0

        logger.info("Notifying %d new high-match job(s)", len(new_jobs))
        sent_count = 0

        for job in new_jobs:
            job_id = job.get("id")
            dispatched = self.notify_job(job)
            if dispatched > 0:
                self.sent_ids.add(job_id)
                sent_count += 1

        if sent_count:
            _save_sent_log(self.sent_ids, self._sent_log_path)

        return sent_count
