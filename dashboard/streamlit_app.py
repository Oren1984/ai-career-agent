# dashboard/streamlit_app.py
# this file is part of the OpenLLM project issue tracker:

"""AI Career Agent — Streamlit Dashboard (v2.5)."""
import sys
import os
import logging

# Allow running from any working directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.db.session import init_db, get_session_factory
from app.services.job_service import JobService, VALID_STATUSES

logger = logging.getLogger(__name__)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Agent",
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
    """
    Create a fresh JobService with a new session for each call.

    Using a fresh session per operation prevents SQLAlchemy session state
    errors (PendingRollbackError, IllegalStateChangeError) that occur when
    a single long-lived cached session is shared across Streamlit reruns.
    """
    factory = _get_session_factory()
    session = factory()
    return JobService(session)


# ── Candidate profile (cached, lightweight) ───────────────────────────────────
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


# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("AI Career Agent")
st.sidebar.caption("v2.5 — Decision support only")
st.sidebar.markdown("---")

# Filters
st.sidebar.subheader("Filters")

status_options = ["all"] + sorted(VALID_STATUSES)
selected_status = st.sidebar.selectbox("Status", status_options, index=0)

match_level_options = ["all", "high", "medium", "low", "unscored"]
selected_level = st.sidebar.selectbox("Match Level", match_level_options, index=0)

text_search = st.sidebar.text_input("Search (title / company / description)", "")

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Actions")

col_a, col_b = st.sidebar.columns(2)

with col_a:
    if st.button("Fetch (Mock)", use_container_width=True):
        try:
            from app.collectors.mock_collector import MockCollector
            svc = get_service()
            stats = svc.run_collectors([MockCollector()])
            st.sidebar.success(
                f"Inserted {stats['inserted']} jobs ({stats['skipped']} dupes skipped)"
            )
        except Exception as exc:
            st.sidebar.error(f"Fetch failed: {exc}")
        finally:
            st.rerun()

with col_b:
    if st.button("Score All", use_container_width=True):
        try:
            svc = get_service()
            n = svc.score_all_unscored()
            st.sidebar.success(f"Scored {n} jobs")
        except Exception as exc:
            st.sidebar.error(f"Scoring failed: {exc}")
        finally:
            st.rerun()

if st.sidebar.button("Fetch via RSS", use_container_width=True):
    try:
        from app.collectors.rss_collector import RSSCollector
        svc = get_service()
        with st.sidebar:
            with st.spinner("Fetching RSS feeds…"):
                stats = svc.run_collectors([RSSCollector()])
        if stats.get("errors", 0) > 0:
            st.sidebar.warning(
                f"Inserted {stats['inserted']} jobs ({stats['skipped']} dupes). "
                f"{stats['errors']} feed(s) failed — check logs."
            )
        else:
            st.sidebar.success(
                f"Inserted {stats['inserted']} jobs ({stats['skipped']} dupes skipped)"
            )
    except Exception as exc:
        st.sidebar.error(f"RSS fetch failed: {exc}")
    finally:
        st.rerun()

# V2: LLM provider status in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("V2 Status")
provider_name = _get_llm_provider_name()
provider_icon = "🟢" if provider_name != "mock" else "⚪"
st.sidebar.caption(f"LLM Provider: {provider_icon} {provider_name}")
st.sidebar.caption("Scoring: keyword + semantic")

# ── Main area ──────────────────────────────────────────────────────────────────
st.title("AI Career Agent Dashboard")

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

# ── V2 Tabs: Jobs | Analytics | Profile ───────────────────────────────────────
tab_jobs, tab_analytics, tab_profile = st.tabs(["Jobs", "Analytics", "Candidate Profile"])

# ── Tab: Jobs ─────────────────────────────────────────────────────────────────
with tab_jobs:
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
        st.info("No jobs found. Click **Fetch (Mock)** in the sidebar to load demo data.")
    else:
        _LEVEL_COLOR = {
            "high": "🟢",
            "medium": "🟡",
            "low": "🔴",
            "unscored": "⚪",
        }

        # Table header
        hcols = st.columns([3, 2, 2, 1, 1, 1, 2])
        hcols[0].markdown("**Title**")
        hcols[1].markdown("**Company**")
        hcols[2].markdown("**Location**")
        hcols[3].markdown("**Score**")
        hcols[4].markdown("**Sem**")
        hcols[5].markdown("**Level**")
        hcols[6].markdown("**Status**")
        st.markdown("---")

        selected_job_id = st.session_state.get("selected_job_id")

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

                    # V2 score display
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

                    # ── V2.5: AI Analysis (user-triggered) ────────────────────
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
                            with st.spinner("Analysing…"):
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

        # Simple bar chart using native Streamlit
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
    "AI Career Agent v2.5 — Decision support only. "
    "This system does not submit job applications automatically."
)
