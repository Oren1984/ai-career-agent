# Source Strategy — AI Career Agent v1.5

This document explains the source collection strategy: which sources are active, why some are
excluded, and how to add new sources.

---

## Source Registry

Sources are configured in `config/sources.yaml`. The source loader (`app/collectors/source_loader.py`)
reads this file and instantiates appropriate collectors at runtime.

### Source Types

| Type | Description | Auto-collected? |
|---|---|---|
| `mock` | Hardcoded demo jobs for testing | Yes |
| `rss` | RSS/Atom feed URL | Yes |
| `company_page` | Company career page URL | Not in V1.5 |
| `manual_reference` | Site documented for manual browsing only | No |
| `future` | Planned V2 source | No |

---

## Active Sources (V1.5)

### mock
- 15 hardcoded demo jobs
- Always available offline
- Covers full range of match levels (high, medium, low) and rejection scenarios
- Activated by `python scripts/fetch_jobs.py` (default) or **Fetch (Mock)** button

### weworkremotely (RSS)
- URL: `https://weworkremotely.com/categories/remote-programming-jobs.rss`
- Remote programming jobs, updated frequently
- No auth required

### remoteok (RSS)
- URL: `https://remoteok.com/remote-jobs.rss`
- Remote tech jobs, updated frequently
- No auth required

---

## Disabled Sources

### linkedin — manual_reference

LinkedIn is documented as `manual_reference` and will **never** be auto-scraped.

**Why:**
1. LinkedIn's Terms of Service (Section 8.2) explicitly prohibits automated scraping and
   data extraction without express written permission from LinkedIn.
2. The LinkedIn API is available only to approved developer partners and does not provide
   general job search access.
3. Browser automation to bypass LinkedIn protections would violate ToS and expose users
   to account bans.

**What to do instead:**
- Browse LinkedIn manually at https://www.linkedin.com/jobs/
- Copy interesting job descriptions into the system via a future manual-import feature (V2).

### indeed — manual_reference

Indeed has similar ToS restrictions and rate-limiting that make automated collection
unreliable. Documented as `manual_reference`.

---

## Future Sources (V2)

### greenhouse
- Companies using Greenhouse ATS expose public job boards at:
  `https://boards-api.greenhouse.io/v1/boards/{company}/jobs`
- No scraping required — clean JSON API
- Plan: implement `GreenhouseCollector` with a list of target companies

### lever
- Companies using Lever expose:
  `https://api.lever.co/v0/postings/{company}`
- Clean JSON API, similar to Greenhouse
- Plan: implement `LeverCollector`

### hackernews_whoishiring
- Monthly "Who is Hiring?" thread on Hacker News
- Available via Algolia HN API:
  `https://hn.algolia.com/api/v1/search?query=who+is+hiring&tags=story&dateRange=pastMonth`
- Requires comment parser to extract structured job info
- Good source for startup/small company roles

---

## How to Add a New Source

### 1. Add an RSS feed

Edit `config/sources.yaml` and add:
```yaml
- name: my_rss_source
  enabled: true
  source_type: rss
  url: "https://example.com/jobs.rss"
  notes: "Description of this feed"
  priority: 5
```

On next run, `source_loader.py` will include it automatically.

### 2. Add a new collector type

1. Create `app/collectors/my_collector.py` extending `BaseCollector`
2. Implement `collect() -> list[RawJob]`
3. Add a new `source_type` (e.g., `greenhouse`) to `source_loader.py`
4. Add the source entry to `config/sources.yaml`

### 3. Test the collector
```bash
python -c "
from app.collectors.my_collector import MyCollector
jobs = MyCollector().collect()
print(f'Collected {len(jobs)} jobs')
print(jobs[0] if jobs else 'No jobs')
"
```

---

## Loading Sources from Config

```python
from app.collectors.source_loader import load_collectors

# All enabled sources
collectors = load_collectors()

# RSS only
collectors = load_collectors(types=["rss"])

# Mock only (offline demo)
collectors = load_collectors(types=["mock"])

# All sources except mock
collectors = load_collectors(include_mock=False)
```

---

## CLI Usage

```bash
# Mock only (default, offline)
python scripts/fetch_jobs.py

# RSS only
python scripts/fetch_jobs.py --rss

# All enabled sources from sources.yaml
python scripts/fetch_jobs.py --all-sources

# All sources, no mock
python scripts/fetch_jobs.py --all-sources --no-mock
```
