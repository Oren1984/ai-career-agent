# n8n Automation — Future / Not Activated

## Status

This directory contains **n8n workflow automation templates**.
n8n is NOT running in the default setup.

## What is n8n?

n8n is a workflow automation platform (like Zapier but self-hosted).
It can receive webhooks from the AI Career Agent and route notifications to any channel: email, Slack, Telegram, Notion, Google Sheets, etc.

## When to Activate

Use n8n when you want to:
- Send notifications to multiple channels without modifying Python code
- Build conditional workflows (e.g. only notify for jobs in Tel Aviv)
- Integrate with non-Python tools (Notion, Airtable, Google Sheets)

## Activation Steps

1. **Start n8n** (separate from the main agent Docker stack)
   ```bash
   cd automation/n8n
   docker compose -f docker-compose.n8n.yml up -d
   ```

2. **Open n8n UI**
   http://localhost:5678

3. **Import the example workflow**
   UI → Workflows → Import → select `workflows/example_job_notification.json`

4. **Configure notification channels**
   Add Email / Slack / Telegram nodes in the workflow editor

5. **Activate the webhook endpoint**
   The webhook URL will be: `http://localhost:5678/webhook/job-notification`

6. **Wire the bridge** in the AI Career Agent
   See `automation/bridge/webhook_contract.md` for the payload format.
   Update `app/notifications/notification_orchestrator.py` to POST to the webhook.

## Files

| File | Purpose |
|------|---------|
| `docker-compose.n8n.yml` | Docker compose for standalone n8n |
| `workflows/example_job_notification.json` | Example workflow template |
