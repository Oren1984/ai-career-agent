# filtering/filter_engine.py
# this file defines the main filtering function to apply AI-based filters to collected jobs before scoring

"""Rules-based filter engine using profile keywords."""
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_PROFILE_PATH = Path(__file__).parent.parent.parent / "config" / "profile.yaml"


# Note: This is a simple keyword-based filter engine for demonstration purposes.
def load_profile(profile_path: str | Path | None = None) -> dict[str, Any]:
    """Load candidate profile from YAML file."""
    path = Path(profile_path or _DEFAULT_PROFILE_PATH)
    if not path.exists():
        logger.warning("Profile not found at %s — using empty profile", path)
        return {"positive_keywords": [], "negative_keywords": [], "target_roles": []}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


# The filter engine checks if a job matches any positive keywords and does not match any negative keywords.
def _text_lower(job) -> str:
    """Combine job title + description into one lowercase string for matching."""
    return f"{job.title} {job.description}".lower()


class FilterEngine:
    """
    Filters jobs based on positive/negative keyword rules from the profile.
    A job passes if it has at least one positive keyword and zero hard negative keywords.
    """

    def __init__(self, profile: dict[str, Any] | None = None):
        if profile is None:
            profile = load_profile()
        self.positive_keywords: list[str] = [k.lower() for k in profile.get("positive_keywords", [])]
        self.negative_keywords: list[str] = [k.lower() for k in profile.get("negative_keywords", [])]
        self.target_roles: list[str] = [r.lower() for r in profile.get("target_roles", [])]

    def check(self, job) -> dict[str, Any]:
        """
        Evaluate a job against the filter rules.

        Returns a dict with:
            passes (bool): whether the job passes all filters
            positive_hits (list): matched positive keywords
            negative_hits (list): matched negative keywords
        """
        text = _text_lower(job)

        positive_hits = [kw for kw in self.positive_keywords if kw in text]
        negative_hits = [kw for kw in self.negative_keywords if kw in text]

        # A job passes if it matches at least one positive keyword
        # and does not trigger any negative keywords
        passes = bool(positive_hits) and not bool(negative_hits)

        return {
            "passes": passes,
            "positive_hits": positive_hits,
            "negative_hits": negative_hits,
        }

    def filter_jobs(self, jobs: list) -> list:
        """Return only jobs that pass the filter."""
        passing = [job for job in jobs if self.check(job)["passes"]]
        logger.info(
            "Filter: %d/%d jobs passed keyword filter",
            len(passing),
            len(jobs),
        )
        return passing

    def identify_role_category(self, job) -> str:
        """
        Attempt to classify the job into a target role category.
        Returns the best matching role or 'other'.
        """
        text = _text_lower(job)
        for role in self.target_roles:
            # Check if all words of the role appear in the text
            role_words = role.split()
            if all(word in text for word in role_words):
                return role.title()
        return "Other"
