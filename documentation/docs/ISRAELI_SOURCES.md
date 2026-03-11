# Israeli Job Sources

## Overview

The AI Career Agent includes a dedicated Israeli job board collector layer under `app/collectors/israel/`.

## Supported Sources

| Source | Status | Notes |
|--------|--------|-------|
| Drushim.co.il | ENABLED (mock-safe) | Largest Israeli job board. Mock data until real scraping implemented. |
| AllJobs.co.il | ENABLED (mock-safe) | Second-largest. Mock data until scraping implemented. |
| JobNet.co.il | DISABLED / PLANNED | Returns empty list. Placeholder. |
| JobKarov | DISABLED / PLANNED | Returns empty list. Placeholder. |
| JobMaster.co.il | DISABLED / PLANNED | Returns empty list. Placeholder. |
| Jobify360 | DISABLED / PLANNED | Returns empty list. Placeholder. |

## Architecture

All Israeli collectors extend `BaseIsraeliCollector` which itself extends `BaseCollector`.

```
BaseCollector (app/collectors/base.py)
  └── BaseIsraeliCollector (app/collectors/israel/base_israel_collector.py)
        ├── DrushimCollector
        ├── AllJobsCollector
        ├── JobNetCollector  (disabled)
        ├── JobKarovCollector  (disabled)
        ├── JobMasterCollector  (disabled)
        └── Jobify360Collector  (disabled)
```

### BaseIsraeliCollector Interface

```python
class BaseIsraeliCollector(BaseCollector):
    source_name: str         # unique source identifier
    supports_apply_link: bool  # whether source exposes direct apply URL
    requires_auth: bool       # whether source needs login
    country: str = "IL"       # always "IL"

    def fetch_jobs(self) -> list[dict]      # raw HTTP/scraping call
    def normalize_job(self, raw) -> RawJob  # convert raw dict to RawJob
    def collect(self) -> list[RawJob]       # orchestrates fetch → normalize
```

## Configuration

Israeli sources are configured in `config/sources.yaml`:

```yaml
- name: drushim
  enabled: true
  source_type: drushim
  search_query: "python developer"
  max_jobs: 50
```

The `source_loader.py` reads these entries and instantiates the appropriate collector class.

## Mock Behavior

Both `DrushimCollector` and `AllJobsCollector` are **mock-safe**: when `fetch_jobs()` is called, they return hardcoded sample jobs instead of making network requests.

This allows the full pipeline to run in offline/development mode without changes.

## Implementing Real Scraping

Each active collector file contains detailed `TODO` comments in `fetch_jobs()` describing:
1. The target URL pattern
2. HTML parsing approach (BeautifulSoup)
3. Pagination strategy
4. Rate limiting notes

To implement real scraping:
1. Install: `pip install requests beautifulsoup4`
2. Implement the TODO section in `fetch_jobs()`
3. Test with a small `max_jobs` value first
4. Remove or replace the mock return statement

## Legal Note

Scraping any website should respect:
- The site's `robots.txt`
- Terms of Service
- Rate limiting (add `time.sleep(1)` between pages)
- No aggressive crawling

Review each site's ToS before activating real scraping in production.
