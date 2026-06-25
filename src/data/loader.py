"""
Dataset loader — fetches the Zomato dataset from Hugging Face.

Implements local caching so repeated runs don't re-download.
In production (Railway), a pre-built slim parquet is committed to the repo
so the server never needs to download from Hugging Face at runtime.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from src.config import settings

logger = logging.getLogger(__name__)

# Pre-built slim parquet committed to the repo (only essential columns, ~0.5 MB)
_SLIM_PARQUET = Path(__file__).resolve().parent.parent.parent / "data" / "restaurants_slim.parquet"


class DatasetLoader:
    """Load the Zomato restaurant dataset from local cache or Hugging Face."""

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

        Priority order:
        1. Pre-built slim parquet (committed to repo — used in production)
        2. Local raw parquet cache
        3. Download from Hugging Face (local dev fallback)
        """
        # 1. Check for the slim parquet committed to the repo
        if _SLIM_PARQUET.exists():
            logger.info("Loading dataset from slim parquet: %s", _SLIM_PARQUET)
            return pd.read_parquet(_SLIM_PARQUET)

        # 2. Check for the full raw cache
        if self._cache_file.exists():
            logger.info("Loading dataset from cache: %s", self._cache_file)
            return pd.read_parquet(self._cache_file)

        # 3. Download from Hugging Face as last resort
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

