# Webhook Contract — AI Career Agent → n8n Bridge

## Overview

When the notification system is extended to support n8n, the AI Career Agent
will POST a JSON payload to the n8n webhook endpoint for each new high-match job.

This document defines the payload contract so both sides (Python agent + n8n workflow)
can be built independently.

## Endpoint

```
POST http://localhost:5678/webhook/job-notification
Content-Type: application/json
```

## Payload Schema

```json
{
  "event": "new_high_match_job",
  "timestamp": "2026-03-11T10:30:00Z",
  "agent_version": "1.0",
  "job": {
    "id": 42,
    "title": "AI Engineer",
    "company": "StartupAI",
    "location": "Tel Aviv, Israel",
    "source": "drushim",
    "url": "https://www.drushim.co.il/job/1001",
    "date_found": "2026-03-10T08:00:00Z",
    "match_score": 10.5,
    "match_level": "high",
    "keyword_score": 9.0,
    "semantic_score": 7.5,
    "matched_keywords": ["python", "ai", "llm", "docker"],
    "rejection_flags": [],
    "explanation": "Final score: 10.5 (HIGH). Keyword score: 9.0 ..."
  }
}
```

## Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `event` | string | Always `"new_high_match_job"` for job notifications |
| `timestamp` | ISO 8601 | When the notification was triggered |
| `agent_version` | string | Version of the AI Career Agent |
| `job.id` | int | Database job ID |
| `job.title` | string | Job title |
| `job.company` | string | Company name |
| `job.location` | string | Location (city, country) |
| `job.source` | string | Collector source name (mock, drushim, alljobs, etc.) |
| `job.url` | string | Direct link to job listing |
| `job.date_found` | ISO 8601 | When the job was first collected |
| `job.match_score` | float | Final match score |
| `job.match_level` | string | `"high"` \| `"medium"` \| `"low"` |
| `job.keyword_score` | float | Raw keyword-based score |
| `job.semantic_score` | float | Semantic/theme score (0-10) |
| `job.matched_keywords` | list[str] | Keywords that matched the profile |
| `job.rejection_flags` | list[str] | Negative keywords detected |
| `job.explanation` | string | Human-readable score explanation |

## Response

n8n should return HTTP 200 for success. The agent does not retry on failure in the current implementation.

## Security

- Consider adding a shared secret header: `X-Agent-Secret: <token>`
- In production, run n8n behind a reverse proxy with HTTPS
