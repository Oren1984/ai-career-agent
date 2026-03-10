# Known Limitations — AI Career Agent V2

---

## 1. Job Collection Limitations

- RSS feed availability is volatile — feeds may be unavailable or change structure
- Job description extraction is best-effort — HTML stripping may miss structured content
- Full job descriptions rarely available via RSS (snippets only)
- Mock data is hardcoded — not real jobs
- LinkedIn and Indeed not scraped (ToS violations — intentional exclusion)
- No Greenhouse/Lever/HN integration yet (planned for V2.5)

---

## 2. Semantic Matching Limitations

- Theme-based semantic scoring uses keyword substring matching, not true NLP
- Synonyms and paraphrases not handled (e.g., "machine learning" ≠ "ML" unless both listed)
- Theme vocabulary is static — requires manual updates when technology landscape changes
- Semantic score only measures theme coverage, not contextual relevance
- No true embedding-based similarity (sentence-transformers not used — avoids ML dependencies)
- Semantic bonus is capped at +2.0 points — may not differentiate strongly matched jobs

---

## 3. LLM Provider Limitations

- LLM analysis is not yet displayed in the job detail panel UI (groundwork laid, V2.5)
- All providers use the same generic prompt — no provider-specific optimization
- No token budget control for very long job descriptions (truncated at 2000 chars)
- Ollama availability check uses a 3-second timeout — slow networks may cause false negatives
- No retry logic for API failures — single attempt per call
- No response caching — LLM calls are made fresh each time

---

## 4. Candidate Profile Limitations

- Profile files are examples — must be edited to reflect the actual candidate
- Skills are compared as exact substrings — skill aliases not resolved
- Projects not currently used in scoring (loaded but only displayed in dashboard)
- No resume parsing — user must manually fill `skills.json` and `summary.txt`
- No integration with LinkedIn profiles or CV files

---

## 5. Scheduling Limitations

- APScheduler is optional — must be installed separately
- No job_store persistence — scheduler state lost on restart; missed jobs not replayed
- No alerting or notification on scheduler failures
- Cron expressions require manual configuration — no UI for scheduling
- Scheduler not integrated into Docker compose — runs as separate process

---

## 6. Database Limitations

- SQLite only — single writer, not suitable for multi-user or production scale
- V2 migration uses `ALTER TABLE` — safe for SQLite, not tested with PostgreSQL
- No data retention policy — old jobs accumulate indefinitely
- No export (CSV, JSON) — view and filter only

---

## 7. Dashboard Limitations

- Single-user only — no authentication
- Streamlit reruns entire page on every interaction
- No pagination — all matching jobs loaded at once (performance degrades at scale)
- No export to CSV or other formats
- Candidate Profile tab displays sample data — user must edit profile files to see real data
- Bar chart requires `pandas` (added in V2) — fails gracefully if not installed

---

## 8. Permanent Design Constraints (Will NOT Change)

These are intentional design decisions:

- **No automatic job applications** — system is decision-support only
- **No CV sending** — user controls every application submission
- **No browser automation** — no Selenium, Playwright, or similar tools
- **No CAPTCHA solving**
- **No hidden or background data submission**

---

## 9. Python Version

- Python 3.10+ required (uses `X | Y` union type hints)
- Tested with Python 3.11
