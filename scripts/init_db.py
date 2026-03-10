#!/usr/bin/env python3
"""Initialize the SQLite database — create all tables and apply V2 migrations."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

from app.db.session import init_db, get_engine

# V2 columns to add to the scores table if they don't exist yet
_V2_MIGRATIONS = [
    ("keyword_score",  "ALTER TABLE scores ADD COLUMN keyword_score REAL"),
    ("semantic_score", "ALTER TABLE scores ADD COLUMN semantic_score REAL"),
    ("final_score",    "ALTER TABLE scores ADD COLUMN final_score REAL"),
    ("matched_themes", "ALTER TABLE scores ADD COLUMN matched_themes TEXT"),
    ("missing_themes", "ALTER TABLE scores ADD COLUMN missing_themes TEXT"),
]


def apply_v2_migrations(engine):
    """Add V2 columns to the scores table if they are absent (safe, idempotent)."""
    from sqlalchemy import inspect, text
    inspector = inspect(engine)

    # scores table may not exist on brand-new DBs — skip in that case
    if "scores" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("scores")}

    with engine.connect() as conn:
        for col_name, alter_sql in _V2_MIGRATIONS:
            if col_name not in existing_columns:
                conn.execute(text(alter_sql))
                logger.info("V2 migration: added column '%s' to scores table.", col_name)
        conn.commit()


if __name__ == "__main__":
    engine = get_engine()
    from app.db.models import Base
    Base.metadata.create_all(engine)
    apply_v2_migrations(engine)
    logger.info("Database initialized at %s", engine.url)
    print("Database initialized successfully (V2-ready).")
