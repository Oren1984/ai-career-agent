# scripts/reset_demo_state.py
# This file is part of the OpenLLM project issue tracker:

"""Reset the demo state — drop and recreate DB, fetch jobs, score them.

Usage:
    python scripts/reset_demo_state.py            # default: israel mode
    python scripts/reset_demo_state.py --mode mock
    python scripts/reset_demo_state.py --mode all
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import argparse
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_VALID_MODES = ("mock", "rss", "israel", "all")


def reset_database():
    """Drop all tables and recreate them from scratch."""
    from app.db.session import get_engine
    from app.db.models import Base

    logger.info("[reset] Dropping and recreating all DB tables...")
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Apply V2 column migrations
    from scripts.init_db import apply_v2_migrations
    apply_v2_migrations(engine)

    logger.info("[reset] Database reset complete.")


def fetch_jobs(mode: str):
    """Run the fetch step for the given mode."""
    from app.db.session import get_session
    from app.services.job_service import JobService
    from scripts.fetch_jobs import build_collectors

    logger.info("[reset] Fetching jobs (mode: %s)...", mode)
    session = get_session()
    try:
        collectors = build_collectors(mode)
        if not collectors:
            logger.warning("[reset] No collectors loaded — skipping fetch")
            return {"collected": 0, "inserted": 0, "skipped": 0}
        service = JobService(session)
        stats = service.run_collectors(collectors)
        logger.info("[reset] Fetch complete: %s", stats)
        return stats
    finally:
        session.close()


def score_jobs():
    """Score all unscored jobs."""
    from app.db.session import get_session
    from app.services.job_service import JobService

    logger.info("[reset] Scoring all unscored jobs...")
    session = get_session()
    try:
        service = JobService(session)
        count = service.score_all_unscored()
        stats = service.get_summary_stats()
        logger.info("[reset] Scored %d jobs", count)
        return count, stats
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Reset the demo state: drop DB, fetch jobs, score them.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  israel  — Israeli job boards (drushim + alljobs demo data) [default]
  mock    — hardcoded mock jobs
  rss     — RSS feed jobs (requires network)
  all     — all enabled sources

Example:
  python scripts/reset_demo_state.py
  python scripts/reset_demo_state.py --mode mock
        """,
    )
    parser.add_argument(
        "--mode",
        choices=_VALID_MODES,
        default="israel",
        help="Source mode to fetch after reset (default: israel)",
    )
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  AI Career Agent — Demo State Reset")
    print(f"  Mode: {args.mode.upper()}")
    print("=" * 60)

    # Step 1: Reset DB
    print("\n[1/3] Resetting database...")
    reset_database()
    print("      Database reset.")

    # Step 2: Fetch jobs
    print(f"\n[2/3] Fetching jobs (mode: {args.mode})...")
    stats = fetch_jobs(args.mode)
    print(f"      Collected: {stats.get('collected', 0)}, "
          f"Inserted: {stats.get('inserted', 0)}, "
          f"Skipped: {stats.get('skipped', 0)}")

    # Step 3: Score jobs
    print("\n[3/3] Scoring jobs...")
    scored_count, summary = score_jobs()
    print(f"      Scored: {scored_count} jobs")

    print()
    print("=" * 60)
    print("  RESET COMPLETE")
    print(f"  Total jobs in DB : {summary['total_jobs']}")
    print(f"  High matches     : {summary['high_match']}")
    print(f"  Medium matches   : {summary['medium_match']}")
    print(f"  Low matches      : {summary['low_match']}")
    print()
    print("  Run the dashboard:")
    print("    streamlit run dashboard/streamlit_app.py")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
