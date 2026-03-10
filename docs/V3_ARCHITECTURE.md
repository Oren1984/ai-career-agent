# AI Career Agent — V3 Architecture

## Overview

V3 adds three major capabilities on top of the V2.5 foundation:

1. **Embedding-based semantic matching** — cosine similarity via sentence-transformers
2. **Resume parser** — PDF extraction + LLM/keyword fallback → candidate profile files
3. **Job notifications** — email/Slack/Telegram with per-job deduplication

The V1/V2 core (collectors, normalizer, keyword scorer, SQLite, dashboard) is unchanged.

---

## Module Map

```
app/
├── collectors/          # Job sources (unchanged from V2.5)
│   ├── base_collector.py
│   ├── mock_collector.py
│   ├── rss_collector.py
│   ├── greenhouse_collector.py
│   ├── lever_collector.py
│   ├── hackernews_collector.py
│   └── source_loader.py
│
├── db/                  # SQLAlchemy models + session (unchanged)
│   ├── models.py
│   ├── session.py
│   └── normalizer.py
│
├── filtering/           # FilterEngine (unchanged)
│
├── matching/            # Scoring layer (V3 additions)
│   ├── scorer.py            # V1 keyword scorer
│   ├── semantic_scorer.py   # V2 theme-based scorer
│   ├── embedding_scorer.py  # V3 embedding scorer (new)
│   └── combined_scorer.py   # V3 updated — supports both modes
│
├── notifications/       # V3 notification system (new)
│   ├── notifier.py          # Notifier orchestrator
│   └── channels/
│       ├── base_channel.py
│       ├── email_channel.py
│       ├── slack_channel.py
│       └── telegram_channel.py
│
├── candidate/           # Profile loader (V2, unchanged)
├── llm/                 # LLM providers (V2, unchanged)
├── scheduler/           # APScheduler wrapper (V2, unchanged)
└── services/            # JobService (V2, unchanged)

scripts/
├── init_db.py
├── fetch_jobs.py
├── score_jobs.py
├── run_scheduler.py
└── parse_resume.py      # V3 resume parser (new)

config/
├── profile.yaml
├── sources.yaml
├── schedule.yaml
└── notifications.yaml   # V3 (new)

data/
├── jobs.db
├── notifications_sent.json   # V3 deduplication log (new)
└── candidate_profile/
    ├── summary.txt
    ├── skills.json
    └── projects.json
```

---

## Embedding Scorer (`app/matching/embedding_scorer.py`)

### Design

- Uses `sentence-transformers` library with model `all-MiniLM-L6-v2`
- Optional dependency — `is_available()` returns False when not installed
- Model is loaded lazily on first `score()` call
- Profile embedding is computed once and cached in `_profile_embedding`
- Job text = `"{title} {description}"` concatenated
- Similarity = dot product of L2-normalized embeddings (= cosine similarity)
- `semantic_score = clamp(similarity, 0, 1) * 10.0`

### Data flow

```python
EmbeddingScorer(profile_text="Python AI Engineer")
    .score(job)           # accepts Job ORM object
    .score_text(title, description)  # accepts raw strings
→ EmbeddingScoreResult(
    semantic_score=7.4,       # 0.0–10.0
    semantic_similarity=0.74, # 0.0–1.0
    matched_themes=[],        # always empty (embeddings don't use themes)
    missing_themes=[],
)
```

### Resource usage

- Model download: ~90 MB (one time, cached in `~/.cache/huggingface/`)
- Inference: ~5–20 ms per job on CPU (MiniLM is very fast)
- Memory: ~100 MB loaded model

---

## CombinedScorer V3 (`app/matching/combined_scorer.py`)

### Modes

| Mode | Setting | Requires |
|------|---------|---------|
| `"themes"` | Default | Nothing |
| `"embeddings"` | `semantic_mode="embeddings"` | `sentence-transformers` |

If `semantic_mode="embeddings"` is requested but `sentence-transformers` is not installed, the scorer silently falls back to `"themes"` mode.

### Score formula

```
final_score = keyword_score + (semantic_score / 10.0) * 2.0
```

