# app/notifications/email_notifier.py
"""
Email notifier — FUTURE / DISABLED.

STATUS: Disabled. Code is complete but not activated.
To activate: set enabled=True and configure SMTP credentials in notifications.yaml.

This notifier is intentionally separate from the existing EmailChannel
(app/notifications/channels/email_channel.py) which integrates with the
legacy Notifier class. This file targets the new BaseNotifier interface.
"""
import logging
from typing import Any

from app.notifications.base_notifier import BaseNotifier

logger = logging.getLogger(__name__)

_EMAIL_SUBJECT_TEMPLATE = "AI Career Agent: High Match — {title} at {company}"
_EMAIL_BODY_TEMPLATE = """\
New High-Match Job Found!

Title:    {title}
Company:  {company}
Location: {location}
Score:    {score:.1f} ({level})
Source:   {source}
Link:     {url}

---
Sent by AI Career Agent
"""


class EmailNotifier(BaseNotifier):
    """
    Sends job notifications via SMTP email.

    STATUS: FUTURE / DISABLED — not activated.

    To activate:
        1. Set smtp_host, smtp_port, username, password, to_address in config
        2. Set enabled=True when instantiating
        3. Add to NotificationOrchestrator

    Config keys (from notifications.yaml → email section):
        smtp_host     : SMTP server hostname
        smtp_port     : SMTP port (587 for TLS, 465 for SSL)
        username      : SMTP login username
        password      : SMTP login password (use env var in prod)
        from_address  : sender email
        to_address    : recipient email
    """

    notifier_name = "email"
    enabled = False  # DISABLED until configured

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def is_ready(self) -> bool:
        """Return True only if all required SMTP fields are set."""
        required = ["smtp_host", "smtp_port", "username", "password", "to_address"]
        return all(self.config.get(k) for k in required)

    def notify(self, job: dict[str, Any]) -> bool:
        """
        Send an email notification for a job.

        Returns False immediately if not configured (DISABLED state).
        """
        if not self.enabled:
            logger.debug("[EmailNotifier] Disabled — skipping")
            return False

        if not self.is_ready():
            logger.warning("[EmailNotifier] Not configured — cannot send")
            return False

        score = float(job.get("match_score") or job.get("final_score") or 0.0)
        level = (job.get("match_level") or job.get("final_level") or "unknown").upper()

        subject = _EMAIL_SUBJECT_TEMPLATE.format(
            title=job.get("title", "Unknown"),
            company=job.get("company", "Unknown"),
        )
        body = _EMAIL_BODY_TEMPLATE.format(
            title=job.get("title", "Unknown"),
            company=job.get("company", "Unknown"),
            location=job.get("location", ""),
            score=score,
            level=level,
            source=job.get("source", "unknown"),
            url=job.get("url", ""),
        )

        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg["From"] = self.config.get("from_address", self.config["username"])
            msg["To"] = self.config["to_address"]
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            smtp_host = self.config["smtp_host"]
            smtp_port = int(self.config["smtp_port"])

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(self.config["username"], self.config["password"])
                server.send_message(msg)

            logger.info(
                "[EmailNotifier] Sent to %s: %s", self.config["to_address"], subject
            )
            return True

        except Exception as exc:
            logger.error("[EmailNotifier] Failed to send email: %s", exc)
            return False
