# V2 Architecture — AI Career Agent

## Overview

V2 extends the V1.5 stable architecture with four new capability layers:
- **LLM Provider Layer** — pluggable real AI providers with mock fallback
- **Semantic Matching Layer** — theme-based semantic scoring (no ML dependencies required)
- **Candidate Profile Layer** — structured profile from files, used in scoring and LLM prompts
- **Scheduling Layer** — optional background automation via APScheduler

All V1.5 functionality is preserved. All V2 features are optional or gracefully degrade.

---

## Updated Flow

```
Sources → Collectors → Normalizer → SQLite
                                       ↓
                        ┌─────────────────────────────────┐
                        │         CombinedScorer          │
                        │  ┌──────────┐  ┌─────────────┐ │
                        │  │ Keyword  │  │  Semantic   │ │
                        │  │  Scorer  │  │   Scorer    │ │
                        │  │ (V1.5)   │  │  (themes)   │ │
                        │  └──────────┘  └─────────────┘ │
                        │       ↓              ↓          │
                        │  keyword_score + semantic_bonus │
                        │       = final_score             │
                        └─────────────────────────────────┘
                                       ↓
                              Streamlit Dashboard (V2)
                              ┌────────┬──────────┬────────┐
                              │  Jobs  │Analytics │Profile │
                              └────────┴──────────┴────────┘
```

---

## Module Map

### New in V2

```
app/
├── llm/
│   ├── base.py                  # unchanged ABC
│   ├── mock_provider.py         # unchanged mock
│   ├── provider_factory.py      # NEW: get_provider(), list_providers()
│   └── providers/               # NEW
│       ├── claude_provider.py   # Claude via anthropic SDK
│       ├── openai_provider.py   # OpenAI via openai SDK
│       ├── gemini_provider.py   # Gemini via google-generativeai SDK
│       └── ollama_provider.py   # Local Ollama via HTTP
│
├── matching/
│   ├── scorer.py               # unchanged keyword scorer
│   ├── semantic_scorer.py      # NEW: theme-based semantic matching
│   └── combined_scorer.py      # NEW: merges keyword + semantic
│
├── candidate/
│   ├── __init__.py             # NEW
│   └── profile_loader.py       # NEW: CandidateProfile + load_candidate_profile()
│
└── scheduler/
    ├── __init__.py             # NEW
    └── scheduler.py            # NEW: create_scheduler(), run_once(), is_available()

config/
└── schedule.yaml               # NEW: scheduler configuration

data/
└── candidate_profile/          # NEW: candidate files
    ├── summary.txt
    ├── skills.json
    └── projects.json

scripts/
└── run_scheduler.py            # NEW: CLI entry point for scheduler

docs/
├── V2_ARCHITECTURE.md          # this file
├── LLM_CONFIGURATION.md        # LLM provider setup guide
└── CANDIDATE_PROFILE.md        # profile files reference
```

### Modified in V2

| File | Change |
|---|---|
| `app/db/models.py` | Score model: 5 new nullable columns (keyword_score, semantic_score, final_score, matched_themes, missing_themes) |
| `app/services/job_service.py` | CombinedScorer integration, `get_source_analytics()`, `_build_score_row()` |
| `dashboard/streamlit_app.py` | V2 tabs (Jobs / Analytics / Profile), semantic score display, LLM status |
| `scripts/init_db.py` | V2 migration: ALTER TABLE for new columns on existing DBs |
| `requirements.txt` | Added pandas, apscheduler; LLM SDKs listed as optional comments |

---

## Scoring

### V1 (Keyword Only)
`match_score` = sum of matched keyword weights − sum of negative keyword penalties

### V2 (Combined)
```
keyword_score = V1 match_score
semantic_score = (matched_themes / total_themes) × 10    [0–10]
final_score = keyword_score + (semantic_score / 10) × 2.0

match_level:
  high   if final_score ≥ 8.0
  medium if final_score ≥ 4.0
  low    otherwise
```

Semantic can add up to **+2.0 points** (bonus only — never subtracts).
Rejection flags from keyword scoring still apply fully.

### Semantic Themes (default)
1. AI/ML Engineering
2. LLM Applications
3. Python Development
4. MLOps & Infrastructure
5. Data Engineering
6. API & Backend Development

A theme is "matched" if ≥1 of its keyword list appears in the job text.

---

## LLM Provider Fallback Chain

```
LLM_PROVIDER env var
        ↓
_load_provider(name)
        ↓ if not available (no API key or package)
MockLLMProvider (always available, rule-based)
```

No paid API is ever required. The system always falls back to mock.

---

## Scheduling

APScheduler is an optional dependency. The app functions identically without it.

```bash
pip install apscheduler>=3.10.0

# Run once immediately
python scripts/run_scheduler.py --once

# Run background scheduler (every 6 hours)
python scripts/run_scheduler.py
```

The Streamlit dashboard and scoring pipeline do NOT depend on the scheduler.
