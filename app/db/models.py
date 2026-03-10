# db/models.py
# this file defines the SQLAlchemy ORM models for the database tables: Job, Score, StatusHistory

"""SQLAlchemy ORM models for the AI Career Agent database."""
import datetime
import json
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass

# Note: We use a single "jobs" table to store all collected jobs, regardless of source.
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), default="")
    location = Column(String(255), default="")
    source = Column(String(100), default="")
    url = Column(String(512), default="")
    description = Column(Text, default="")
    raw_text = Column(Text, default="")
    date_found = Column(DateTime, default=datetime.datetime.utcnow)
    unique_hash = Column(String(64), unique=True, nullable=False)
    status = Column(String(50), default="new")

    scores = relationship("Score", back_populates="job", cascade="all, delete-orphan")
    status_history = relationship("StatusHistory", back_populates="job", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "source": self.source,
            "url": self.url,
            "description": self.description,
            "date_found": self.date_found.isoformat() if self.date_found else None,
            "unique_hash": self.unique_hash,
            "status": self.status,
        }


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    match_score = Column(Float, default=0.0)
    match_level = Column(String(20), default="low")
    matched_keywords = Column(Text, default="[]")   # JSON list
    missing_keywords = Column(Text, default="[]")   # JSON list
    rejection_flags = Column(Text, default="[]")    # JSON list
    explanation = Column(Text, default="")
    scored_at = Column(DateTime, default=datetime.datetime.utcnow)

    # V2 fields — nullable for backward compatibility with existing rows
    keyword_score = Column(Float, nullable=True)     # raw keyword score (before semantic boost)
    semantic_score = Column(Float, nullable=True)    # theme-based semantic score (0–10)
    final_score = Column(Float, nullable=True)       # combined final score
    matched_themes = Column(Text, nullable=True)     # JSON list of matched theme names
    missing_themes = Column(Text, nullable=True)     # JSON list of missing theme names

    job = relationship("Job", back_populates="scores")

    def get_matched_keywords(self) -> list[str]:
        return json.loads(self.matched_keywords or "[]")

    def get_missing_keywords(self) -> list[str]:
        return json.loads(self.missing_keywords or "[]")

    def get_rejection_flags(self) -> list[str]:
        return json.loads(self.rejection_flags or "[]")

    def get_matched_themes(self) -> list[str]:
        return json.loads(self.matched_themes or "[]")

    def get_missing_themes(self) -> list[str]:
        return json.loads(self.missing_themes or "[]")

    def to_dict(self) -> dict:
        effective_score = self.final_score if self.final_score is not None else self.match_score
        return {
            "id": self.id,
            "job_id": self.job_id,
            # V1 compatible
            "match_score": effective_score,
            "match_level": self.match_level,
            "matched_keywords": self.get_matched_keywords(),
            "missing_keywords": self.get_missing_keywords(),
            "rejection_flags": self.get_rejection_flags(),
            "explanation": self.explanation,
            "scored_at": self.scored_at.isoformat() if self.scored_at else None,
            # V2 fields
            "keyword_score": self.keyword_score,
            "semantic_score": self.semantic_score,
            "final_score": self.final_score,
            "matched_themes": self.get_matched_themes(),
            "missing_themes": self.get_missing_themes(),
        }


class StatusHistory(Base):
    __tablename__ = "status_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    old_status = Column(String(50), default="")
    new_status = Column(String(50), default="")
    changed_at = Column(DateTime, default=datetime.datetime.utcnow)
    note = Column(Text, default="")

    job = relationship("Job", back_populates="status_history")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
            "note": self.note,
        }
