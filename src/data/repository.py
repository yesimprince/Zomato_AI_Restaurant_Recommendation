"""
Restaurant repository — in-memory query interface over preprocessed data.

Acts as the single source of truth for restaurant data after loading and
preprocessing.  Provides convenience methods for filtering, distinct value
lookups, and bulk access.
"""

from __future__ import annotations

import logging
from typing import List, Optional

import pandas as pd

from src.config import settings
from src.data.loader import DatasetLoader
from src.data.preprocessor import DataPreprocessor
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class RestaurantRepository:
    """
    In-memory read-only repository of Restaurant records.

    Can be initialized with:
    - A pre-processed DataFrame (useful for tests)
    - Nothing (auto-loads and preprocesses the dataset on first access)
    """

    def __init__(self, df: Optional[pd.DataFrame] = None) -> None:
        self._df: Optional[pd.DataFrame] = df
        self._restaurants: Optional[List[Restaurant]] = None

    # ── lazy initialization ──

    def _ensure_loaded(self) -> None:
        """Load and preprocess the dataset if not already done."""
        if self._df is not None:
            return

        logger.info("Repository not initialized — loading dataset …")
        loader = DatasetLoader()
        raw_df = loader.load()

        preprocessor = DataPreprocessor()
        self._df = preprocessor.preprocess(raw_df)
        logger.info("Repository initialized with %d restaurants", len(self._df))

    @property
    def df(self) -> pd.DataFrame:
        """Access the underlying DataFrame (lazy-loaded)."""
        self._ensure_loaded()
        assert self._df is not None
        return self._df

    # ── public query API ──

    def get_all(self) -> List[Restaurant]:
        """Return all restaurants as a list of Restaurant model instances."""
        if self._restaurants is None:
            self._restaurants = self._df_to_restaurants(self.df)
        return self._restaurants

    def get_locations(self) -> List[str]:
        """Return sorted list of distinct location strings."""
        locations = self.df["location"].dropna().unique().tolist()
        return sorted(locations)

    def get_cuisines(self) -> List[str]:
        """Return sorted list of distinct cuisine strings (flattened from lists)."""
        all_cuisines: set[str] = set()
        for cuisine_list in self.df["cuisines"]:
            if isinstance(cuisine_list, list):
                all_cuisines.update(cuisine_list)
        return sorted(all_cuisines)

    def count(self) -> int:
        """Total number of restaurants."""
        return len(self.df)

    def sample(self, n: int = 5) -> List[Restaurant]:
        """Return n random restaurants (useful for debugging)."""
        sampled = self.df.sample(n=min(n, len(self.df)))
        return self._df_to_restaurants(sampled)

    # ── internals ──

    @staticmethod
    def _df_to_restaurants(df: pd.DataFrame) -> List[Restaurant]:
        """Convert DataFrame rows to Restaurant model instances."""
        restaurants: List[Restaurant] = []
        for _, row in df.iterrows():
            try:
                restaurant = Restaurant(
                    id=str(row.get("id", "")),
                    name=str(row.get("name", "")),
                    location=str(row.get("location", "")),
                    cuisines=row.get("cuisines", []) if isinstance(row.get("cuisines"), list) else [],
                    cost_for_two=int(row.get("cost_for_two", 0)),
                    rating=float(row.get("rating", 0.0)),
                    votes=int(row.get("votes", 0)),
                    rest_type=str(row.get("rest_type", "")) if pd.notna(row.get("rest_type")) else None,
                    budget_tier=str(row.get("budget_tier", "medium")),
                )
                restaurants.append(restaurant)
            except (ValueError, TypeError) as e:
                logger.debug("Skipping row due to conversion error: %s", e)
        return restaurants
