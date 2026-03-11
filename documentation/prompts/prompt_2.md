## This file documents the prompt used to instruct the AI system during development.
## It is stored for documentation and transparency of how parts of the project were generated.

## You are the implementation agent for this repository.

## Before writing code, read and understand the following files in the repository:

- README.md
- PROJECT_SPEC.md
- CLAUDE_INSTRUCTIONS.md
- TEST_PLAN.md
- config/profile.yaml

These files define the system and are the source of truth.

Your job is to build the complete Version 1 implementation of the project.

- Do not stop after planning.
- Do not stop after a phase.
- Continue working until the system is fully implemented, tested, and documented.

You should only stop when the repository contains a working system, tests, reports, and a runnable dashboard.

---

## PROJECT GOAL

Build a lightweight modular AI-assisted job discovery system.

The system collects job listings, analyzes them against a candidate profile, and presents them in a dashboard.

Important rule:
- This system does NOT automatically apply to jobs.
- It is only a decision-support tool.

---

## VERSION 1 CAPABILITIES

The system must include:

1 Job collectors
Collect job listings from simple sources such as:
- RSS feeds
- simple career pages
- mock/demo job sources

Each job should include:

- title
- company
- location
- url
- description
- source
- date_found

---

## 2 Job normalization

Convert raw job listings into a consistent structure.

Implement deduplication using a unique hash based on:

title + company + description

---------------------------------------------------------------------

## 3 SQLite database

Create a lightweight database with tables such as:
- jobs
- scores
- status_history

Each job should track:
- title
- company
- location
- url
- description
- date_found
- status
- match_score

---

## 4 Filtering engine

Use the rules defined in config/profile.yaml.

Support:
- positive keyword matching
- negative keyword detection
- role classification

---

## 5 Match scoring engine

Implement a rules-based scoring system.

Example scoring rules:
- Python → +2
- AI / ML → +3
- Docker → +2
- AWS → +2
- FastAPI → +2
- LLM / RAG → +3

Negative signals:
- Senior → −2
- PhD → −3
- 10+ years → −3

The engine must output:
- match_score
- match_level (high / medium / low)
- matched_keywords
- missing_keywords
- rejection_flags
- explanation text

The explanation should be human readable.

---

## 6 Streamlit dashboard

Create a clean Streamlit dashboard.

It must display:
- overview metrics
- job list
- match scores
- filtering options
- search
- job explanation panel
- job link
- manual status update

Status values:
- new
- reviewing
- saved
- ignored
- applied_manual

The dashboard must work in Docker.

---

## 7 Services and scripts

Create scripts or services for:
- database initialization
- job collection
- job scoring
- running the dashboard

---

## 8 Docker support

Provide Dockerfile and docker-compose configuration.

Running:
- docker compose up

should start the system and the dashboard.

---

## 9 Tests

Implement pytest tests for:
- job parsing
- duplicate detection
- filtering logic
- scoring logic
- database persistence
- dashboard startup sanity

Tests must pass successfully.

---

## 10 Logging

Add basic logging for:
- job collection
- filtering
- scoring
- database operations

---

## 11 Reports

When implementation is finished, generate the following files:
- FINAL_IMPLEMENTATION_REPORT.md
- TEST_RESULTS.md
- KNOWN_LIMITATIONS.md
- NEXT_STEPS_V2.md

FINAL_IMPLEMENTATION_REPORT must include:
- system architecture
- modules implemented
- data flow
- dashboard description
- how to run
- summary of capabilities

TEST_RESULTS must include:
- tests created
- pass/fail summary
- coverage areas

KNOWN_LIMITATIONS must describe:
- scraping limitations
- local execution limitations
- what is intentionally excluded in V1

NEXT_STEPS_V2 must suggest:
- LLM integration
- resume tailoring
- optional browser automation
- Postgres support
- background scheduling
- advanced analytics

---

## ENGINEERING RULES

Keep the system lightweight.

Avoid unnecessary complexity.

Prefer simple and reliable solutions.

Use Python 3.11 style.

Use type hints where appropriate.

Avoid heavy frameworks.

Do not implement:

automatic job application
browser automation for applying
CAPTCHA solving
paid API dependency

The system must work locally.

---

## WORKFLOW

Execute the following without stopping:

1 Inspect repository files
2 Create project structure
3 Implement database
4 Implement collectors
5 Implement normalization and deduplication
6 Implement filtering
7 Implement scoring
8 Implement Streamlit dashboard
9 Implement tests
10 Verify Docker runtime
11 Generate reports
12 Perform internal audit
13 Clean up code
14 Finalize documentation

Do not stop after describing steps.

Actually implement the code and create the files.

---

## SUCCESS CRITERIA

The project is complete only when:
- The system runs locally
- The dashboard loads
- Jobs appear in the dashboard
- Match scoring works
- Filtering works
- Tests run successfully
- Docker works
- Final reports exist

---

## FINAL STEP

When finished, provide a short summary including:
- what modules were implemented
- how to run the system
- how to run tests
- which files contain the most important logic
- what improvements are recommended for Version 2