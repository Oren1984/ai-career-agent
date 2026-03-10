# collectors/source_loader.py
# this file defines the load_collectors() function to read sources.yaml and instantiate collectors

"""
Source loader — reads config/sources.yaml and instantiates the appropriate collectors.

Usage:
    from app.collectors.source_loader import load_collectors
    collectors = load_collectors()          # all enabled sources
    collectors = load_collectors(types=["rss"])    # only RSS sources
    collectors = load_collectors(include_mock=True) # include mock
"""
import logging
import os
from typing import Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

from app.collectors.base import BaseCollector

logger = logging.getLogger(__name__)

_DEFAULT_SOURCES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config",
    "sources.yaml",
)


def load_sources_config(path: str | None = None) -> list[dict[str, Any]]:
    """
    Load and return the raw list of source entries from sources.yaml.
    Returns an empty list if the file is missing or YAML is unavailable.
    """
    if not HAS_YAML:
        logger.warning("PyYAML not installed — cannot load sources.yaml")
        return []

    config_path = path or _DEFAULT_SOURCES_PATH

    if not os.path.exists(config_path):
        logger.warning("sources.yaml not found at %s", config_path)
        return []

    try:
        with open(config_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        sources = data.get("sources", []) if data else []
        logger.info("Loaded %d source entries from %s", len(sources), config_path)
        return sources
    except Exception as exc:
        logger.error("Failed to load sources.yaml: %s", exc)
        return []


def load_collectors(
    path: str | None = None,
    types: list[str] | None = None,
    include_mock: bool = True,
) -> list[BaseCollector]:
    """
    Build and return a list of collector instances from sources.yaml.

    Args:
        path:         Path to sources.yaml (defaults to config/sources.yaml).
        types:        If provided, only return collectors of these source_types
                      e.g. ["rss", "mock"]. Defaults to all active types.
        include_mock: Whether to include the mock collector (default: True).

    Returns:
        List of instantiated BaseCollector objects, ordered by priority.
    """
    sources = load_sources_config(path)

    if not sources:
        # Fallback: return mock collector so the app always works
        logger.warning("No sources loaded from config — falling back to MockCollector")
        from app.collectors.mock_collector import MockCollector
        return [MockCollector()] if include_mock else []

    # Sort by priority (lower = first)
    sources = sorted(sources, key=lambda s: s.get("priority", 99))

    collectors: list[BaseCollector] = []
    rss_feeds: list[dict] = []

    for source in sources:
        if not source.get("enabled", False):
            logger.debug("Source '%s' is disabled — skipping", source.get("name"))
            continue

        source_type = source.get("source_type", "")

        if types and source_type not in types:
            continue

        name = source.get("name", "unknown")

        if source_type == "mock":
            if not include_mock:
                logger.debug("Skipping mock source '%s' (include_mock=False)", name)
                continue
            from app.collectors.mock_collector import MockCollector
            collectors.append(MockCollector())
            logger.info("Loaded MockCollector for source '%s'", name)

        elif source_type == "rss":
            url = source.get("url")
            if url:
                rss_feeds.append({"url": url, "source": name})
                logger.info("Queued RSS feed: %s (%s)", name, url)
            else:
                logger.warning("RSS source '%s' has no URL — skipping", name)

        elif source_type == "greenhouse":
            companies = source.get("companies", [])
            if companies:
                from app.collectors.greenhouse_collector import GreenhouseCollector
                collectors.append(GreenhouseCollector(companies=companies))
                logger.info("Loaded GreenhouseCollector for %d companies: %s", len(companies), companies)
            else:
                logger.warning("Greenhouse source '%s' has no companies list — skipping", name)

        elif source_type == "lever":
            companies = source.get("companies", [])
            if companies:
                from app.collectors.lever_collector import LeverCollector
                collectors.append(LeverCollector(companies=companies))
                logger.info("Loaded LeverCollector for %d companies: %s", len(companies), companies)
            else:
                logger.warning("Lever source '%s' has no companies list — skipping", name)

        elif source_type == "hackernews":
            max_jobs = source.get("max_jobs", 100)
            from app.collectors.hackernews_collector import HackerNewsHiringCollector
            collectors.append(HackerNewsHiringCollector(max_jobs=max_jobs))
            logger.info("Loaded HackerNewsHiringCollector (max_jobs=%d)", max_jobs)

        elif source_type in ("company_page", "manual_reference", "future"):
            logger.debug(
                "Source '%s' (type=%s) is not auto-collectable — skipping",
                name,
                source_type,
            )

        else:
            logger.warning("Unknown source_type '%s' for source '%s'", source_type, name)

    # Batch all RSS feeds into a single RSSCollector
    if rss_feeds:
        from app.collectors.rss_collector import RSSCollector
        collectors.append(RSSCollector(feeds=rss_feeds))
        logger.info("Loaded RSSCollector with %d feeds", len(rss_feeds))

    logger.info("load_collectors() returning %d collector(s)", len(collectors))
    return collectors
