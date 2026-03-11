# dashboard/streamlit_app.py
# This file is part of the OpenLLM project issue tracker:

"""AI Career Agent — Streamlit Dashboard (V1).

V1 Platform: Israeli sources (Drushim, AllJobs) + RSS + Mock
Sources are configured in config/sources.yaml.
"""
import sys
import os
import subprocess
import logging

# Allow running from any working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st  # noqa: E402
from app.db.session import init_db, get_session_factory  # noqa: E402
from app.services.job_service import JobService, VALID_STATUSES  # noqa: E402

logger = logging.getLogger(__name__)

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRIPTS_DIR = os.path.join(_REPO_ROOT, "scripts")
_PYTHON = sys.executable

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Agent — V1",
    page_icon="🤖",
    layout="wide",
)


# ── DB bootstrap ───────────────────────────────────────────────────────────────
@st.cache_resource
def _get_session_factory():
    """Initialize DB once and return the session factory (cached across reruns)."""
    try:
        init_db()
    except Exception as exc:
        logger.error("DB init failed: %s", exc)
    return get_session_factory()


def get_service() -> JobService:
    """Create a fresh JobService with a new session for each call."""
    factory = _get_session_factory()
    session = factory()
    return JobService(session)


# ── Source mode detection ──────────────────────────────────────────────────────
def _detect_source_mode() -> str:
    """
    Detect the current source mode from SOURCE_MODE env var or sources.yaml.

    Priority:
      1. SOURCE_MODE environment variable
      2. Enabled source types in config/sources.yaml
      3. Default: "mock"
    """
    env_mode = os.environ.get("SOURCE_MODE", "").lower().strip()
    if env_mode in ("mock", "rss", "israel", "all"):
        return env_mode

    # Detect from sources.yaml
    try:
        import yaml
        sources_path = os.path.join(_REPO_ROOT, "config", "sources.yaml")
        with open(sources_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        sources = data.get("sources", [])
        enabled_types = {
            s["source_type"]
            for s in sources
            if s.get("enabled", False)
        }
        israel_types = {"drushim", "alljobs", "jobnet", "jobkarov", "jobmaster", "jobify360"}
        has_israel = bool(enabled_types & israel_types)
        has_rss = "rss" in enabled_types
        has_mock = "mock" in enabled_types

        if has_israel and has_rss:
            return "all"
        elif has_israel:
            return "israel"
        elif has_rss:
            return "rss"
        elif has_mock:
            return "mock"
    except Exception:
        pass
    return "mock"


@st.cache_data(ttl=60)
def _get_source_mode() -> str:
    return _detect_source_mode()


_MODE_LABELS = {
    "mock":   "Mock (demo data)",
    "rss":    "RSS Feeds",
    "israel": "Israeli Sources (Drushim + AllJobs)",
    "all":    "All Sources",
}

_MODE_COLORS = {
    "mock":   "gray",
    "rss":    "blue",
    "israel": "green",
    "all":    "orange",
}


def _run_script(script_name: str, *args: str) -> tuple[bool, str]:
    """Run a script via subprocess and return (success, output)."""
    cmd = [_PYTHON, os.path.join(_SCRIPTS_DIR, script_name)] + list(args)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=_REPO_ROOT,
        )
        output = result.stdout + (f"\n[stderr]\n{result.stderr}" if result.stderr.strip() else "")
        return result.returncode == 0, output.strip()
    except subprocess.TimeoutExpired:
        return False, "Script timed out after 120 seconds."
    except Exception as exc:
        return False, f"Failed to run script: {exc}"


# ── Candidate profile (cached) ─────────────────────────────────────────────────
@st.cache_resource
def _load_candidate_profile():
    try:
        from app.candidate.profile_loader import load_candidate_profile
        return load_candidate_profile()
    except Exception as exc:
        logger.warning("Could not load candidate profile: %s", exc)
        return None


