"""
Dataset loader — fetches the Zomato dataset from Hugging Face.

Implements local caching so repeated runs don't re-download.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.config import settings

logger = logging.getLogger(__name__)


class DatasetLoader:
    """Load the Zomato restaurant dataset from Hugging Face or local cache."""

    def __init__(
        self,
        dataset_name: str | None = None,
        cache_path: str | None = None,
    ) -> None:
        self.dataset_name = dataset_name or settings.hf_dataset_name
        self.cache_dir = Path(cache_path or settings.data_cache_path)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_file = self.cache_dir / "restaurants_raw.parquet"

    # ── public API ──

    def load(self) -> pd.DataFrame:
        """
        Return the raw dataset as a DataFrame.

        Checks for a local parquet cache first; falls back to Hugging Face
        download and then caches the result.
        """
        if self._cache_file.exists():
            logger.info("Loading dataset from cache: %s", self._cache_file)
            return pd.read_parquet(self._cache_file)

        logger.info(
            "Cache not found. Downloading dataset '%s' from Hugging Face …",
            self.dataset_name,
        )
        df = self._download()
        self._save_cache(df)
        return df

    # ── internals ──

    def _download(self) -> pd.DataFrame:
        """Download the dataset from Hugging Face and return as DataFrame."""
        from datasets import load_dataset  # lazy import to avoid slow startup

        dataset = load_dataset(self.dataset_name, split="train")
        df = dataset.to_pandas()
        logger.info(
            "Downloaded %d rows with columns: %s",
            len(df),
            list(df.columns),
        )
        return df

    def _save_cache(self, df: pd.DataFrame) -> None:
        """Persist DataFrame to local parquet for fast reload."""
        df.to_parquet(self._cache_file, index=False)
        logger.info("Cached dataset to %s", self._cache_file)
