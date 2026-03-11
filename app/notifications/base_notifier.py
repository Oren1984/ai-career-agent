# app/notifications/base_notifier.py
"""Abstract base interface for notifiers."""
from abc import ABC, abstractmethod
from typing import Any


class BaseNotifier(ABC):
    """
    Base interface for all notifier implementations.

    A notifier receives a job dict (from get_jobs_with_scores) and
    dispatches an alert via a specific output channel (console, file, email, etc.).
    """

    notifier_name: str = "base"
    enabled: bool = True

    @abstractmethod
    def is_ready(self) -> bool:
        """Return True if this notifier is configured and ready to send."""
        ...

    @abstractmethod
    def notify(self, job: dict[str, Any]) -> bool:
        """
        Send a notification for a single job.

        Args:
            job: Job dict from JobService.get_jobs_with_scores().

        Returns:
            True if notification was sent/written successfully.
        """
        ...

    def notify_batch(self, jobs: list[dict[str, Any]]) -> int:
        """
        Notify for a list of jobs. Returns count of successful notifications.
        Default implementation loops over notify(); subclasses may override.
        """
        count = 0
        for job in jobs:
            if self.notify(job):
                count += 1
        return count