# ── LLM provider info (cached) ─────────────────────────────────────────────────
@st.cache_resource
def _get_llm_provider_name() -> str:
    try:
        from app.llm.provider_factory import get_provider
        p = get_provider()
        return p.provider_name
    except Exception:
        return "mock"


# ── Detect current mode ────────────────────────────────────────────────────────
source_mode = _get_source_mode()
mode_label = _MODE_LABELS.get(source_mode, source_mode)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("AI Career Agent")
st.sidebar.caption("V1 Platform — Israeli & Global Sources")
st.sidebar.markdown("---")

# Source mode indicator
st.sidebar.subheader("Source Mode")
mode_color = _MODE_COLORS.get(source_mode, "gray")
st.sidebar.markdown(
    f'<span style="background-color:{mode_color};color:white;'
    f'padding:3px 10px;border-radius:12px;font-weight:bold;font-size:0.85em;">'
    f'  {mode_label}'
    f'</span>',
    unsafe_allow_html=True,
)
st.sidebar.caption("Set `SOURCE_MODE` env var to override (mock/rss/israel/all)")
st.sidebar.markdown("---")

# ── Filters ────────────────────────────────────────────────────────────────────
st.sidebar.subheader("Filters")
status_options = ["all"] + sorted(VALID_STATUSES)
selected_status = st.sidebar.selectbox("Status", status_options, index=0)
match_level_options = ["all", "high", "medium", "low", "unscored"]
selected_level = st.sidebar.selectbox("Match Level", match_level_options, index=0)
text_search = st.sidebar.text_input("Search (title / company / description)", "")

st.sidebar.markdown("---")

# ── Quick Actions ──────────────────────────────────────────────────────────────
st.sidebar.subheader("Quick Actions")

# Fetch buttons — one per source mode
if st.sidebar.button("Fetch Mock Jobs", use_container_width=True,
                     help="Load hardcoded demo jobs (no network needed)"):
    with st.sidebar:
        with st.spinner("Fetching mock jobs..."):
            ok, out = _run_script("fetch_jobs.py", "--mode", "mock")
    if ok:
        st.sidebar.success("Mock jobs fetched.")
    else:
        st.sidebar.error(f"Fetch failed:\n{out[:400]}")
    st.rerun()

if st.sidebar.button("Fetch RSS Jobs", use_container_width=True,
                     help="Fetch from RSS feeds (requires network)"):
    with st.sidebar:
        with st.spinner("Fetching RSS feeds..."):
            ok, out = _run_script("fetch_jobs.py", "--mode", "rss")
    if ok:
        st.sidebar.success("RSS jobs fetched.")
    else:
        st.sidebar.warning(f"RSS fetch finished with issues:\n{out[:400]}")
    st.rerun()

if st.sidebar.button("Fetch Israeli Jobs", use_container_width=True,
                     help="Fetch from Drushim + AllJobs (currently mock-safe)"):
    with st.sidebar:
        with st.spinner("Fetching Israeli source jobs..."):
            ok, out = _run_script("fetch_jobs.py", "--mode", "israel")
    if ok:
        st.sidebar.success("Israeli source jobs fetched.")
    else:
        st.sidebar.error(f"Fetch failed:\n{out[:400]}")
    st.rerun()

if st.sidebar.button("Score Jobs", use_container_width=True,
                     help="Score all unscored jobs against your candidate profile"):
    with st.sidebar:
        with st.spinner("Scoring jobs..."):
            ok, out = _run_script("score_jobs.py")
    if ok:
        st.sidebar.success("Scoring complete.")
    else:
        st.sidebar.error(f"Scoring failed:\n{out[:400]}")
    st.rerun()

if st.sidebar.button("Reset Demo State", use_container_width=True,
                     help="Drop and recreate DB, fetch Israeli demo jobs, score them"):
    with st.sidebar:
        with st.spinner("Resetting demo state (this may take a moment)..."):
            ok, out = _run_script("reset_demo_state.py", "--mode", "israel")
    if ok:
        st.sidebar.success("Demo state reset. Dashboard refreshed.")
        # Clear the session factory cache so it picks up the new DB
        _get_session_factory.clear()
    else:
        st.sidebar.error(f"Reset failed:\n{out[:400]}")
    st.rerun()

