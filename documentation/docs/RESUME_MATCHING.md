# Resume Matching

## Overview

The resume matching pipeline extracts structured candidate data from a PDF resume and stores it in `data/candidate_profile/`. This data is then used by the scoring system to personalize job matching.

## Script

**File:** `scripts/parse_resume.py`

```bash
python scripts/parse_resume.py resume.pdf
python scripts/parse_resume.py resume.pdf --dry-run
python scripts/parse_resume.py resume.pdf --output-dir data/candidate_profile
```

## Pipeline

1. **Extract text** from PDF
   - Tries `pypdf` first
   - Falls back to `pdfminer.six`
   - Raises RuntimeError with install instructions if neither is available

2. **Structure the data**
   - If an LLM provider is configured (not mock): uses LLM to extract structured JSON
   - Otherwise: keyword-based fallback extraction from `_TECH_KEYWORDS`

3. **Write profile files**
   - `data/candidate_profile/summary.txt` — 2-3 sentence professional summary
   - `data/candidate_profile/skills.json` — skills by category (ai_ml, python, cloud_infra, data, tools)

## Output Format

`summary.txt`:
```
Python developer with 4 years experience building AI-powered applications.
Strong background in LLM integration, RAG pipelines, and MLOps.
```

`skills.json`:
```json
{
  "ai_ml": ["LLM", "RAG", "MLOps", "PyTorch"],
  "python": ["Python", "FastAPI", "SQLAlchemy"],
  "cloud_infra": ["AWS", "Docker", "Terraform"],
  "data": ["SQL", "PostgreSQL"],
  "tools": ["Git", "GitHub Actions"]
}
```

## Dependencies

| Library | Role | Required? |
|---------|------|-----------|
| pypdf | PDF text extraction | Optional (one of two) |
| pdfminer.six | PDF text extraction fallback | Optional (one of two) |

Install at least one:
```bash
pip install pypdf>=4.0.0
# or
pip install pdfminer.six>=20221105
```

## Integration with Scoring

The `CandidateProfile` class (`app/candidate/profile_loader.py`) loads:
- `summary.txt` → used as profile description for embedding comparison
- `skills.json` → used to augment keyword matching

In `CombinedScorer(semantic_mode="embeddings")`, the profile text is embedded and compared to each job description for cosine similarity scoring.

## Fallback Behavior

If no PDF library is installed:
- `extract_pdf_text()` raises `RuntimeError` with clear install instructions

If LLM extraction fails:
- Falls back to keyword scanning via `_TECH_KEYWORDS`
- No data is lost — the pipeline always produces output

If the output directory doesn't exist:
- Created automatically with `mkdir(parents=True, exist_ok=True)`
