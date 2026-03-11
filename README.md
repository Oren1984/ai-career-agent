# AI Career Agent — V1

AI-assisted job hunting system that discovers, scores, and surfaces high-match job opportunities from Israeli and global sources.

The system collects job listings from multiple sources (Israeli job boards, RSS feeds, or mock demo data), scores them against a candidate profile using keyword and semantic matching, and provides a Streamlit dashboard for browsing and manual tracking.

This project is a **decision-support system**. The user remains in control of every application decision.

---

## What is the V1 Platform

V1 adds Israeli job board support (Drushim, AllJobs) as first-class sources alongside the existing RSS and mock collectors. The architecture is:

```
Sources → Collectors → Normalizer (dedup) → SQLite
                                               |
                            CombinedScorer (keyword + semantic)
                                               |
                              Streamlit Dashboard (V1)
                         [Jobs | Analytics | Candidate Profile]
```

Source modes available:
- **mock** — hardcoded demo jobs (always works, no network required)
- **rss** — RSS feeds (We Work Remotely, RemoteOK, etc.)
- **israel** — Israeli job boards (Drushim.co.il, AllJobs.co.il; currently mock-safe until real scraping is implemented)
- **all** — all enabled sources from `config/sources.yaml`

---

## Quick Start (Recommended V1 Flow)

```bash
pip install -r requirements.txt

# One-shot demo: init DB, fetch Israeli jobs, score, print dashboard URL
python scripts/run_v1_demo.py

# Launch the dashboard
streamlit run dashboard/streamlit_app.py
```

Dashboard available at: http://localhost:8501

---

## Source Modes

### Mock (always works)
```bash
python scripts/fetch_jobs.py --mode mock
```

### RSS (requires network)
```bash
python scripts/fetch_jobs.py --mode rss
```

### Israeli Sources (Drushim + AllJobs)
```bash
python scripts/fetch_jobs.py --mode israel
```
Currently returns demo data. Real HTTP scraping is planned — see `app/collectors/israel/`.

### All enabled sources
```bash
python scripts/fetch_jobs.py --mode all
```

---

## Dashboard Overview

The dashboard at `dashboard/streamlit_app.py` has three tabs:

- **Jobs** — browse all jobs with filters by status and match level; view job details with score breakdown and AI analysis
- **Analytics** — jobs by source, match level distribution, high-match ratio
- **Candidate Profile** — shows your profile summary, target roles, skills, and projects

### Sidebar Quick Actions

| Button | What it does |
|---|---|
| Fetch Mock Jobs | Loads hardcoded demo jobs (no network) |
| Fetch RSS Jobs | Fetches from RSS feeds |
| Fetch Israeli Jobs | Fetches from Drushim + AllJobs |
| Score Jobs | Scores all unscored jobs |
| Reset Demo State | Drops and recreates DB, fetches Israeli demo jobs, scores them |

The current source mode is shown in the sidebar. Override with the `SOURCE_MODE` environment variable.

---

## Configuration

### Candidate Profile

Edit these files to match your background:

- `config/profile.yaml` — target roles, positive/negative keywords
- `data/candidate_profile/summary.txt` — free-text professional summary
- `data/candidate_profile/skills.json` — skills by category
- `data/candidate_profile/projects.json` — recent projects

### Source Registry

`config/sources.yaml` — enable/disable sources, add company slugs for Greenhouse/Lever, configure Israeli source queries.

### LLM Provider (optional)

```bash
# Demo mode (default — no API key needed)
LLM_PROVIDER=mock

# Real provider examples
LLM_PROVIDER=claude   ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai   OPENAI_API_KEY=sk-...
LLM_PROVIDER=gemini   GOOGLE_API_KEY=AIza...
LLM_PROVIDER=ollama   # Ollama running locally on port 11434
```

### Scheduling (optional)

```bash
pip install apscheduler>=3.10.0

# One-shot run
python scripts/run_scheduler.py --once

# Background scheduler (collects + scores every 6 hours)
python scripts/run_scheduler.py
```

---

## What is Future-Ready (not yet live)

| Feature | Status |
|---|---|
| Drushim real scraping | Planned — collector returns demo data |
| AllJobs real scraping | Planned — collector returns demo data |
| Gmail / email notifications | Config ready (`config/notifications.yaml`) |
| n8n / webhook integration | Architecture ready |
| Slack / Telegram notifications | Config ready |
| LinkedIn / Indeed | Manual reference only (ToS restrictions) |

---

## Project Structure

```
app/
  collectors/
    israel/           # Drushim, AllJobs, and other Israeli collectors
    greenhouse_collector.py
    lever_collector.py
    rss_collector.py
    mock_collector.py
    source_loader.py  # reads config/sources.yaml
  db/                 # SQLAlchemy models, session, normalizer
  filtering/          # FilterEngine (keyword pass/fail)
  matching/           # Scorer, SemanticScorer, CombinedScorer
  services/           # JobService (orchestration, analytics)
  llm/                # LLM provider layer (Claude, OpenAI, Gemini, Ollama, mock)
  candidate/          # CandidateProfile, load_candidate_profile()
  scheduler/          # APScheduler-based background scheduler
  notifications/      # Email, Slack, Telegram, file notifiers

config/
  sources.yaml        # Source registry
  profile.yaml        # Candidate keywords and target roles
  schedule.yaml       # Scheduler config

dashboard/
  streamlit_app.py    # V1 Streamlit dashboard

scripts/
  init_db.py          # Initialize DB
  fetch_jobs.py       # Fetch jobs (--mode mock/rss/israel/all)
  score_jobs.py       # Score all unscored jobs
  reset_demo_state.py # Drop DB, fetch, score in one step
  run_v1_demo.py      # One-shot V1 demo entrypoint
  run_scheduler.py    # Scheduler CLI

data/
  jobs.db             # SQLite database
  candidate_profile/  # summary.txt, skills.json, projects.json

tests/                # pytest test suite
docs/                 # Architecture docs
```

---

## Tech Stack

- Python 3.11+
- Streamlit (dashboard)
- SQLite via SQLAlchemy (database)
- Docker (containerization)
- BeautifulSoup + feedparser (RSS collection)
- APScheduler (optional scheduling)
- anthropic / openai / google-generativeai (optional LLM providers)
- sentence-transformers (optional embedding scoring)

---

## Important Design Principle

This system **does not automatically submit job applications**.

It does NOT implement:
- Automatic CV sending
- Browser automation for applying
- CAPTCHA solving

The agent surfaces opportunities and explains why they match your profile. You decide what to apply to.

---

## Documentation

| File | Description |
|---|---|
| `docs/V1_RUNTIME_ALIGNMENT_REPORT.md` | V1 runtime alignment changes |
| `docs/V3_ARCHITECTURE.md` | Full architecture reference |
| `docs/LLM_CONFIGURATION.md` | LLM provider setup guide |
| `docs/CANDIDATE_PROFILE.md` | Candidate profile file reference |