# LLM status
st.sidebar.markdown("---")
st.sidebar.subheader("LLM Status")
provider_name = _get_llm_provider_name()
provider_icon = "🟢" if provider_name != "mock" else "⚪"
st.sidebar.caption(f"Provider: {provider_icon} {provider_name}")
st.sidebar.caption("Scoring: keyword + semantic")

# ── Main area ──────────────────────────────────────────────────────────────────
st.title("AI Career Agent — V1 Dashboard")

try:
    service = get_service()
    summary = service.get_summary_stats()
except Exception as exc:
    st.error(f"Could not load dashboard data: {exc}")
    st.stop()

# ── Summary metrics ────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total Jobs", summary["total_jobs"])
m2.metric("High Match", summary["high_match"])
m3.metric("Medium Match", summary["medium_match"])
m4.metric("Low Match", summary["low_match"])
m5.metric("New / Unreviewed", summary["status_counts"].get("new", 0))

st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_jobs, tab_analytics, tab_profile = st.tabs(["Jobs", "Analytics", "Candidate Profile"])

# ── Tab: Jobs ─────────────────────────────────────────────────────────────────
with tab_jobs:
    # Data source banner
    try:
        svc_for_analytics = get_service()
        analytics = svc_for_analytics.get_source_analytics()
        by_source = analytics.get("by_source", {}) if analytics else {}
    except Exception:
        by_source = {}

    if by_source:
        source_names = ", ".join(
            f"**{src}** ({cnt})" for src, cnt in sorted(by_source.items(), key=lambda x: -x[1])
        )
        st.info(
            f"Current data sources: {source_names}. "
            "Use the Quick Actions in the sidebar to fetch or reset data."
        )
    else:
        st.info(
            "No jobs in the database yet. "
            "Use **Fetch Israeli Jobs**, **Fetch Mock Jobs**, or **Fetch RSS Jobs** in the sidebar."
        )

    try:
        jobs = service.get_jobs_with_scores(
            status_filter=selected_status if selected_status != "all" else None,
            match_level_filter=selected_level if selected_level != "all" else None,
            text_search=text_search or None,
        )
    except Exception as exc:
        st.error(f"Could not load job list: {exc}")
        jobs = []

    st.subheader(f"Jobs ({len(jobs)} shown)")

    if not jobs:
        st.info(
            "No jobs match the current filters. "
            "Try changing the filters or fetching more jobs."
        )
    else:
        _LEVEL_COLOR = {
            "high": "🟢",
            "medium": "🟡",
            "low": "🔴",
            "unscored": "⚪",
        }

        hcols = st.columns([3, 2, 2, 1, 1, 1, 2])
        hcols[0].markdown("**Title**")
        hcols[1].markdown("**Company**")
        hcols[2].markdown("**Location**")
        hcols[3].markdown("**Score**")
        hcols[4].markdown("**Sem**")
        hcols[5].markdown("**Level**")
        hcols[6].markdown("**Status**")
        st.markdown("---")

        for job in jobs:
            jid = job["id"]
            badge = _LEVEL_COLOR.get(job["match_level"], "⚪")
            row = st.columns([3, 2, 2, 1, 1, 1, 2])
            row[0].write(job["title"])
            row[1].write(job["company"])
            row[2].write(job["location"])
            row[3].write(f"{job['match_score']:.1f}")
            sem = job.get("semantic_score")
            row[4].write(f"{sem:.1f}" if sem is not None else "—")
            row[5].write(f"{badge}")
            row[6].write(job["status"])

            if st.button(f"View #{jid}", key=f"view_{jid}"):
                st.session_state["selected_job_id"] = jid
                st.rerun()

        # ── Detail panel ───────────────────────────────────────────────────────
        selected_id = st.session_state.get("selected_job_id")
        if selected_id:
            detail = next((j for j in jobs if j["id"] == selected_id), None)

            if detail is None:
                try:
                    all_jobs = service.get_jobs_with_scores()
                    detail = next((j for j in all_jobs if j["id"] == selected_id), None)
                except Exception:
                    detail = None

            if detail:
                st.markdown("---")
                st.subheader(f"Job Detail — {detail['title']}")

                d1, d2 = st.columns([2, 1])

                with d1:
                    st.markdown(f"**Company:** {detail['company']}")
                    st.markdown(f"**Location:** {detail['location']}")
                    st.markdown(f"**Source:** {detail['source']}")
                    if detail["url"]:
                        st.markdown(f"**URL:** [{detail['url']}]({detail['url']})")
                    st.markdown(f"**Date Found:** {detail['date_found']}")

                    st.markdown("#### Description")
                    st.text_area(
                        "description",
                        value=detail["description"],
                        height=200,
                        disabled=True,
                        label_visibility="collapsed",
                    )

                with d2:
                    badge = _LEVEL_COLOR.get(detail["match_level"], "⚪")

                    kw_score = detail.get("keyword_score")
                    sem_score = detail.get("semantic_score")
                    final_score = detail.get("final_score") or detail["match_score"]

                    st.markdown(
                        f"### {badge} Final Score: {final_score:.1f} — {detail['match_level'].upper()}"
                    )

                    if kw_score is not None and sem_score is not None:
                        sc1, sc2 = st.columns(2)
                        sc1.metric("Keyword Score", f"{kw_score:.1f}")
                        sc2.metric("Semantic Score", f"{sem_score:.1f}/10")

                    if detail.get("matched_themes"):
                        st.markdown("**Matched Themes:**")
                        st.success(", ".join(detail["matched_themes"]))

                    if detail.get("missing_themes"):
                        st.markdown("**Missing Themes:**")
                        st.info(", ".join(detail["missing_themes"]))

                    if detail["matched_keywords"]:
                        st.markdown("**Matched Keywords:**")
                        st.success(", ".join(detail["matched_keywords"]))

                    if detail["missing_keywords"]:
                        st.markdown("**Missing Keywords:**")
                        st.info(", ".join(detail["missing_keywords"]))

                    if detail["rejection_flags"]:
                        st.markdown("**Rejection Flags:**")
                        st.warning(", ".join(detail["rejection_flags"]))

                    st.markdown("**Explanation:**")
                    st.write(detail["explanation"])

                    # ── AI Analysis (user-triggered) ───────────────────────────
                    st.markdown("---")
                    st.markdown("**AI Analysis**")

                    _cache_key = f"llm_analysis_{selected_id}"
                    cached_analysis = st.session_state.get(_cache_key)

                    if cached_analysis:
                        with st.expander("Analysis result", expanded=True):
                            st.write(cached_analysis)
                        if st.button("Clear Analysis", key=f"clear_analysis_{selected_id}"):
                            del st.session_state[_cache_key]
                            st.rerun()
                    else:
                        if st.button(
                            "Get AI Analysis",
                            key=f"llm_{selected_id}",
                            help=f"Analyse this job with the {provider_name} provider",
                        ):
                            with st.spinner("Analysing..."):
                                try:
                                    from app.llm.provider_factory import get_provider
                                    from app.candidate.profile_loader import load_candidate_profile
                                    _provider = get_provider()
                                    _profile = load_candidate_profile()
                                    _analysis = _provider.analyze_job(
                                        job_title=detail["title"],
                                        job_description=detail["description"],
                                        profile_summary=_profile.to_prompt_string(),
                                    )
                                    st.session_state[_cache_key] = _analysis
                                    st.rerun()
                                except Exception as exc:
                                    st.error(f"AI analysis failed: {exc}")

                    st.markdown("---")
                    st.markdown("**Update Status:**")
                    new_status = st.selectbox(
                        "New status",
                        sorted(VALID_STATUSES),
                        index=sorted(VALID_STATUSES).index(detail["status"])
                        if detail["status"] in VALID_STATUSES
                        else 0,
                        key=f"status_select_{selected_id}",
                    )
                    note = st.text_input("Note (optional)", key=f"note_{selected_id}")
                    if st.button("Save Status", key=f"save_{selected_id}"):
                        try:
                            ok = service.update_status(selected_id, new_status, note)
                            if ok:
                                st.success(f"Status updated to '{new_status}'")
                            else:
                                st.error("Failed to update status.")
                        except Exception as exc:
                            st.error(f"Status update failed: {exc}")
                        st.rerun()

                    if st.button("Close Detail", key=f"close_{selected_id}"):
                        del st.session_state["selected_job_id"]
                        st.rerun()

