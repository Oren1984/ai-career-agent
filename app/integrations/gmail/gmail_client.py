# app/integrations/gmail/gmail_client.py
# This file implements the GmailClient class for sending emails via the Gmail API using OAuth 2.0.

"""
Gmail API client — FUTURE / NOT ACTIVATED.

STATUS: Disabled. This module is a forward-compatible placeholder.
Do NOT import or instantiate in production until OAuth credentials are set up.

When ready to activate:
  1. Enable Gmail API in Google Cloud Console
  2. Create OAuth 2.0 credentials and download credentials.json
  3. Install: pip install google-auth google-auth-oauthlib google-api-python-client
  4. Run the OAuth flow to generate token.json
  5. Update GmailClient config and set ENABLED = True
  6. Wire into NotificationOrchestrator

References:
  https://developers.google.com/gmail/api/quickstart/python
"""
import logging
from typing import Any

from app.integrations.gmail.gmail_models import GmailMessage, GmailSendResult

logger = logging.getLogger(__name__)

ENABLED = False  # DO NOT CHANGE — activation requires OAuth setup


class GmailClient:
    """
    Sends emails via the Gmail API using OAuth 2.0.

    STATUS: FUTURE / NOT ACTIVATED.

    This class is a complete forward-compatible implementation.
    It will fail safely (returning GmailSendResult(success=False))
    if called while ENABLED=False or credentials are missing.
    """

    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self._service = None

    def _build_service(self):
        """
        Build the Gmail API service object.

        TODO (when activating):
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
            creds = None
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                with open(self.token_path, "w") as token:
                    token.write(creds.to_json())
            self._service = build("gmail", "v1", credentials=creds)
        """
        raise NotImplementedError(
            "GmailClient._build_service() requires OAuth setup. See module docstring."
        )

    def send(self, message: GmailMessage) -> GmailSendResult:
        """
        Send a Gmail message.

        Returns GmailSendResult(success=False) if not activated.

        TODO (when activating):
            import base64
            from email.mime.text import MIMEText
            msg = MIMEText(message.body)
            msg["to"] = message.to
            msg["subject"] = message.subject
            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
            self._service.users().messages().send(
                userId="me", body={"raw": raw}
            ).execute()
        """
        if not ENABLED:
            logger.debug("GmailClient.send() called but ENABLED=False — skipping")
            return GmailSendResult(success=False, error="GmailClient is not activated")

        return GmailSendResult(success=False, error="GmailClient.send() not yet implemented")
