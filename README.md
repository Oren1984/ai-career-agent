# AI Career Agent — V3

AI-assisted job hunting system that discovers, scores, and alerts you to high-match job opportunities.

The system collects job listings from multiple sources, scores them against a candidate profile using keyword and semantic matching, and provides a Streamlit dashboard for browsing and manual tracking.

This project is a **decision-support system**. The user remains in control of every application decision.

---

## What's New in V3

- **Embedding-Based Semantic Matching** — sentence-transformers `all-MiniLM-L6-v2` for cosine similarity scoring; graceful fallback to theme-based scoring when not installed
- **Resume Parser** — `scripts/parse_resume.py` extracts text from PDF resumes and writes structured candidate profile files; LLM-assisted or keyword fallback
- **Job Notifications** — email (SMTP), Slack (Incoming Webhook), and Telegram (Bot API) alerts for new high-match jobs; each job notified at most once

---

## What Was Added in V2

- **LLM Provider Layer** — Claude, OpenAI, Gemini, Ollama support with mock fallback
- **Semantic Matching** — theme-based scoring alongside keyword rules
- **Combined Score** — `keyword_score + semantic_bonus = final_score`
- **Candidate Profile Layer** — structured profile files drive matching and LLM prompts
- **Scheduling Support** — optional APScheduler-based background automation
- **Analytics Tab** — jobs by source, by match level, high-match ratio
- **Profile Tab** — candidate summary, skills, and projects displayed in dashboard
- **New Collectors** — Greenhouse, Lever, HackerNews "Who is Hiring?" (all optional)
- **AI Analysis Button** — per-job LLM analysis in the dashboard detail panel

---

## Features

- Job collection from RSS feeds, mock data, Greenhouse, Lever, and HackerNews
- Configurable source registry (`config/sources.yaml`)
- Rules-based keyword scoring with weighted positive/negative keywords
- Semantic scoring — theme-based (default) or embedding-based (optional)
- Combined final score with explainable output
- Candidate profile from structured files (`data/candidate_profile/`)
- Resume parser with PDF extraction and LLM/keyword-based skill extraction
- Streamlit dashboard with 3 tabs: Jobs, Analytics, Candidate Profile
- Per-job LLM analysis button (cached in session)
- Job notifications via email, Slack, and Telegram (deduplication included)
- Manual status tracking (new → reviewing → saved → applied_manual)
- Status history log
- Docker support
- Full test suite (283 tests)

---

## Architecture

```
Sources → Collectors → Normalizer (dedup) → SQLite
                                               ↓
                            CombinedScorer (keyword + semantic)
                              ├── SemanticScorer (themes, default)
                              └── EmbeddingScorer (sentence-transformers, optional)
                                               ↓
                              Streamlit Dashboard (V3)
                         [Jobs | Analytics | Candidate Profile]
                                               ↓
                              Notifier (email / Slack / Telegram)
```

---

## Quick Start

### Docker (recommended)

```bash
docker compose up
```

Dashboard available at: http://localhost:8501

### Local

```bash
pip install -r requirements.txt
python scripts/init_db.py
python scripts/fetch_jobs.py --mock
python scripts/score_jobs.py
streamlit run dashboard/streamlit_app.py
```

---

## Configuration

### Candidate Profile

Edit these files to match your actual background:

- `config/profile.yaml` — target roles, positive/negative keywords
- `data/candidate_profile/summary.txt` — free-text professional summary
- `data/candidate_profile/skills.json` — skills by category
- `data/candidate_profile/projects.json` — recent projects

Or parse your resume automatically:

```bash
python scripts/parse_resume.py your_resume.pdf
```

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

### Embedding-Based Scoring (optional)

```bash
pip install sentence-transformers>=2.6.0
```

The first run downloads `all-MiniLM-L6-v2` (~90 MB). Subsequent runs use the local cache.
Enable in code via `CombinedScorer(semantic_mode="embeddings")`.

### Notifications

Edit `config/notifications.yaml`:

```yaml
notifications:
  email:
    enabled: true
    smtp_server: smtp.gmail.com
    smtp_port: 587
    smtp_user: "you@gmail.com"
    smtp_password: "your-app-password"
    recipient: ""       # defaults to smtp_user

  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/..."

  telegram:
    enabled: true
    bot_token: "123456:ABC..."
    chat_id: "your-chat-id"
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

## Tech Stack

- Python 3.11+
- Streamlit (dashboard)
- SQLite via SQLAlchemy (database)
- Docker (containerization)
- BeautifulSoup + feedparser (RSS collection)
- APScheduler (optional scheduling)
- anthropic / openai / google-generativeai (optional LLM providers)
- sentence-transformers (optional embedding scoring)
- pypdf / pdfminer.six (optional resume parsing)

---

## Important Design Principle

This system **does not automatically submit job applications**.

It does NOT implement:
- Automatic CV sending
- Browser automation for applying
- CAPTCHA solving

The agent surfaces opportunities and explains why they match your profile.
You decide what to apply to.

---

## Documentation

| File | Description |
|---|---|
| `docs/V3_ARCHITECTURE.md` | Full V3 architecture and module map |
| `docs/V2_ARCHITECTURE.md` | V2 architecture reference |
| `docs/LLM_CONFIGURATION.md` | LLM provider setup guide |
| `docs/CANDIDATE_PROFILE.md` | Candidate profile file reference |
| `FINAL_IMPLEMENTATION_REPORT.md` | Implementation report |
| `KNOWN_LIMITATIONS.md` | Known limitations and constraints |