# ── Tab: Analytics ────────────────────────────────────────────────────────────
with tab_analytics:
    st.subheader("Source & Match Analytics")

    try:
        analytics = service.get_source_analytics()
    except Exception as exc:
        st.error(f"Could not load analytics: {exc}")
        analytics = None

    if analytics:
        a1, a2, a3 = st.columns(3)
        a1.metric("Total Jobs", analytics["total_jobs"])
        a2.metric("Total Scored", analytics["total_scored"])
        a3.metric("High Match Ratio", f"{analytics['high_match_ratio']:.0%}")

        st.markdown("---")

        col_src, col_lvl = st.columns(2)

        with col_src:
            st.markdown("**Jobs by Source**")
            if analytics["by_source"]:
                for src, count in sorted(analytics["by_source"].items(), key=lambda x: -x[1]):
                    st.write(f"• **{src}**: {count}")
            else:
                st.info("No data yet.")

        with col_lvl:
            st.markdown("**Jobs by Match Level**")
            level_icons = {"high": "🟢", "medium": "🟡", "low": "🔴", "unscored": "⚪"}
            for lvl, count in analytics["by_level"].items():
                icon = level_icons.get(lvl, "")
                st.write(f"{icon} **{lvl.capitalize()}**: {count}")

        st.markdown("---")
        st.markdown("**Match Level Distribution**")
        level_data = {k.capitalize(): v for k, v in analytics["by_level"].items() if v > 0}
        if level_data:
            import pandas as pd
            df = pd.DataFrame(list(level_data.items()), columns=["Level", "Count"])
            df = df.set_index("Level")
            st.bar_chart(df)

