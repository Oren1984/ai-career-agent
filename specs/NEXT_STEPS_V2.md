# Next Steps — V2.5 and Beyond

V2.0 is complete and stable. This document outlines what remains for future iterations.

---

## Completed in V2.0

- [x] LLM provider layer (Claude, OpenAI, Gemini, Ollama, mock fallback)
- [x] Semantic matching (theme-based, no ML dependencies)
- [x] Combined scorer (keyword + semantic → final_score)
- [x] Candidate profile layer (summary.txt, skills.json, projects.json)
- [x] Scheduling support (APScheduler, run_once, background scheduler)
- [x] Analytics improvements (by_source, by_level, high_match_ratio)
- [x] Dashboard V2 (3 tabs: Jobs, Analytics, Candidate Profile)
- [x] 171 tests, all passing

## Completed in V2.5

- [x] AI Analysis button in job detail panel (user-triggered, cached per job)
- [x] GreenhouseCollector (public ATS API, no auth)
- [x] LeverCollector (public ATS API, no auth)
- [x] HackerNewsHiringCollector (Algolia HN API, no auth)
- [x] source_loader.py updated for greenhouse/lever/hackernews types
- [x] sources.yaml updated with new entries (disabled by default)
- [x] 29 new tests → 200 total, all passing
- [x] SOURCES.md rewritten as SOURCE_STRATEGY.md equivalent

---

## V3 / Future Priorities

### 1. Adzuna API Collector

Public job search API with a free tier. Requires API key (free registration).

**Work:**
- Register at https://developer.adzuna.com
- Implement `AdzunaCollector` in `app/collectors/`
- Add to sources.yaml as `source_type: adzuna`

### 3. Embedding-Based Semantic Similarity

Replace theme-matching with proper vector similarity using lightweight sentence embeddings.

**Options:**
- `sentence-transformers` with a small model (e.g., `all-MiniLM-L6-v2`, ~80MB)
- API-based embeddings (OpenAI, Claude) when provider is available
- Hybrid: use API when available, fall back to theme-based

**Work:**
- Add `EmbeddingSemanticScorer` alongside `SemanticScorer`
- Store job embeddings in DB for fast re-ranking
- Optionally expose embedding model as config option

### 4. Resume Parsing

Allow uploading a PDF or DOCX resume and auto-populate `skills.json` and `summary.txt`.

**Work:**
- Add `scripts/parse_resume.py`
- Use `pdfminer` or `pypdf` for PDF extraction
- Use LLM to extract structured skills from raw text
- Write to `data/candidate_profile/`

### 5. Cover Letter Generation (V3)

Use LLM to draft a tailored cover letter for a selected job.

**Constraints:**
- User must explicitly trigger this — never automatic
- User reviews and edits before use
- No automatic submission

### 6. Email/Slack Notifications

When scheduler runs and finds new high-match jobs, send a notification.

**Work:**
- `app/notifications/` module
- SMTP email (via Python `smtplib`)
- Slack webhook support
- Configurable threshold (e.g., notify only for high-match jobs)

### 7. PostgreSQL Support

The infrastructure exists (DATABASE_URL env var), but V2 was only tested with SQLite.

**Work:**
- Test V2 migrations with PostgreSQL
- Update Docker compose for optional PostgreSQL service
- Document connection string format

### 8. Export Features

Allow exporting job lists to CSV or JSON.

**Work:**
- "Export CSV" button in dashboard
- Filter-aware export (only export currently visible jobs)

### 9. Pagination

Dashboard currently loads all jobs at once, which degrades at scale.

**Work:**
- Limit query to N jobs per page
- Add page controls to sidebar

---

## Permanent Constraints (Will Never Change)

- No automatic job application submission
- No automatic CV or cover letter sending
- No browser automation (Selenium, Playwright)
- No CAPTCHA solving
- No hidden background behavior

The system remains a decision-support tool. The user controls every application action.
