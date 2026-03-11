# Candidate Profile Guide — AI Career Agent V2

## Overview

The candidate profile layer allows the system to understand who you are beyond
simple keyword lists. It powers:
- Semantic theme matching (which areas of your background match the job)
- LLM analysis prompts (richer context for AI-powered job analysis)
- Dashboard profile display tab

---

## Profile Files

All files live in `data/candidate_profile/` and are optional.
Missing files are silently skipped.

### `summary.txt` — Free-text professional summary

```
Applied AI Engineer with 3+ years building LLM-powered applications.
Strong background in Python, FastAPI, Docker, and AWS.
Focused on RAG systems, MLOps pipelines, and AI deployment.
Looking for remote roles in AI/ML engineering or MLOps.
```

### `skills.json` — Structured skills by category

```json
{
  "ai_ml": ["LLM", "RAG", "Embeddings", "Fine-tuning", "Prompt Engineering"],
  "python": ["Python", "FastAPI", "Pydantic", "SQLAlchemy", "PyTest"],
  "cloud_infra": ["AWS", "Terraform", "Docker", "GitHub Actions", "CI/CD"],
  "data": ["SQL", "PostgreSQL", "Data Pipelines"],
  "tools": ["Git", "Linux", "REST APIs"]
}
```

Format: dict of `category_name → list of skill strings`.
A flat list `["Python", "Docker", ...]` is also accepted.

### `projects.json` — Recent projects

```json
[
  {
    "name": "RAG Customer Support Bot",
    "description": "Built a RAG system using LangChain and OpenAI. Deployed on AWS via FastAPI.",
    "technologies": ["Python", "LangChain", "OpenAI", "FastAPI", "Docker", "AWS"]
  }
]
```

Fields: `name` (string), `description` (string), `technologies` (list of strings).
All fields are optional within each project object.

---

## Keyword Config (`config/profile.yaml`)

This file is read first and provides keyword-based matching rules.
The candidate profile loader also reads it to populate `target_roles`,
`positive_keywords`, and `negative_keywords`.

```yaml
target_roles:
  - Applied AI Engineer
  - MLOps Engineer
  - AI Engineer

positive_keywords:
  - python
  - ai
  - ml
  - docker
  - fastapi
  - terraform
  - aws
  - llm
  - rag

negative_keywords:
  - phd
  - senior
  - principal
  - relocation
```

---

## CandidateProfile Object

The `load_candidate_profile()` function returns a `CandidateProfile` dataclass:

```python
from app.candidate.profile_loader import load_candidate_profile

profile = load_candidate_profile()

print(profile.summary)           # str
print(profile.target_roles)      # list[str]
print(profile.positive_keywords) # list[str]
print(profile.negative_keywords) # list[str]
print(profile.skills)            # dict[str, list[str]]
print(profile.projects)          # list[dict]
print(profile.all_skills)        # flat list[str] from all skill categories

# Build a prompt string for LLM
print(profile.to_prompt_string())
```

---

## Semantic Theme Enrichment

If `profile.positive_keywords` contains skills not already in the built-in
semantic themes, they are automatically added to a "Profile Skills" theme
for semantic scoring. This ensures your custom skills are always considered.

---

## How to Customize

1. Edit `data/candidate_profile/summary.txt` with your actual background.
2. Edit `data/candidate_profile/skills.json` with your real skills.
3. Edit `data/candidate_profile/projects.json` with your actual projects.
4. Edit `config/profile.yaml` to adjust keyword matching rules.

The system will use your updated profile on the next scoring run (or after clicking "Score All" in the dashboard).
