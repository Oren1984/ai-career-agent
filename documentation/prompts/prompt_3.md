## This file documents the prompt used to instruct the AI system during development.
## It is stored for documentation and transparency of how parts of the project were generated.

## You are now in stabilization, bug-fix, source-configuration, and V2-preparation mode for this repository.

## Read the repository files again and use them as the source of truth, including:
- README.md
- PROJECT_SPEC.md
- CLAUDE_INSTRUCTIONS.md
- TEST_PLAN.md
- config/profile.yaml
- FINAL_IMPLEMENTATION_REPORT.md
- TEST_RESULTS.md
- KNOWN_LIMITATIONS.md
- NEXT_STEPS_V2.md

## You must continue working directly in the repository.
- Do not stop at analysis only.
- Fix the implementation, harden it, document it, and prepare the repository cleanly for future V2 work.

## Important product rule:
- This system must remain a decision-support assistant.
- Do NOT implement automatic job application submission.
- Do NOT implement automatic CV sending.
- Do NOT implement browser automation for applying.
- Do NOT implement CAPTCHA solving.

==================================================
CURRENT ISSUES TO FIX FIRST
==================================================
The current implementation has database/session stability problems visible in runtime:

1. SQLAlchemy session state errors:
- PendingRollbackError
- IllegalStateChangeError
- commit() called while transaction state is invalid

2. Database uniqueness/insertion problem:
- UNIQUE constraint failed: jobs.id

These issues must be fixed first before any further enhancement.

==================================================
FIX REQUIREMENTS
==================================================
1. Database primary key fix
- Review the Job model and all insert flows.
- Ensure jobs.id is not manually assigned in a way that causes duplicate primary keys.
- Use proper autoincrement behavior for the primary key if appropriate.
- Keep unique_hash-based deduplication as the logical duplicate prevention mechanism.
- Prevent duplicate inserts cleanly and safely.

2. Session lifecycle fix
- Review all session usage across:
  - app/db
  - app/services
  - dashboard/streamlit_app.py
  - scripts
- Ensure rollback() is called after failed transactions.
- Ensure commit() is not called from nested or invalid transaction states.
- Refactor session management for safe and predictable behavior.
- Make collector failures and insert failures fail gracefully without leaving the UI unusable.

3. Dashboard stability fix
- The Streamlit dashboard must not crash if:
  - a collector fails
  - RSS parsing fails
  - insert dedup encounters an error
- Surface errors in a clean UI message instead of a raw crash where possible.
- Make the app recover gracefully.

==================================================
SOURCE CONFIGURATION IMPROVEMENT
==================================================
The system currently needs a clean and explicit way to know which sources to scan.

Implement a source registry/configuration layer.

Create a configuration file such as:
- config/sources.yaml

It should support source definitions like:
- name
- enabled
- source_type
- url
- notes
- priority

Support these source categories:
- mock
- rss
- company_page
- manual_reference
- future

Important:
Do NOT implement aggressive or fragile scraping for LinkedIn.
If LinkedIn is included, keep it as:
- manual_reference
or
- future
with documentation explaining why direct scraping is not enabled in V1/V1.5.

You may include practical initial sources such as:
- mock source
- RSS-based public feeds
- selected company career pages if lightweight and stable
- manual references for sites the user wants to track

The implementation should make it easy to add/edit sources later.

==================================================
V1.5 IMPROVEMENT PASS
==================================================
After fixing the critical bugs, improve the project into a stable V1.5 state.

Add or improve:

1. Stable demo mode
- Ensure the app works reliably with mock/demo jobs.
- The app must be demonstrable even if live sources fail.

2. Better collector orchestration
- Collectors should be isolated.
- Failure in one collector should not break all others.

3. Better logging
- Improve logging for:
  - source loading
  - collector execution
  - insert results
  - scoring
  - status updates
  - failures

4. Better status and admin flow
- Keep the manual statuses:
  - new
  - reviewing
  - saved
  - ignored
  - applied_manual

5. Better documentation
- Update README and reports to clearly explain:
  - what sources are active
  - how source configuration works
  - why LinkedIn is not actively scraped
  - how demo mode works
  - current V1.5 boundaries

==================================================
V2 PREPARATION ONLY
==================================================
Do NOT fully implement heavy V2 features now.
Instead, prepare the codebase cleanly for them.

Create scaffolding, interfaces, config placeholders, and docs for:

1. Real LLM provider integration
- Claude
- OpenAI
- Gemini
- optional Ollama/local

2. Semantic matching
- embeddings-based scoring
- profile-to-job semantic similarity

3. Scheduling
- APScheduler or equivalent background scheduling design

4. Resume/CV layer
- resume parsing placeholder
- structured candidate profile extraction
- future cover letter generation support

5. Analytics and database upgrade path
- roadmap for possible Postgres migration
- analytics/reporting ideas

These should be prepared as clean extension points, not as full production features yet.

==================================================
TESTING REQUIREMENTS
==================================================
Update and expand tests.

You must test:
- DB insert flow
- duplicate prevention
- rollback handling after failed insert
- session recovery after exceptions
- collector isolation
- source config loading
- filtering
- scoring
- dashboard basic startup sanity
- demo mode stability

Fix tests as needed.
Run the test suite.
Update test reports accordingly.

==================================================
DOCUMENTATION AND REPORTS
==================================================
Update or create the following files so the repository is clean and portfolio-ready:

1. README.md
2. FINAL_IMPLEMENTATION_REPORT.md
3. TEST_RESULTS.md
4. KNOWN_LIMITATIONS.md
5. NEXT_STEPS_V2.md
6. config/sources.yaml
7. optionally: docs/SOURCE_STRATEGY.md
8. optionally: docs/V1_5_STABILIZATION_REPORT.md

Documentation must clearly explain:
- what was fixed
- why the DB/session issue happened
- how it was resolved
- what sources are currently supported
- what remains future work
- what V2 means in this project
- what is intentionally excluded

==================================================
DEFINITION OF SUCCESS
==================================================
This task is complete only if all of the following are true:

- The dashboard runs without the current SQLAlchemy crash
- jobs.id duplication issue is resolved
- session rollback/commit handling is stable
- demo mode works reliably
- source configuration exists and is documented
- tests pass
- reports are updated
- the repository is ready for future V2 extension
- automatic CV submission still does not exist

==================================================
WORK MODE
==================================================
Do not stop after recommendations.
Do not only explain.
Apply the fixes directly in the repository.
Then run/verify tests.
Then update documentation and reports.
Then provide a concise final summary including:
- bugs fixed
- source strategy implemented
- files changed
- current supported source types
- what is ready for V2 next