## This file documents the prompt used to instruct the AI system during development.
## It is stored for documentation and transparency of how parts of the project were generated.

## You need to FIX the current repository so the app actually reflects the new V1 architecture in practice, not only on paper.

Current problem:
The repository contains the new V1 closure work (Israeli collectors, dedup, notifications, Gmail/n8n future-ready, CI/CD, tests, docs), but when running the dashboard, the UI still behaves like the old version:
- it shows old mock jobs
- quick actions still expose only old fetch actions
- the new Israeli-source flow is not visible in the dashboard
- the DB/run flow is confusing
- scheduler tests are failing
- the user should not need manual round-trips and guesswork just to see the new version

Your job is to CLEANLY FIX this entire situation in one pass.

==================================================
GOAL
==================================================

Make the repository behave like a real V1 product where:
1. the dashboard reflects the new V1 architecture
2. Israeli sources are visible and understandable
3. mock/demo mode is clearly separated from V1 Israeli-source mode
4. the run flow is simple and obvious
5. failing scheduler tests are fixed
6. the user can launch and demonstrate the correct version without confusion

==================================================
WHAT TO FIX
==================================================

1) DASHBOARD / UI ALIGNMENT

Update the Streamlit dashboard so it clearly reflects the current V1 architecture.

Requirements:
- Clearly show which source mode is currently active:
  - Mock mode
  - RSS mode
  - Israeli sources mode
- Add a visible section in the UI for source mode/status
- Add a dedicated action/button for Israeli source collection
- Keep old mock mode only as a separate demo/testing mode
- Do not let the dashboard feel like it is still the old version

The user should immediately understand:
- what data is currently shown
- where it came from
- whether it is mock/demo or Israeli-source V1 flow

2) FETCH FLOW SIMPLIFICATION

Create a clean run flow for V1.

Requirements:
- Ensure `fetch_jobs.py` can run Israeli enabled sources in a predictable way
- Make source selection/config behavior clear
- If needed, add flags or config support such as:
  - mock only
  - rss only
  - israel only
  - all enabled
- Document the default behavior clearly
- The user should not need guesswork to know what fetch mode is being used

3) DATABASE / DATA RESET EXPERIENCE

The current app is showing old data and that causes confusion.

Fix the experience so demoing the new version is easy.

Requirements:
- Provide a clean and documented way to reset the DB/demo data
- If needed, add a helper script for reset + init + fetch + score
- Make sure the user can easily refresh the system into the intended V1 state
- Avoid dangerous destructive behavior unless explicit

If helpful, create a script like:
- scripts/reset_demo_state.py
or
- scripts/run_v1_demo.py

4) SCHEDULER TEST FAILURES

Two tests are currently failing because scheduler.shutdown(wait=False) is called while the APScheduler instance is not running.

Fix this properly.

Requirements:
- either start the scheduler before shutdown in tests
- or make tests robust to not-running state
- or adjust create_scheduler contract if needed
- choose the cleanest engineering fix
- all tests must pass afterward

Important:
Do not hack around it badly.
Fix it in a clean and maintainable way.

5) V1 DEMO ENTRYPOINT

Create one obvious way to run the correct V1 demo.

Requirements:
- provide one recommended command/script for:
  - init/reset
  - fetch correct sources
  - score
  - launch dashboard
- make this visible in README and/or docs
- reduce friction for the user as much as possible

Good outcome:
The user should have one clean path to run “the new version” without confusion.

6) REQUIREMENTS / RUNTIME CONSISTENCY

Ensure runtime dependencies and behavior are aligned.

Requirements:
- keep requirements correct
- make sure optional packages degrade gracefully
- ensure the dashboard and scripts run consistently with the current codebase
- preserve future-ready Gmail/n8n mocks without activating them

7) DOCUMENTATION UPDATE

Update documentation so it matches the actual runtime behavior.

At minimum update:
- README.md
- docs/V1_CLOSURE_REPORT.md
- any run instructions affected by the fixes

Documentation must explain:
- what “new V1 version” means in runtime
- what is mock mode
- what is Israeli-source mode
- what the recommended demo flow is
- what remains future/mock-only

==================================================
EXPECTED IMPLEMENTATION DETAILS
==================================================

Please implement practical improvements such as:

- Dashboard badges / labels:
  - “Current Mode: Mock”
  - “Current Mode: Israeli Sources”
- Separate quick actions:
  - Fetch Mock Jobs
  - Fetch RSS Jobs
  - Fetch Israeli Jobs
  - Score Jobs
  - Reset Demo State (optional if safe)
- A small visible note in dashboard header explaining current dataset origin
- Better config/source loader clarity
- One V1 helper runner script if needed

==================================================
FINAL DELIVERABLES
==================================================

At the end, provide:

1. Code changes
2. Updated dashboard behavior
3. Fixed tests
4. Updated run flow
5. Updated docs
6. A final short report file:

docs/V1_RUNTIME_ALIGNMENT_REPORT.md

This report must include:
- what runtime confusion existed
- what was fixed
- how dashboard behavior changed
- how fetch modes now work
- how to run the correct V1 flow
- what remains mock/future-only
- confirmation that tests pass

==================================================
SUCCESS CRITERIA
==================================================

The task is complete only if:
- the dashboard no longer feels like the old version
- there is a visible Israeli-source V1 path
- mock/demo mode is separated clearly
- scheduler tests pass
- the user has one obvious way to run the correct V1 version
- docs match reality

Do not stop at partial analysis.
Implement the fixes.
Then update docs.
Then create the final runtime alignment report.