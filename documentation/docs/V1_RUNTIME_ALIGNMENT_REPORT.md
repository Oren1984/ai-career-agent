# V1 Runtime Alignment Report

## Date: 2026-03-11

---

## 1. What Runtime Confusion Existed Before This Fix

The repository contained V1 architecture (Israeli collectors, Drushim/AllJobs, dedup, notifications, etc.) but the running application still felt like the old V2.5 platform:

- The dashboard title still said "AI Career Agent Dashboard" with a "v2.5" caption
- The sidebar had only "Fetch (Mock)" and "Score All" buttons — no awareness of Israeli sources
- No source mode indicator: the user had no way to see which sources were active
- `scripts/fetch_jobs.py` used legacy `--mock` / `--rss` flags with no `--mode israel` option
- No `Reset Demo State` entry point existed
- No V1-specific demo script existed
- `datetime.utcnow()` deprecation warnings existed in 5 collector/notifier files
- Two scheduler tests failed with `SchedulerNotRunningError` because they called `scheduler.shutdown()` on a scheduler that was never started

---

## 2. What Was Fixed

### FIX 1: Dashboard UI Alignment (`dashboard/streamlit_app.py`)

- Rewrote the dashboard to clearly reflect V1 architecture
- Added a **Source Mode indicator** in the sidebar showing the current active mode (mock / RSS / Israeli Sources / All Sources)
- Mode is detected from `SOURCE_MODE` env var or by reading `config/sources.yaml`; can be overridden at runtime
- Replaced the two generic action buttons with five clearly named **Quick Action buttons**:
  - Fetch Mock Jobs
  - Fetch RSS Jobs
  - Fetch Israeli Jobs
  - Score Jobs
  - Reset Demo State
- All quick actions use `subprocess.run` with `sys.executable` (no hardcoded `python`)
- Added a **source banner** at the top of the Jobs tab showing which sources contributed current data
- Dashboard title and footer updated to say "V1"
- All three tabs (Jobs, Analytics, Candidate Profile) remain fully functional

### FIX 2: Fetch Flow (`scripts/fetch_jobs.py`)

- Added `--mode` flag with choices: `mock`, `rss`, `israel`, `all` (default: `all`)
- `--mode israel` loads Drushim + AllJobs collectors via `source_loader.load_collectors(types=[...])`
- Legacy flags (`--mock`, `--rss`, `--all-sources`) retained for backward compatibility
- Added clear section headers and logging output indicating which mode is running

### FIX 3: Database Reset Script (`scripts/reset_demo_state.py`)

- Created `scripts/reset_demo_state.py`
- Drops all DB tables and recreates them (including V2 column migrations)
- Fetches jobs using the specified `--mode` (default: `israel`)
- Scores all fetched jobs
- Prints a summary showing total, high, medium, low match counts
- Prints "Run the dashboard: streamlit run dashboard/streamlit_app.py"

### FIX 4: Scheduler Test Failures (`app/scheduler/scheduler.py`, `tests/test_scheduler.py`)

- Root cause: `test_create_scheduler_returns_scheduler` and `test_create_scheduler_custom_cron` called `scheduler.shutdown(wait=False)` on a `BackgroundScheduler` that was never started. APScheduler 3.x raises `SchedulerNotRunningError` in that case.
- Fix: added `safe_shutdown(scheduler, wait=False)` helper to `app/scheduler/scheduler.py` that checks `scheduler.state != STATE_STOPPED` before calling `shutdown()`
- Updated both tests to call `safe_shutdown()` instead of `scheduler.shutdown()`
- All 10 scheduler tests now pass

### FIX 5: V1 Demo Entrypoint (`scripts/run_v1_demo.py`)

- Created `scripts/run_v1_demo.py`
- Orchestrates: init DB → fetch Israeli jobs → score jobs → print dashboard instructions
- Falls back to mock if no Israeli collectors are loaded
- Prints: "Dashboard ready. Run: streamlit run dashboard/streamlit_app.py"

### FIX 6: datetime.utcnow() Deprecation Warnings

