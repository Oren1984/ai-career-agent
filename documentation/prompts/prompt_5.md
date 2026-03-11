## This file documents the prompt used to instruct the AI system during development.
## It is stored for documentation and transparency of how parts of the project were generated.

## You are implementing the final V3 upgrade of the AI Career Agent project.

## The system is currently at Version 2.5 and fully stable:
- 200 tests passing
- Job collectors working
- Dashboard working
- AI analysis implemented
- Scheduler optional
- Source-based collectors (RSS + Greenhouse + Lever + HackerNews)

Your task is to implement the final Version 3 upgrade.

This is the LAST version of the system. After V3 the architecture will be considered complete.

Do not break any existing functionality.

All existing tests must continue to pass.

The system must remain lightweight and runnable locally.

--------------------------------------------------
V3 FEATURES TO IMPLEMENT
--------------------------------------------------

Implement exactly three new capabilities:

1) Embedding-based semantic matching
2) Resume parsing
3) Job notifications

No additional features should be introduced.

--------------------------------------------------
1. EMBEDDING SEMANTIC MATCHING
--------------------------------------------------

Replace the current theme-based semantic scoring with optional embedding-based similarity.

Use sentence-transformers.

# Recommended model:

all-MiniLM-L6-v2

## Requirements:

- Create module:

app/matching/embedding_scorer.py

- Use cosine similarity between:
  candidate profile embedding
  job description embedding

- Candidate embedding built from:

profile.summary
profile.skills
profile.projects

- Job embedding built from:

title + description

- Use caching so embeddings are not recomputed unnecessarily.

- Maintain compatibility with existing scoring:

CombinedScorer must support two modes:

semantic_mode = "themes"
semantic_mode = "embeddings"

Default remains themes if sentence-transformers is not installed.

Embedding scoring output:

semantic_score
semantic_similarity
matched_themes (optional)

Embedding score should remain compatible with existing final_score calculation.

--------------------------------------------------
2. RESUME PARSING
--------------------------------------------------

Allow the user to upload a PDF resume and automatically extract candidate information.

Create script:

scripts/parse_resume.py

## Libraries allowed:

pypdf
pdfminer.six

## Process:

1) Extract raw text from PDF
2) Use the LLM provider (if available) to structure data into:

skills
technologies
experience summary
keywords

3) Write structured data into:

data/candidate_profile/skills.json
data/candidate_profile/summary.txt

Add a command:

python scripts/parse_resume.py resume.pdf

The system should update candidate profile files automatically.

If no LLM provider is configured, fall back to keyword extraction.

--------------------------------------------------
3. JOB NOTIFICATIONS
--------------------------------------------------

Implement optional notifications when high-match jobs are discovered.

Create module:

app/notifications/

## Supported channels:

email
slack webhook
telegram bot

## Behavior:

When scheduler runs and new jobs with match_level = "high" appear:

## send notification message containing:
- job title
- company
- match score
- source
- job link

Config file:

config/notifications.yaml

Example:

email:
  enabled: false
  smtp_server:
  smtp_user:
  smtp_password:

slack:
  enabled: false
  webhook_url:

telegram:
  enabled: false
  bot_token:
  chat_id:

Notifications must only trigger once per job.

--------------------------------------------------
TESTING
--------------------------------------------------

Add tests for:

embedding scorer
resume parsing
notification triggers

All existing tests must pass.

Total tests should increase beyond current test count.

--------------------------------------------------
DOCUMENTATION
--------------------------------------------------

Update documentation:

README.md
FINAL_IMPLEMENTATION_REPORT.md
TEST_RESULTS.md
KNOWN_LIMITATIONS.md

Add new document:

docs/V3_ARCHITECTURE.md

Explain:

embedding scoring
resume parsing workflow
notification system
resource usage

--------------------------------------------------
FINAL STATE (SUCCESS CRITERIA)
--------------------------------------------------

V3 is considered complete when:

- all tests pass
- embedding scoring works
- resume parsing works
- notifications work
- dashboard remains stable
- collectors remain stable
- system runs locally

After this implementation the system should be labeled:

AI Career Agent V3 — Final Architecture