- `keyword_score`: 0.0–10.0 from `Scorer`
- `semantic_score`: 0.0–10.0 from `SemanticScorer` or `EmbeddingScorer`
- `final_score`: uncapped (max ≈ 12.0 in theory; high threshold is 8.0)

### CombinedScoreResult V3 additions

```python
@dataclass
class CombinedScoreResult:
    ...
    semantic_similarity: float | None   # set when using embeddings mode
    semantic_mode: str                  # "themes" or "embeddings"
```

---

## Resume Parser (`scripts/parse_resume.py`)

### Pipeline

```
PDF file
    ↓
extract_pdf_text()
    ├── extract_text_pypdf()    # preferred
    └── extract_text_pdfminer() # fallback if pypdf fails or returns empty
    ↓
Raw text
    ↓
extract_with_llm()             # if LLM provider configured (non-mock)
    └── Returns JSON: {summary, skills, keywords}
    OR
keyword fallback
    ├── extract_keywords_fallback()   # regex scan for tech keywords
    └── build_summary_fallback()      # first long lines of text
    ↓
write_profile_files()
    ├── data/candidate_profile/summary.txt
    └── data/candidate_profile/skills.json
```

### CLI usage

```bash
# Basic
python scripts/parse_resume.py resume.pdf

# Custom output directory
python scripts/parse_resume.py resume.pdf --output-dir data/candidate_profile

# Dry run (no files written)
python scripts/parse_resume.py resume.pdf --dry-run

# Verbose
python scripts/parse_resume.py resume.pdf --verbose
```

### Keyword categories

The fallback extractor detects these categories from resume text:

| Category | Examples |
|----------|---------|
| `ai_ml` | LLM, RAG, PyTorch, embeddings, fine-tuning |
| `python` | Python, FastAPI, Django, numpy, pandas |
| `cloud_infra` | AWS, Docker, Kubernetes, Terraform |
| `data` | SQL, PostgreSQL, Spark, Kafka, dbt |
| `tools` | git, Linux, REST API, microservices |

---

## Notifications (`app/notifications/`)

### Architecture

```
Notifier
    ├── loads config/notifications.yaml
    ├── loads data/notifications_sent.json (already-notified job IDs)
    ├── builds active channels: [EmailChannel, SlackChannel, TelegramChannel]
    │
    └── notify_new_high_matches(session)
            ├── JobService.get_jobs_with_scores(match_level_filter="high")
            ├── filters out already-notified IDs
            ├── for each new job:
            │   ├── _format_message(job) → (subject, body)
            │   └── channel.send(subject, body, job) for each channel
            └── saves updated sent IDs to notifications_sent.json
```

### Channel interface

Each channel implements:

```python
class BaseChannel(ABC):
    channel_name: str
    def is_configured(self) -> bool: ...
    def send(self, subject: str, body: str, job: dict) -> bool: ...
```

### Deduplication

Sent job IDs are persisted in `data/notifications_sent.json`:

```json
{
  "notified_job_ids": [42, 77, 99]
}
```

A job is never notified twice, even across restarts.

### Channel details

**Email** (`EmailChannel`):
- SMTP with STARTTLS (port 587 default)
- Requires: `smtp_server`, `smtp_user`, `smtp_password`
- Optional: `smtp_port`, `recipient` (defaults to `smtp_user`), `use_tls`

**Slack** (`SlackChannel`):
- POST to Incoming Webhook URL with Block Kit JSON
- Requires: `webhook_url`

**Telegram** (`TelegramChannel`):
- POST to `https://api.telegram.org/bot{token}/sendMessage` with MarkdownV2
- Requires: `bot_token`, `chat_id`

---

## Test Coverage

| Module | Tests | File |
|--------|-------|------|
| EmbeddingScorer | 15 | `tests/test_embedding_scorer.py` |
| Resume parser | 20 | `tests/test_resume_parser.py` |
| Notifications | 25 | `tests/test_notifications.py` |
| V1/V2 modules | 223 | various |
| **Total** | **283** | |

All tests use mocks — no network calls, no real LLM API calls, no real SMTP/webhook calls.
