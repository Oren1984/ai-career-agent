"""Abstract LLM provider interface — future-ready for V2 integration."""
from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """
    Interface for LLM providers.
    Implement this to add OpenAI, Claude, Gemini, or local models in V2.
    """

    provider_name: str = "base"

    @abstractmethod
    def analyze_job(self, job_title: str, job_description: str, profile_summary: str) -> str:
        """
        Generate a natural-language analysis of a job posting.

        Args:
            job_title: The job title.
            job_description: Full job description text.
            profile_summary: A summary of the candidate's profile.

        Returns:
            A string containing the LLM's analysis.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this provider is properly configured and reachable."""
        ...
