# Gmail Integration — Future / Not Activated

## Status

This module is **NOT activated**. It is a forward-compatible placeholder.

Do not use `GmailClient` in production until OAuth 2.0 credentials are configured.

## When to Activate

Use this integration when you want the agent to send job notifications via a real Gmail account instead of the current console/file notifiers.

## Activation Steps

1. **Enable Gmail API** in Google Cloud Console
   https://console.cloud.google.com/ → APIs & Services → Enable Gmail API

2. **Create OAuth 2.0 credentials**
   APIs & Services → Credentials → Create Credentials → OAuth client ID
   Type: Desktop app
   Download `credentials.json`

3. **Install dependencies**
   ```bash
   pip install google-auth google-auth-oauthlib google-api-python-client
   ```

4. **Run the OAuth flow** (one-time, generates `token.json`)
   ```python
   from app.integrations.gmail.gmail_client import GmailClient
   client = GmailClient()
   client._build_service()   # Follow the browser prompt
   ```

5. **Set `ENABLED = True`** in `gmail_client.py`

6. **Wire into NotificationOrchestrator**
   ```python
   from app.integrations.gmail.gmail_client import GmailClient
   from app.notifications.notification_orchestrator import NotificationOrchestrator

   orchestrator = NotificationOrchestrator()
   # Add a Gmail-backed notifier here
   ```

## Files

| File | Purpose |
|------|---------|
| `gmail_client.py` | Real Gmail API client (disabled, full TODOs inside) |
| `gmail_models.py` | `GmailMessage` and `GmailSendResult` dataclasses |
| `gmail_mock.py`   | Mock client for use in tests — safe to use anytime |

## Security Notes

- Never commit `credentials.json` or `token.json` to git
- Add both files to `.gitignore`
- In production, store credentials in environment variables or a secrets manager