Fixed 5 files to use `datetime.now(timezone.utc).replace(tzinfo=None)` instead of `datetime.utcnow()`:
- `app/collectors/israel/drushim_collector.py`
- `app/collectors/israel/alljobs_collector.py`
- `app/collectors/greenhouse_collector.py` (2 occurrences)
- `app/collectors/lever_collector.py` (2 occurrences; also replaced `datetime.utcfromtimestamp`)
- `app/notifications/file_notifier.py`

### FIX 7: README.md

- Rewrote README to reflect V1 reality
- Documents what the V1 platform is
- Shows the recommended quick start flow (`run_v1_demo.py`)
- Documents all four source modes
- Includes a dashboard overview table of Quick Actions
- Lists what is future-ready (real scraping, Gmail, n8n, Slack, Telegram)
- Updated project structure to include new scripts

---

## 3. How Dashboard Behavior Changed

| Before | After |
|---|---|
| Title: "AI Career Agent Dashboard" | Title: "AI Career Agent — V1 Dashboard" |
| Caption: "v2.5 — Decision support only" | Caption: "V1 Platform — Israeli & Global Sources" |
| Buttons: "Fetch (Mock)", "Score All", "Fetch via RSS" | Buttons: Fetch Mock / Fetch RSS / Fetch Israeli / Score Jobs / Reset Demo State |
| No source mode indicator | Colored badge showing current mode |
| No data source context in Jobs tab | Banner showing which sources contributed current data |
| Footer: "AI Career Agent v2.5" | Footer: "AI Career Agent V1 — mode: [current mode]" |

---

## 4. How Fetch Modes Now Work

```
python scripts/fetch_jobs.py --mode mock     # MockCollector only
python scripts/fetch_jobs.py --mode rss      # RSSCollector (from sources.yaml feeds)
python scripts/fetch_jobs.py --mode israel   # DrushimCollector + AllJobsCollector
python scripts/fetch_jobs.py --mode all      # all enabled sources (default)
```

The dashboard Quick Action buttons map directly to these modes.

---

## 5. How to Run the Correct V1 Flow

### One-Shot Demo (recommended)
```bash
pip install -r requirements.txt
python scripts/run_v1_demo.py
streamlit run dashboard/streamlit_app.py
```

### Step-by-Step
```bash
pip install -r requirements.txt

# 1. Initialize DB
python scripts/init_db.py

# 2. Fetch Israeli source jobs (mock-safe)
python scripts/fetch_jobs.py --mode israel

# 3. Score jobs
python scripts/score_jobs.py

# 4. Launch dashboard
streamlit run dashboard/streamlit_app.py
```

### Reset and Restart
```bash
python scripts/reset_demo_state.py --mode israel
streamlit run dashboard/streamlit_app.py
```

### Docker
```bash
docker compose up
```

---

## 6. What Remains Mock / Future-Only

| Feature | Status |
|---|---|
| Drushim.co.il real HTTP scraping | Returns demo data (3 hardcoded jobs). Real scraping needs BeautifulSoup + pagination work. See `app/collectors/israel/drushim_collector.py` TODOs. |
| AllJobs.co.il real HTTP scraping | Returns demo data (3 hardcoded jobs). Same status. |
| JobNet, JobKarov, JobMaster, Jobify360 | Disabled collectors. Return empty list. |
| Email notifications | Config-ready (`config/notifications.yaml`). Requires SMTP credentials. |
| Slack / Telegram notifications | Config-ready. Requires webhook URL / bot token. |
| LinkedIn / Indeed | Manual reference only (ToS restrictions). |
| Greenhouse / Lever ATS | Functional collectors — requires company slugs in `sources.yaml`. |
| HackerNews "Who is Hiring?" | Functional collector — set `enabled: true` in `sources.yaml`. |

---

## 7. Test Status

After this fix:

- All scheduler tests pass (10/10): `python -m pytest tests/test_scheduler.py`
- No `SchedulerNotRunningError` failures
- `safe_shutdown()` helper added to `app/scheduler/scheduler.py`
- All other existing tests unaffected (no breaking changes to existing API surfaces)

To run the full test suite:
```bash
python -m pytest tests/ -v
```
