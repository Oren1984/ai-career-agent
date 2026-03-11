## This file documents the prompt used to instruct the AI system during development.
## It is stored for documentation and transparency of how parts of the project were generated.

## You are working on Version 1 closure of a modular job-search automation platform.

## Your task is to IMPLEMENT and CLOSE the entire V1 foundation in one structured pass, based on the exact scope below.

IMPORTANT:
- Work carefully and consistently.
- Preserve modular architecture.
- Do not over-engineer.
- Do not activate real Gmail or real n8n integrations.
- Prepare them as future-ready mocked/planned infrastructure only.
- Keep everything production-style, clean, documented, and testable.
- At the end, create a final closure report file that summarizes exactly what was implemented, what is mocked, what is disabled, what is planned, and how the system is structured.

==================================================
V1 SCOPE TO IMPLEMENT
==================================================

1) ISRAELI SOURCES LAYER

Create the following source layer:

app/collectors/israel/
├── base_israel_collector.py
├── drushim_collector.py
├── alljobs_collector.py
├── jobnet_collector.py
├── jobkarov_collector.py
├── jobmaster_collector.py
└── jobify360_collector.py

Requirements:
- Build a full modular skeleton for all these sources.
- Not all sources must be active on day one.
- Support enabled_sources and planned_sources behavior.
- Enable only 2–3 relatively stable sources by default.
- Mark the rest as disabled/planned clearly in config and docs.
- Every collector should follow a shared contract/interface.
- Each collector should support:
  - fetch_jobs()
  - normalize_job()
  - source_name
  - supports_apply_link
  - requires_auth
- If scraping/parsing is not fully safe to implement now, create a placeholder/mock-safe collector with clear TODO comments and documentation.

2) STRONG DEDUP ENGINE

Implement strong deduplication logic.

Dedup strategy should support layered matching:
- by URL if available
- by source_job_id if available
- by normalized title + company + city/area
- optional light fuzzy matching fallback

Requirements:
- clean modular dedup engine
- deterministic behavior
- test coverage
- clear explanation in docs
- persistence support if relevant
- keep implementation simple, reliable, and explainable

3) SCORING LAYER

Keep and complete the scoring layer with:
- keyword scoring
- semantic / embeddings scoring
- combined scoring

Requirements:
- preserve fallback behavior if embedding libraries are unavailable
- graceful degradation
- no hard dependency that breaks the system
- clean scorer interfaces
- combined scorer should still work even if semantic scorer is disabled/unavailable
- scoring should be testable and documented

4) RESUME MATCHING

Keep and complete resume matching flow with:
- parse_resume.py
- extraction logic
- fallback behavior
- candidate profile writing/storage

Requirements:
- make it useful but lightweight
- avoid unnecessary complexity
- support fallback when resume parsing is partial
- document how resume data flows into matching/scoring
- test key paths

5) NOTIFICATIONS

Implement V1 notifications in a simple and safe way:
- console/log output
- local file summary
- email later (not active now)

Requirements:
- keep notification architecture modular
- support future channels later
- orchestrator structure is welcome
- for V1 connect only simple safe channels
- document active vs future channels clearly

6) GMAIL DIRECT OPTIONAL (FUTURE-READY ONLY)

Prepare Gmail integration infrastructure but DO NOT activate real Gmail access.

Create something like:

app/integrations/gmail/
├── gmail_client.py
├── gmail_models.py
├── gmail_mock.py
└── README_FUTURE_GMAIL.md

Requirements:
- this is future-ready only
- no real OAuth flow should be active
- no real Gmail permissions required
- include mocked/planned structure only
- include documentation for future auth flow
- define future env vars such as:
  - GMAIL_ENABLED=false
  - GMAIL_MODE=mock
  - GMAIL_CLIENT_ID=
  - GMAIL_CLIENT_SECRET=
- explain future use cases:
  - read replies
  - detect recruiter emails
  - save interactions
- clearly state what is implemented now vs what is only mocked/planned

