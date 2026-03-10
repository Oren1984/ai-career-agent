#!/usr/bin/env python3
"""Score all unscored jobs against the candidate profile."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from app.db.session import init_db, get_session
from app.services.job_service import JobService


def main():
    init_db()
    session = get_session()

    try:
        service = JobService(session)
        count = service.score_all_unscored()
        stats = service.get_summary_stats()

        print(f"\nScoring complete:")
        print(f"  Jobs scored      : {count}")
        print(f"  Total jobs in DB : {stats['total_jobs']}")
        print(f"  High matches     : {stats['high_match']}")
        print(f"  Medium matches   : {stats['medium_match']}")
        print(f"  Low matches      : {stats['low_match']}")

    finally:
        session.close()


if __name__ == "__main__":
    main()
