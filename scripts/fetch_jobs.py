# scripts/fetch_jobs.py
# This file is part of the OpenLLM project issue tracker:

"""Fetch jobs from all configured collectors and persist to DB."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import argparse
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from app.db.session import init_db, get_session
from app.services.job_service import JobService


def main():
    parser = argparse.ArgumentParser(description="Fetch jobs from configured collectors.")
    parser.add_argument("--mock", action="store_true", default=False,
                        help="Use mock collector only")
    parser.add_argument("--rss", action="store_true", default=False,
                        help="Use RSS collector only")
    parser.add_argument("--all-sources", action="store_true", default=False,
                        help="Load all enabled sources from config/sources.yaml")
    parser.add_argument("--no-mock", action="store_true",
                        help="Exclude mock collector even when using --all-sources")
    args = parser.parse_args()

    init_db()
    session = get_session()

    try:
        collectors = []

        if args.all_sources:
            from app.collectors.source_loader import load_collectors
            collectors = load_collectors(include_mock=not args.no_mock)
            logger.info("Loaded %d collector(s) from sources.yaml", len(collectors))

        else:
            # Explicit flags — default to mock if nothing specified
            use_mock = args.mock or (not args.rss)
            use_rss = args.rss

            if use_mock and not args.no_mock:
                from app.collectors.mock_collector import MockCollector
                collectors.append(MockCollector())
                logger.info("Using MockCollector")

            if use_rss:
                from app.collectors.rss_collector import RSSCollector
                collectors.append(RSSCollector())
                logger.info("Using RSSCollector (default feeds)")

        if not collectors:
            logger.error("No collectors selected.")
            sys.exit(1)

        service = JobService(session)
        stats = service.run_collectors(collectors)

        print(f"\nCollection complete:")
        print(f"  Collected : {stats['collected']}")
        print(f"  Inserted  : {stats['inserted']}")
        print(f"  Skipped   : {stats['skipped']} (duplicates)")
        if stats.get("errors", 0) > 0:
            print(f"  Errors    : {stats['errors']} collector(s) failed (see logs)")

    finally:
        session.close()


if __name__ == "__main__":
    main()