7) N8N READINESS ONLY (FUTURE-READY ONLY)

Prepare n8n future integration structure but DO NOT activate real n8n workflows.

Create something like:

automation/
├── n8n/
│   ├── docker-compose.n8n.yml
│   ├── workflows/
│   │   └── example_job_notification.json
│   └── README_FUTURE_N8N.md
└── bridge/
    ├── webhook_contract.md
    └── sample_payloads.json

Requirements:
- this is future-ready only
- no real dependency on n8n
- no live activation required
- create mocked/planned webhook contract
- include sample future endpoints:
  - /webhooks/job-found
  - /webhooks/new-match
  - /webhooks/recruiter-reply
- explain clearly how future automation would work
- clearly distinguish active V1 functionality from mocked future architecture

8) TESTING

Implement a complete V1 testing foundation.

Include:

Unit tests:
- collectors parsing
- dedup engine
- scorer
- resume parser fallback
- config loading

Integration tests:
- fetch → normalize → dedup
- score → save
- notify mock
- disabled Gmail behavior
- disabled n8n behavior

Mock tests:
- mock Gmail connector
- mock n8n webhook
- fake sources / fixtures

Important:
The system must work correctly even when there is no:
- Gmail auth
- n8n
- embedding libraries
- external APIs

Use graceful fallback everywhere appropriate.

9) GITHUB ACTIONS CI/CD

Create a clean GitHub Actions setup for V1.

This should be smart CI/CD, not heavy cloud deployment.

Create:

.github/workflows/
├── ci.yml
├── test-matrix.yml
├── security.yml
├── docker-smoke.yml
└── release.yml

Requirements:

ci.yml:
- run on push / pull_request
- lint
- format check
- tests
- import/config validation

test-matrix.yml:
- test multiple Python versions if appropriate

security.yml:
- basic security scan
- bandit
- pip-audit
- trivy only if Docker context exists and it makes sense

docker-smoke.yml:
- optional Docker build
- smoke validation that app starts

release.yml:
- release on tag only
- build artifact/package
- no real deployment

Important:
- CI should be strong
- CD should be light and controlled
- no auto cloud deployment

==================================================
IMPLEMENTATION RULES
==================================================

- Keep architecture modular and readable.
- Prefer clean, practical code over theoretical complexity.
- Add comments only where they help.
- Add documentation where future readers need clarity.
- Respect disabled/planned/future-ready separation.
- Avoid fake completeness: if something cannot be fully activated now, represent it honestly as mock/planned/future.
- Do not break existing architecture unnecessarily.
- Reuse existing structures when appropriate.
- Keep naming consistent across code, tests, config, and docs.

==================================================
DELIVERABLES REQUIRED
==================================================

1. Implement/update the codebase according to all sections above.
2. Add/update configuration files as needed.
3. Add/update tests.
4. Add/update GitHub Actions workflows.
5. Add/update documentation files for:
   - Israeli sources
   - dedup logic
   - scoring
   - resume matching
   - notifications
   - future Gmail
   - future n8n
   - CI/CD
6. At the very end, create a final closure report file.

==================================================
FINAL CLOSURE REPORT
==================================================

Create this file at the end:

docs/V1_CLOSURE_REPORT.md

This report must include:

1. Executive summary
2. What was implemented in V1
3. Israeli sources status:
   - enabled
   - disabled
   - planned
4. Dedup strategy summary
5. Scoring architecture summary
6. Resume matching summary
7. Notifications summary
8. Gmail future-ready mock summary
9. n8n future-ready mock summary
10. Testing summary
11. GitHub Actions / CI-CD summary
12. What is intentionally NOT active yet
13. Recommended next steps for V1.5 / V2
14. Any assumptions / limitations / TODOs

==================================================
WORKING STYLE
==================================================

Proceed step by step internally, but perform the work as one cohesive closure pass.
Do not ask unnecessary questions.
Make reasonable engineering decisions where needed.
Be explicit in the final report.
Aim for a repository state that looks clean, intentional, and professionally structured.