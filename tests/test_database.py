# tests/test_database.py
# This file is part of the OpenLLM project issue tracker:

"""Tests for database persistence and integrity."""
import json
import pytest
from datetime import datetime

from app.db.models import Job, Score, StatusHistory
from app.collectors.base import RawJob
from app.db.normalizer import insert_jobs_dedup, raw_to_job
from app.services.job_service import JobService


def _make_raw(title="AI Engineer", company="Corp AI", description="Python docker aws ai"):
    return RawJob(
        title=title,
        company=company,
        location="Remote",
        description=description,
        url="https://example.com/job/test",
        source="test",
        raw_text=description,
    )


class TestJobPersistence:
    def test_job_inserted_and_retrievable(self, db_session):
        raw = _make_raw()
        insert_jobs_dedup(db_session, [raw])
        job = db_session.query(Job).first()
        assert job is not None
        assert job.title == "AI Engineer"
        assert job.company == "Corp AI"
        assert job.status == "new"

    def test_job_has_unique_hash(self, db_session):
        raw = _make_raw()
        insert_jobs_dedup(db_session, [raw])
        job = db_session.query(Job).first()
        assert job.unique_hash
        assert len(job.unique_hash) == 64

    def test_multiple_jobs_stored(self, db_session):
        raws = [_make_raw(f"Job {i}", f"Corp {i}") for i in range(5)]
        insert_jobs_dedup(db_session, raws)
        count = db_session.query(Job).count()
        assert count == 5

    def test_job_to_dict(self, db_session):
        raw = _make_raw()
        insert_jobs_dedup(db_session, [raw])
        job = db_session.query(Job).first()
        d = job.to_dict()
        assert d["title"] == "AI Engineer"
        assert "id" in d
        assert "status" in d


class TestScorePersistence:
    def test_score_stored_and_retrieved(self, db_session, sample_profile):
        raw = _make_raw()
        insert_jobs_dedup(db_session, [raw])
        service = JobService(db_session, profile=sample_profile)
        service.score_all_unscored()

        score = db_session.query(Score).first()
        assert score is not None
        assert score.match_score is not None
        assert score.match_level in ("high", "medium", "low")

    def test_score_keywords_are_lists(self, db_session, sample_profile):
        raw = _make_raw(description="python docker aws ai llm")
        insert_jobs_dedup(db_session, [raw])
        service = JobService(db_session, profile=sample_profile)
        service.score_all_unscored()

        score = db_session.query(Score).first()
        assert isinstance(score.get_matched_keywords(), list)
        assert isinstance(score.get_missing_keywords(), list)
        assert isinstance(score.get_rejection_flags(), list)

    def test_score_explanation_stored(self, db_session, sample_profile):
        raw = _make_raw()
        insert_jobs_dedup(db_session, [raw])
        service = JobService(db_session, profile=sample_profile)
        service.score_all_unscored()

        score = db_session.query(Score).first()
        assert score.explanation
        assert len(score.explanation) > 10


class TestStatusHistory:
    def test_status_update_recorded(self, db_session, sample_profile):
        raw = _make_raw()
        insert_jobs_dedup(db_session, [raw])
        job = db_session.query(Job).first()

        service = JobService(db_session, profile=sample_profile)
        service.update_status(job.id, "reviewing")

        history = db_session.query(StatusHistory).filter_by(job_id=job.id).first()
        assert history is not None
        assert history.old_status == "new"
        assert history.new_status == "reviewing"

    def test_job_status_updated(self, db_session, sample_profile):
        raw = _make_raw()
        insert_jobs_dedup(db_session, [raw])
        job = db_session.query(Job).first()

        service = JobService(db_session, profile=sample_profile)
        service.update_status(job.id, "saved")

        db_session.refresh(job)
        assert job.status == "saved"

    def test_invalid_status_rejected(self, db_session, sample_profile):
        raw = _make_raw()
        insert_jobs_dedup(db_session, [raw])
        job = db_session.query(Job).first()

        service = JobService(db_session, profile=sample_profile)
        result = service.update_status(job.id, "invalid_status")
        assert result is False


class TestJobService:
    def test_get_summary_stats(self, db_session, sample_profile):
        raws = [_make_raw(f"Job {i}", f"Corp {i}") for i in range(3)]
        insert_jobs_dedup(db_session, raws)
        service = JobService(db_session, profile=sample_profile)
        service.score_all_unscored()
        stats = service.get_summary_stats()
        assert stats["total_jobs"] == 3
        assert "high_match" in stats
        assert "medium_match" in stats
        assert "low_match" in stats

    def test_get_jobs_with_scores(self, db_session, sample_profile):
        raw = _make_raw()
        insert_jobs_dedup(db_session, [raw])
        service = JobService(db_session, profile=sample_profile)
        service.score_all_unscored()
        jobs = service.get_jobs_with_scores()
        assert len(jobs) == 1
        assert "match_score" in jobs[0]
        assert "title" in jobs[0]

    def test_run_collectors_returns_stats(self, db_session, sample_profile):
        from app.collectors.mock_collector import MockCollector
        service = JobService(db_session, profile=sample_profile)
        stats = service.run_collectors([MockCollector()])
        assert stats["inserted"] > 0
        assert "skipped" in stats
        assert "collected" in stats
