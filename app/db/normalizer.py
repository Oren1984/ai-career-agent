"""Normalize and deduplicate raw job records before DB insertion."""
import hashlib
import logging
from sqlalchemy.exc import IntegrityError

from app.collectors.base import RawJob
from app.db.models import Job

logger = logging.getLogger(__name__)


def compute_hash(title: str, company: str, description: str) -> str:
    """Generate a unique hash from job title + company + first 500 chars of description."""
    key = f"{title.lower().strip()}|{company.lower().strip()}|{description[:500].lower().strip()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def raw_to_job(raw: RawJob) -> Job:
    """Convert a RawJob dataclass into a Job ORM model."""
    unique_hash = compute_hash(raw.title, raw.company, raw.description)
    return Job(
        title=raw.title,
        company=raw.company,
        location=raw.location,
        source=raw.source,
        url=raw.url,
        description=raw.description,
        raw_text=raw.raw_text,
        date_found=raw.date_found,
        unique_hash=unique_hash,
        status="new",
    )


def insert_jobs_dedup(session, raw_jobs: list[RawJob]) -> tuple[int, int]:
    """
    Insert raw jobs into the database, skipping duplicates.

    Each job is flushed individually so that an IntegrityError on one row
    does not corrupt the session state for subsequent rows.

    Returns:
        (inserted_count, skipped_count)
    """
    inserted = 0
    skipped = 0

    # If the session is in a broken state from a prior failure, recover first.
    try:
        existing_hashes: set[str] = {
            row[0] for row in session.query(Job.unique_hash).all()
        }
    except Exception as exc:
        logger.warning("Session query failed, attempting rollback: %s", exc)
        session.rollback()
        existing_hashes = {
            row[0] for row in session.query(Job.unique_hash).all()
        }

    for raw in raw_jobs:
        job = raw_to_job(raw)

        if job.unique_hash in existing_hashes:
            logger.debug("Skipping duplicate: %s @ %s", raw.title, raw.company)
            skipped += 1
            continue

        try:
            session.add(job)
            # Flush individually so an IntegrityError only affects this row,
            # not the entire batch.
            session.flush()
            existing_hashes.add(job.unique_hash)
            inserted += 1
        except IntegrityError:
            # Race condition or hash collision — skip silently.
            session.rollback()
            logger.debug(
                "Duplicate detected at flush (race condition), skipping: %s @ %s",
                raw.title,
                raw.company,
            )
            skipped += 1
            # Reload existing hashes after rollback so the set stays accurate.
            existing_hashes = {
                row[0] for row in session.query(Job.unique_hash).all()
            }

    try:
        session.commit()
    except Exception as exc:
        session.rollback()
        logger.error("Commit failed during insert_jobs_dedup: %s", exc)
        raise

    logger.info("Inserted %d jobs, skipped %d duplicates", inserted, skipped)
    return inserted, skipped
