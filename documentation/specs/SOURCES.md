# Source Strategy — AI Career Agent

## Guiding Principles

Prefer lightweight, stable, public APIs.
Avoid aggressive scraping, login-required sources, or ToS violations.
All sources must degrade gracefully — the system always works in demo mode.

---

## V1/V1.5 Sources

| Source | Type | Status | Notes |
|---|---|---|---|
| Mock | mock | Active | Hardcoded demo jobs, always available |
| We Work Remotely | rss | Active | Public RSS feed |
| RemoteOK | rss | Active | Public RSS feed |
| LinkedIn | manual_reference | Disabled | ToS prohibits scraping |
| Indeed | manual_reference | Disabled | ToS + paid API only |

---

## V2.5 Sources (New)

### Greenhouse ATS (`source_type: greenhouse`)

- **API:** `https://boards-api.greenhouse.io/v1/boards/{company}/jobs`
- **Auth:** None required
- **Config:** Add company slugs to `companies:` list in `sources.yaml`
- **Collector:** `app/collectors/greenhouse_collector.py`

To enable:
```yaml
- name: greenhouse
  enabled: true
  source_type: greenhouse
  companies:
    - anthropic
    - openai
    - stripe
```

Find slugs in the board URL: `https://boards.greenhouse.io/{slug}`

### Lever ATS (`source_type: lever`)

- **API:** `https://api.lever.co/v0/postings/{company}`
- **Auth:** None required
- **Config:** Add company slugs to `companies:` list in `sources.yaml`
- **Collector:** `app/collectors/lever_collector.py`

To enable:
```yaml
- name: lever
  enabled: true
  source_type: lever
  companies:
    - netflix
    - github
```

Find slugs in the board URL: `https://jobs.lever.co/{slug}`

### Hacker News "Who is Hiring?" (`source_type: hackernews`)

- **API:** Algolia HN Search API (public, no auth)
- **Story lookup:** `https://hn.algolia.com/api/v1/search?query=Ask+HN:+Who+is+Hiring?&tags=story`
- **Comments:** `https://hn.algolia.com/api/v1/search?tags=comment,story_{id}`
- **Config:** `max_jobs` (default: 100)
- **Collector:** `app/collectors/hackernews_collector.py`

To enable:
```yaml
- name: hackernews_whoishiring
  enabled: true
  source_type: hackernews
  max_jobs: 100
```

**Note:** HN job posts are plain-text comments in inconsistent formats.
Parsing extracts what it can; description quality varies widely.

---

## Permanently Excluded Sources

| Source | Reason |
|---|---|
| LinkedIn | ToS explicitly prohibits automated scraping |
| Indeed | ToS restricts scraping; API requires paid partnership |

These will never be added as automated collectors.

---

## Source Requirements

Each collector must produce `RawJob` objects with:
- `title` (str, required)
- `company` (str)
- `location` (str)
- `description` (str)
- `url` (str)
- `source` (str, unique per source)
- `date_found` (datetime)

## Fallback Requirement

If all real-world sources fail or are disabled, the system falls back to:
- MockCollector (demo mode)
- Empty result set (no crash)
