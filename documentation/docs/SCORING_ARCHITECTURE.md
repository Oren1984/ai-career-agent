# Scoring Architecture

## Overview

The scoring system evaluates how well a job matches the candidate's profile.
It combines keyword-based rules with optional semantic matching.

## Components

### 1. Scorer (V1 — keyword-based)
**File:** `app/matching/scorer.py`

Rules-based scorer that:
- Adds points for positive keywords found in title + description
- Subtracts points for negative keywords (seniority, relocation)
- Returns `ScoreResult` with match_score, match_level, matched_keywords, rejection_flags

Default weights (from `_DEFAULT_KEYWORD_SCORES`):
- `llm`, `rag`, `mlops`, `ai`, `ml` → +3.0 each
- `python`, `docker`, `fastapi`, `terraform`, `aws` → +2.0 each
- `phd`, `principal` → -3.0 each
- `senior`, `relocation`, `10+ years` → -2.0 each

### 2. SemanticScorer (V2 — theme-based)
**File:** `app/matching/semantic_scorer.py`

Theme-based semantic scorer that:
- Defines theme clusters (e.g., "AI/ML", "Cloud/Infrastructure", "Python Stack")
- Checks if job description covers each theme
- Returns a semantic score 0-10 based on theme coverage
- No external dependencies — pure Python

### 3. EmbeddingScorer (V3 — sentence-transformers)
**File:** `app/matching/embedding_scorer.py`

Embedding-based scorer that:
- Uses sentence-transformers for cosine similarity
- Compares job description embedding to candidate profile embedding
- Returns similarity score 0-1 scaled to 0-10
- Requires: `pip install sentence-transformers>=2.7.0`
- Gracefully disabled if not installed

### 4. CombinedScorer (V2/V3 — recommended)
**File:** `app/matching/combined_scorer.py`

Combines all scorers:
```
final_score = keyword_score + (semantic_score / 10) * SEMANTIC_MAX_BONUS
```

Where `SEMANTIC_MAX_BONUS = 2.0` (semantic can add up to 2 points).

Supports two modes:
- `"themes"` (default): uses SemanticScorer — no dependencies
- `"embeddings"`: uses EmbeddingScorer — falls back to themes if not installed

## Score Thresholds

| Level | Score |
|-------|-------|
| HIGH | ≥ 8.0 |
| MEDIUM | ≥ 4.0 |
| LOW | < 4.0 |

## Usage

```python
from app.matching.combined_scorer import CombinedScorer

scorer = CombinedScorer()         # theme mode (default)
result = scorer.score(job_orm)

print(result.final_score)          # e.g. 10.5
print(result.final_level)          # "high"
print(result.matched_keywords)     # ["python", "llm", "docker"]
print(result.matched_themes)       # ["AI/ML", "Python Stack"]
print(result.explanation)          # human-readable summary
```

## Score Storage

Scores are stored in the `scores` table with both V1 and V2 fields:
- V1: `match_score`, `match_level`, `matched_keywords`, `rejection_flags`
- V2: `keyword_score`, `semantic_score`, `final_score`, `matched_themes`

The `Score.to_dict()` method returns both sets for full backward compatibility.
