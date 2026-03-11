## This file documents the prompt used to instruct the AI system during development.
## It is stored for documentation and transparency of how parts of the project were generated.


## You are the implementation agent for this repository.

## Read and use these files as the source of truth before writing code:

1. README.md
2. PROJECT_SPEC.md
3. CLAUDE_INSTRUCTIONS.md
4. TEST_PLAN.md
5. config/profile.yaml

## Your mission is to build Version 1 of this project as a modular, lightweight, Dockerized AI-assisted job hunting system.

Important:
This version is strictly a decision-support system.
It MUST NOT automatically submit job applications.
It MUST NOT implement browser automation for applying.
It MUST NOT implement CAPTCHA solving.
It MUST NOT send CVs automatically.

You should not stop after planning.
You should proceed end-to-end and implement the project in working stages until there is a runnable MVP in the repository.

## High-level goal

Build a local modular system that:

- collects jobs from simple sources
- normalizes and stores them in SQLite
- filters and scores them against the candidate profile
- explains why a job matches or does not match
- shows the results in a Streamlit dashboard
- supports manual status tracking

## Delivery mode

Work continuously in implementation mode.
Do not stop after each phase.
Do not ask for confirmation unless there is a true blocker.
If something is missing, make a reasonable engineering decision and continue.
Keep everything lightweight and practical.

## What to build

### 1. Project structure
Create and organize the codebase under folders such as:

- app/collectors
- app/filtering
- app/matching
- app/db
- app/services
- app/llm
- dashboard
- tests

### 2. Database
Implement SQLite support.

Create tables for at least:

- jobs
- scores
- status history

Each job should include fields like:

- id
- title
- company
- location
- source
- url
- description
- raw_text
- date_found
- unique_hash
- status

### 3. Collectors
Implement at least one or two simple collectors that are realistic and lightweight.

Preferred order:
- RSS-based collector
- simple company careers page parser
- mock/demo local collector if needed for stable testing

If live sources are unreliable, create a stable mock source layer so the system can still be demonstrated and tested.

### 4. Normalization and deduplication
Normalize collected jobs into one consistent schema.
Prevent duplicate insertion using a unique hash strategy.

### 5. Filter engine
Implement rules-based filtering using the keywords from config/profile.yaml.

Support:
- positive keyword matching
- negative keyword flags
- simple role/category identification

### 6. Match engine
Implement a scoring engine based on explicit rules.

It should return at least:
- numeric match_score
- match_level (high / medium / low)
- matched_keywords
- missing_keywords
- rejection_flags
- explanation

The explanation should be readable and useful.

### 7. Streamlit dashboard
Build a simple but clean dashboard that shows:

- total jobs
- high / medium / low matches
- filters by status, company, score, role, text
- a list/table of jobs
- detailed view for a selected job
- explanation text
- manual status update options:
  - new
  - reviewing
  - saved
  - ignored
  - applied_manual

### 8. Services and scripts
Provide runnable scripts or entry points for:

- initialize database
- fetch jobs
- score jobs
- run dashboard

### 9. Docker
Make the project runnable in Docker.

Ensure the dashboard starts correctly from Docker Compose.

### 10. Tests
Implement pytest tests for:
- job parsing
- duplicate detection
- filter logic
- scoring logic
- database persistence
- basic dashboard startup sanity if practical

### 11. Logging and reporting
Add basic logging.
At the end, generate a final implementation summary report in markdown.

Create a file named:

FINAL_IMPLEMENTATION_REPORT.md

It should include:
- what was implemented
- architecture summary
- files created
- limitations
- how to run
- test summary
- next recommended improvements

Also create:

TEST_RESULTS.md

with:
- tests created
- pass/fail summary
- notable coverage areas

## Engineering rules

- Prefer simple, robust solutions over fancy abstractions
- Keep dependencies minimal
- Keep the code readable and modular
- Use Python 3.11 style
- Use SQLAlchemy or a simple DB layer consistently
- Use type hints where practical
- Avoid overengineering
- Avoid complex agent orchestration in V1
- Keep the llm/ layer as a future-ready interface only; do not make the project depend on paid APIs

## Architecture rules

Version 1 must remain:

- local-first
- lightweight
- modular
- rules-based
- ready for future LLM providers

The llm layer should contain only a clean abstraction and mock/provider placeholders if useful.

## Working style

Execute in this order, without stopping unless blocked:

1. inspect repository files
2. create/complete structure
3. implement database
4. implement collectors
5. implement normalization/dedup
6. implement filtering
7. implement scoring
8. implement dashboard
9. implement tests
10. verify Docker
11. write final reports

## Important instruction

Do not only describe what you will do.
Actually create the files and implement the code.
Do not end with a plan only.
Do the work.

When finished, provide a concise completion summary pointing to:
- main modules
- how to run
- what tests exist
- what remains for V2