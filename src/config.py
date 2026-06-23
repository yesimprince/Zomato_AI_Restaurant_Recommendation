"""
Centralized application configuration.

Loads settings from environment variables and .env file using pydantic-settings.
All configurable values (API keys, thresholds, paths) live here.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application-wide settings loaded from .env and environment variables."""

    # ── Hugging Face dataset ──
    hf_dataset_name: str = Field(
        default="ManikaSaini/zomato-restaurant-recommendation",
        description="Hugging Face dataset identifier",
    )

    # ── Data cache ──
    data_cache_path: str = Field(
        default="./data",
        description="Local directory for cached dataset files",
    )

    # ── Budget tier thresholds (INR cost_for_two boundaries) ──
    budget_thresholds: Dict[str, int] = Field(
        default={"low": 500, "medium": 1500},
        description="Upper bounds for budget tiers: cost <= low → 'low', cost <= medium → 'medium', else 'high'",
    )

    # ── Candidate & recommendation limits ──
    max_candidates: int = Field(
        default=15,
        description="Max restaurants sent to the LLM for ranking",
    )
    top_k: int = Field(
        default=5,
        description="Number of final recommendations returned to the user",
    )

    # ── Groq LLM ──
    groq_api_key: str = Field(
        default="",
        description="Groq API key (required for LLM calls)",
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model identifier",
    )
    groq_fallback_model: str = Field(
        default="llama-3.1-8b-instant",
        description="Cheaper/faster fallback model for dev or retries",
    )
    groq_temperature: float = Field(
        default=0.3,
        description="LLM sampling temperature (lower = more deterministic)",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def cache_dir(self) -> Path:
        """Return the cache directory as a Path, creating it if needed."""
        path = Path(self.data_cache_path)
        path.mkdir(parents=True, exist_ok=True)
        return path


# Singleton instance — import this wherever settings are needed.
settings = Settings()
