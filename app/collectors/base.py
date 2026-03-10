"""Abstract base class for all job collectors."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawJob:
    """Normalized raw job record before DB insertion."""
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    raw_text: str = ""
    date_found: datetime = field(default_factory=datetime.utcnow)


class BaseCollector(ABC):
    """All collectors must implement collect()."""

    source_name: str = "unknown"

    @abstractmethod
    def collect(self) -> list[RawJob]:
        """Collect and return a list of raw job records."""
        ...
