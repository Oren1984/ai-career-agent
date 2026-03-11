# app/integrations/gmail/gmail_mock.py
# This file implements the GmailMockClient class, a mock version of GmailClient for testing purposes.

"""
Mock Gmail client for testing — does NOT send real emails.

Used in tests to verify notification logic without requiring
OAuth credentials or network access.
"""
import logging
from typing import Any

from app.integrations.gmail.gmail_models import GmailMessage, GmailSendResult

logger = logging.getLogger(__name__)


class GmailMockClient:
    """
    Mock implementation of GmailClient for use in tests.

    Records all calls to send() in self.sent_messages.
    Can be configured to simulate failures with force_fail=True.

    Usage in tests:
        mock_gmail = GmailMockClient()
        result = mock_gmail.send(GmailMessage(to="test@test.com", subject="Test", body="Hello"))
        assert result.success is True
        assert len(mock_gmail.sent_messages) == 1
    """

    def __init__(self, force_fail: bool = False):
        self.force_fail = force_fail
        self.sent_messages: list[GmailMessage] = []
        self.call_count = 0

    def send(self, message: GmailMessage) -> GmailSendResult:
        """Record the send call and return a mock result."""
        self.call_count += 1

        if self.force_fail:
            logger.debug("[GmailMock] Simulating send failure")
            return GmailSendResult(success=False, error="Mock forced failure")

        self.sent_messages.append(message)
        mock_message_id = f"mock-msg-{self.call_count:04d}"
        logger.debug("[GmailMock] Recorded send to %s: %s", message.to, message.subject)
        return GmailSendResult(success=True, message_id=mock_message_id)

    def reset(self) -> None:
        """Clear recorded messages and reset counter."""
        self.sent_messages.clear()
        self.call_count = 0
