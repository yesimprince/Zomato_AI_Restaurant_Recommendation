"""
Data preprocessor — normalizes raw dataset rows to the canonical Restaurant schema.

Handles column renaming, type coercion, cuisine parsing, location normalization,
and budget tier derivation.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, Optional

import pandas as pd

from src.config import settings

logger = logging.getLogger(__name__)

# City alias map: common alternative spellings → canonical name
_LOCATION_ALIASES: Dict[str, str] = {
    "bengaluru": "Bangalore",
    "bombay": "Mumbai",
    "madras": "Chennai",
    "calcutta": "Kolkata",
    "poona": "Pune",
    "trivandrum": "Thiruvananthapuram",
    "cochin": "Kochi",
    "pondicherry": "Puducherry",
    "gurgaon": "Gurugram",
}


class DataPreprocessor:
    """
    Transform a raw Zomato DataFrame into cleaned, schema-compliant rows.

    The caller (DatasetLoader → Repository) passes in the raw DataFrame and
    receives back a cleaned DataFrame whose columns match the canonical
    Restaurant model.
    """

    def __init__(
        self,
        budget_thresholds: Optional[Dict[str, int]] = None,
        location_aliases: Optional[Dict[str, str]] = None,
    ) -> None:
        self.budget_thresholds = budget_thresholds or settings.budget_thresholds
        self.location_aliases = location_aliases or _LOCATION_ALIASES

    # ── public API ──

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Full preprocessing pipeline.

        Steps:
        1. Select & rename columns
        2. Parse cuisines into lists
        3. Coerce numeric types
        4. Normalize locations
        5. Derive budget_tier
        6. De-duplicate entries
        7. Assign stable id
        8. Drop rows with missing required values
        """
        logger.info("Starting preprocessing on %d rows …", len(df))

        df = self._select_and_rename(df)
        df = self._parse_cuisines(df)
        df = self._coerce_numerics(df)
        df = self._normalize_locations(df)
        df = self._derive_budget_tier(df)
        df = self._deduplicate(df)
        df = self._assign_ids(df)
        df = self._drop_invalid(df)

        logger.info("Preprocessing complete: %d clean rows", len(df))
        return df.reset_index(drop=True)

    # ── pipeline steps ──

    def _select_and_rename(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map raw dataset columns to canonical names.

        The Zomato HF dataset uses these columns (inspected from the dataset):
          - name, online_order, book_table, rate, votes, approx_cost(for two people),
            listed_in(type), listed_in(city), rest_type, cuisines, location, ...

        We rename the relevant ones to our canonical schema.
        """
        # Build a flexible column mapping — handles variations in naming
        column_map = self._build_column_map(df.columns.tolist())

        # Keep only the columns we can map
        available = {raw: canon for raw, canon in column_map.items() if raw in df.columns}
        if not available:
            raise ValueError(
                f"Could not find expected columns in dataset. "
                f"Available columns: {df.columns.tolist()}"
            )

        df = df[list(available.keys())].rename(columns=available)

        logger.info("Selected & renamed columns: %s", list(df.columns))
        return df

    @staticmethod
    def _build_column_map(actual_columns: list[str]) -> Dict[str, str]:
        """
        Build a mapping from raw column names to canonical names.

        Handles the known Zomato dataset schema plus common variations.
        """
        # Normalize column names for matching (lowercase, strip)
        lower_cols = {c.lower().strip(): c for c in actual_columns}

        mapping: Dict[str, str] = {}

        # name
        for candidate in ["name", "restaurant name", "restaurant_name"]:
            if candidate in lower_cols:
                mapping[lower_cols[candidate]] = "name"
                break

        # location / city
        for candidate in ["location", "city", "listed_in(city)", "listed_in (city)"]:
            if candidate in lower_cols:
                mapping[lower_cols[candidate]] = "location"
                break

        # cuisines
        for candidate in ["cuisines", "cuisine", "cuisine type"]:
            if candidate in lower_cols:
                mapping[lower_cols[candidate]] = "cuisines"
                break

        # cost for two
        for candidate in [
            "approx_cost(for two people)",
            "approx_cost (for two people)",
            "average_cost_for_two",
            "cost_for_two",
            "cost for two",
        ]:
            if candidate in lower_cols:
                mapping[lower_cols[candidate]] = "cost_for_two"
                break

        # rating
        for candidate in ["rate", "rating", "aggregate_rating", "aggregate rating"]:
            if candidate in lower_cols:
                mapping[lower_cols[candidate]] = "rating"
                break

        # votes
        for candidate in ["votes", "num_votes", "vote count"]:
            if candidate in lower_cols:
                mapping[lower_cols[candidate]] = "votes"
                break

        # restaurant type
        for candidate in ["rest_type", "restaurant_type", "type", "listed_in(type)", "listed_in (type)"]:
            if candidate in lower_cols:
                mapping[lower_cols[candidate]] = "rest_type"
                break

        return mapping

    def _parse_cuisines(self, df: pd.DataFrame) -> pd.DataFrame:
        """Split comma-separated cuisine strings into lists of trimmed strings."""
        if "cuisines" not in df.columns:
            df["cuisines"] = [[] for _ in range(len(df))]
            return df

        def _split(val):
            if pd.isna(val) or not isinstance(val, str) or val.strip() == "":
                return []
            return [c.strip() for c in val.split(",") if c.strip()]

        df = df.copy()
        df["cuisines"] = df["cuisines"].apply(_split)
        return df

    def _coerce_numerics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Coerce rating and cost_for_two to numeric types, marking failures as NaN."""
        df = df.copy()

        # Rating — handle strings like "4.1/5", "NEW", "-"
        if "rating" in df.columns:
            df["rating"] = df["rating"].apply(self._parse_rating)

        # Cost — handle strings like "₹800", "1,200", etc.
        if "cost_for_two" in df.columns:
            df["cost_for_two"] = df["cost_for_two"].apply(self._parse_cost)

        # Votes
        if "votes" in df.columns:
            df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype(int)

        return df

    @staticmethod
    def _parse_rating(val) -> float | None:
        """Extract a numeric rating from various string formats."""
        if pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            return float(val)
        val = str(val).strip()
        # Handle "4.1/5" → 4.1
        val = val.split("/")[0].strip()
        # Handle "NEW", "-", "" → None
        try:
            result = float(val)
            return result if 0.0 <= result <= 5.0 else None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_cost(val) -> int | None:
        """Extract integer cost from strings like '₹800', '1,200', etc."""
        if pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            return int(val)
        val = str(val).strip()
        # Remove currency symbols and commas
        val = re.sub(r"[₹$,\s]", "", val)
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return None

    def _normalize_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Trim, title-case, and apply alias mapping to location strings."""
        if "location" not in df.columns:
            return df

        df = df.copy()

        def _normalize(val):
            if pd.isna(val) or not isinstance(val, str):
                return None
            val = val.strip().title()
            # Check alias map (case-insensitive)
            lowered = val.lower()
            if lowered in self.location_aliases:
                return self.location_aliases[lowered]
            return val

        df["location"] = df["location"].apply(_normalize)
        return df

    def _derive_budget_tier(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign 'low', 'medium', or 'high' based on cost_for_two thresholds."""
        if "cost_for_two" not in df.columns:
            df["budget_tier"] = "medium"
            return df

        low_max = self.budget_thresholds.get("low", 500)
        med_max = self.budget_thresholds.get("medium", 1500)

        df = df.copy()

        def _tier(cost):
            if pd.isna(cost):
                return "medium"  # default when cost is unknown
            if cost <= low_max:
                return "low"
            if cost <= med_max:
                return "medium"
            return "high"

        df["budget_tier"] = df["cost_for_two"].apply(_tier)
        return df

    def _deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        De-duplicate restaurant entries (same name + location).
        Keep the entry with the highest votes.
        """
        if df.empty:
            return df

        # Sort by votes descending so that drop_duplicates keeps the one with the highest votes
        df = df.sort_values(by="votes", ascending=False)

        before = len(df)
        df = df.drop_duplicates(subset=["name", "location"], keep="first")
        dropped = before - len(df)
        if dropped > 0:
            logger.info("Deduplicated %d duplicate restaurant entries", dropped)

        return df.reset_index(drop=True)

    def _assign_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign a stable string id based on the DataFrame index."""
        df = df.copy()
        df["id"] = df.index.astype(str)
        return df

    def _drop_invalid(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop rows missing required fields (name, location, rating, cost_for_two)."""
        required = ["name", "location", "rating", "cost_for_two"]
        before = len(df)
        df = df.dropna(subset=[c for c in required if c in df.columns])
        dropped = before - len(df)
        if dropped:
            logger.warning("Dropped %d rows with missing required values", dropped)
        return df
