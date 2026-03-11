# candidate/profile_loader.py
# this file defines the CandidateProfile dataclass and
# the load_candidate_profile function to read profile data from disk

"""Candidate profile loader — reads structured profile files and builds a unified CandidateProfile."""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_PROFILE_DIR = Path(__file__).parent.parent.parent / "data" / "candidate_profile"
_CONFIG_PROFILE_PATH = Path(__file__).parent.parent.parent / "config" / "profile.yaml"


# Note: This loader is designed to be flexible and tolerant of missing files.
@dataclass
class CandidateProfile:
    """
    Unified candidate profile object built from:
      - config/profile.yaml    (target roles, keywords)
      - data/candidate_profile/summary.txt   (free-text summary)
      - data/candidate_profile/skills.json   (structured skills)
      - data/candidate_profile/projects.json (project examples)
    """

    # From config/profile.yaml
    target_roles: list[str] = field(default_factory=list)
    positive_keywords: list[str] = field(default_factory=list)
    negative_keywords: list[str] = field(default_factory=list)

    # From data/candidate_profile/
    summary: str = ""
    skills: dict[str, list[str]] = field(default_factory=dict)
    projects: list[dict[str, Any]] = field(default_factory=list)

    # Convenience properties
    @property
    def all_skills(self) -> list[str]:
        """Flat list of all skills across all categories."""
        result: list[str] = []
        for skill_list in self.skills.values():
            result.extend(skill_list)
        return result

    # This method is designed to create a concise summary of the candidate's profile for use in LLM prompts.
    def to_prompt_string(self) -> str:
        """Build a concise profile summary suitable for LLM prompts."""
        parts: list[str] = []

        if self.summary:
            parts.append(f"Summary: {self.summary}")

        if self.target_roles:
            parts.append(f"Target Roles: {', '.join(self.target_roles)}")

        if self.all_skills:
            parts.append(f"Key Skills: {', '.join(self.all_skills[:20])}")
        elif self.positive_keywords:
            parts.append(f"Key Skills: {', '.join(self.positive_keywords)}")

        if self.projects:
            project_names = [p.get("name", "Unnamed") for p in self.projects[:3]]
            parts.append(f"Recent Projects: {', '.join(project_names)}")

        if self.negative_keywords:
            parts.append(f"Not targeting: {', '.join(self.negative_keywords)} roles")

        return "\n".join(parts)

    # This method can be used for debugging or logging to see the full structured profile data.
    def to_dict(self) -> dict[str, Any]:
        return {
            "target_roles": self.target_roles,
            "positive_keywords": self.positive_keywords,
            "negative_keywords": self.negative_keywords,
            "summary": self.summary,
            "skills": self.skills,
            "projects": self.projects,
        }


# This function is the main entry point for loading the candidate profile from disk.
def load_candidate_profile(
    profile_dir: str | Path | None = None,
    config_path: str | Path | None = None,
) -> CandidateProfile:
    """
    Load the candidate profile from disk.

    Reads (in order, all optional):
      1. config/profile.yaml      → target_roles, keywords
      2. data/candidate_profile/summary.txt   → free-text summary
      3. data/candidate_profile/skills.json   → structured skills
      4. data/candidate_profile/projects.json → projects

    Missing files are silently skipped; defaults are empty.
    """
    profile = CandidateProfile()

    # 1. Load config/profile.yaml
    cfg_path = Path(config_path or _CONFIG_PROFILE_PATH)
    if cfg_path.exists():
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            profile.target_roles = cfg.get("target_roles", [])
            profile.positive_keywords = cfg.get("positive_keywords", [])
            profile.negative_keywords = cfg.get("negative_keywords", [])
            logger.debug("Loaded profile config from %s", cfg_path)
        except Exception as exc:
            logger.warning("Could not read %s: %s", cfg_path, exc)

    # 2–4. Load data/candidate_profile/ files
    p_dir = Path(profile_dir or _DEFAULT_PROFILE_DIR)

    summary_path = p_dir / "summary.txt"
    if summary_path.exists():
        try:
            profile.summary = summary_path.read_text(encoding="utf-8").strip()
            logger.debug("Loaded candidate summary from %s", summary_path)
        except Exception as exc:
            logger.warning("Could not read %s: %s", summary_path, exc)

    # 3. skills.json can be either a dict of categories → lists, or a flat list of skills.
    skills_path = p_dir / "skills.json"
    if skills_path.exists():
        try:
            with open(skills_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Accept either a dict[str, list[str]] or a flat list[str]
            if isinstance(data, dict):
                profile.skills = data
            elif isinstance(data, list):
                profile.skills = {"skills": data}
            logger.debug("Loaded candidate skills from %s", skills_path)
        except Exception as exc:
            logger.warning("Could not read %s: %s", skills_path, exc)

    # Note: projects.json is expected to be a list of dicts, each with at least a "name" field.
    projects_path = p_dir / "projects.json"
    if projects_path.exists():
        try:
            with open(projects_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                profile.projects = data
            logger.debug("Loaded candidate projects from %s", projects_path)
        except Exception as exc:
            logger.warning("Could not read %s: %s", projects_path, exc)

    return profile