# ── Tab: Candidate Profile ─────────────────────────────────────────────────────
with tab_profile:
    st.subheader("Candidate Profile")

    candidate = _load_candidate_profile()

    if candidate is None:
        st.warning("Could not load candidate profile. Check data/candidate_profile/.")
    else:
        p1, p2 = st.columns([2, 1])

        with p1:
            if candidate.summary:
                st.markdown("**Summary**")
                st.write(candidate.summary)

            if candidate.target_roles:
                st.markdown("**Target Roles**")
                st.write(", ".join(candidate.target_roles))

            if candidate.skills:
                st.markdown("**Skills**")
                for category, skills in candidate.skills.items():
                    st.write(f"*{category.replace('_', ' ').title()}:* {', '.join(skills)}")

        with p2:
            if candidate.projects:
                st.markdown("**Projects**")
                for proj in candidate.projects:
                    with st.expander(proj.get("name", "Project")):
                        st.write(proj.get("description", ""))
                        techs = proj.get("technologies", [])
                        if techs:
                            st.caption(f"Tech: {', '.join(techs)}")

            if candidate.positive_keywords:
                st.markdown("**Positive Keywords**")
                st.success(", ".join(candidate.positive_keywords))

            if candidate.negative_keywords:
                st.markdown("**Negative Keywords**")
                st.warning(", ".join(candidate.negative_keywords))

        st.markdown("---")
        st.markdown("**Profile Prompt String** (used in LLM analysis)")
        with st.expander("View"):
            st.code(candidate.to_prompt_string(), language=None)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "AI Career Agent V1 — Decision support only. "
    "This system does not submit job applications automatically. "
    f"| Current mode: {mode_label}"
)
