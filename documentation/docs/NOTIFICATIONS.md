# Notifications

## Overview

The notification system alerts you when new high-match jobs are found.
It is built around a `BaseNotifier` interface with multiple channel implementations.

## Architecture

```
NotificationOrchestrator
  ├── ConsoleNotifier   (ACTIVE — prints to stdout/log)
  ├── FileNotifier      (ACTIVE — writes to data/job_notifications.txt)
  ├── EmailNotifier     (FUTURE — disabled until SMTP configured)
  └── [Future: GmailNotifier, SlackNotifier, TelegramNotifier]
```

### BaseNotifier Interface
```python
class BaseNotifier(ABC):
    notifier_name: str
    enabled: bool

    def is_ready(self) -> bool: ...       # can we send?
    def notify(self, job: dict) -> bool: ...  # send one job notification
    def notify_batch(self, jobs: list) -> int: ...  # send multiple (default: loops)
```

## Active Notifiers

### ConsoleNotifier
- Prints formatted job notification to stdout
- Also logs via Python logger
- Always ready, no configuration needed
- File: `app/notifications/console_notifier.py`

### FileNotifier
- Appends one line per job to `data/job_notifications.txt`
- Creates the file and parent directories if they don't exist
- Always ready, no configuration needed
- File: `app/notifications/file_notifier.py`

### Example output (file):
```
[2026-03-11 10:30:00] MATCH: AI Engineer @ StartupAI | Score: 10.5 (HIGH) | Source: drushim | URL: https://...
```

## Notification Orchestrator

```python
from app.notifications.notification_orchestrator import NotificationOrchestrator

orchestrator = NotificationOrchestrator()
sent = orchestrator.notify_new_high_matches(session)
print(f"Notified {sent} new high-match jobs")
```

The orchestrator:
1. Loads all high-match jobs from the database
2. Filters out jobs already notified (tracked in `data/notifications_sent.json`)
3. Dispatches each new job to all ready notifiers
4. Saves updated notification log

## Future Notifiers

### EmailNotifier (disabled)
- File: `app/notifications/email_notifier.py`
- Requires: SMTP credentials in `config/notifications.yaml`
- Set `enabled=True` when instantiating to activate

### GmailNotifier (future/planned)
- See `app/integrations/gmail/` and `docs/` for setup guide

## Legacy Notifier

The original `app/notifications/notifier.py` (`Notifier` class) supports:
- Email, Slack, Telegram channels
- Configured via `config/notifications.yaml`
- Still fully functional alongside the new system

The new `NotificationOrchestrator` is a cleaner, more modular replacement
designed for the V1 closure. Both can coexist.

## Dedup / Sent Log

Both the legacy `Notifier` and new `NotificationOrchestrator` use
`data/notifications_sent.json` to track which job IDs have been notified.

Format:
```json
{"notified_job_ids": [1, 2, 3, 42]}
```
