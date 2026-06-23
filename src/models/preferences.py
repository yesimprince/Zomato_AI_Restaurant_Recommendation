"""
User preferences model — input validation and normalization.

Defines the UserPreferences model that captures what the user is looking for,
plus PreferenceValidator and PreferenceNormalizer utilities.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# ── Location alias map (shared with preprocessor for consistency) ──

_LOCATION_ALIASES = {
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


class BudgetTier(str, Enum):
    """Valid budget tier values."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserPreferences(BaseModel):
    """
    Validated, normalized user preferences for restaurant recommendations.

    Required fields: location, budget, min_rating.
    Optional fields: cuisine, additional (free text for LLM).
    """

    location: str = Field(
        ...,
        min_length=1,
        description="City or locality (required)",
    )
    budget: BudgetTier = Field(
        ...,
        description="Budget tier: 'low', 'medium', or 'high'",
    )
    cuisine: Optional[str] = Field(
        default=None,
        description="Preferred cuisine (optional, e.g. 'Italian')",
    )
    min_rating: float = Field(
        default=3.5,
        ge=0.0,
        le=5.0,
        description="Minimum acceptable restaurant rating (0.0–5.0)",
    )
    additional: Optional[str] = Field(
        default=None,
        description="Free-text preferences passed to the LLM (e.g. 'family-friendly, outdoor seating')",
    )

    # ── validators ──

    @field_validator("location", mode="before")
    @classmethod
    def normalize_location(cls, v: str) -> str:
        """Trim whitespace, title-case, and apply alias mapping."""
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Location must be a non-empty string")
        v = v.strip().title()
        lowered = v.lower()
        return _LOCATION_ALIASES.get(lowered, v)

    @field_validator("budget", mode="before")
    @classmethod
    def normalize_budget(cls, v: str) -> str:
        """Accept case-insensitive budget values."""
        if isinstance(v, BudgetTier):
            return v
        if isinstance(v, str):
            return v.strip().lower()
        raise ValueError("Budget must be one of: low, medium, high")

    @field_validator("cuisine", mode="before")
    @classmethod
    def normalize_cuisine(cls, v: Optional[str]) -> Optional[str]:
        """Trim and title-case the cuisine string."""
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Cuisine must be a string or None")
        v = v.strip()
        return v.title() if v else None

    @field_validator("additional", mode="before")
    @classmethod
    def clean_additional(cls, v: Optional[str]) -> Optional[str]:
        """Trim free-text; treat empty strings as None."""
        if v is None:
            return None
        if not isinstance(v, str):
            return None
        v = v.strip()
        return v if v else None

    def to_display_dict(self) -> dict:
        """Return a clean dict of applied preferences for display above results."""
        d = {
            "location": self.location,
            "budget": self.budget.value,
            "min_rating": self.min_rating,
        }
        if self.cuisine:
            d["cuisine"] = self.cuisine
        if self.additional:
            d["additional"] = self.additional
        return d


class PreferenceValidator:
    """
    Validates user preferences against the available dataset values.

    Provides richer feedback than Pydantic alone — e.g. suggesting
    valid locations when the user enters an unknown one.
    """

    def __init__(self, known_locations: List[str], known_cuisines: List[str]) -> None:
        self._locations = {loc.lower(): loc for loc in known_locations}
        self._cuisines = {cui.lower(): cui for cui in known_cuisines}

    def validate_location(self, location: str) -> tuple[bool, str, List[str]]:
        """
        Check if the location exists in the dataset.

        Returns:
            (is_valid, canonical_name, suggestions)
        """
        normalized = location.strip().lower()

        # Exact match
        if normalized in self._locations:
            return True, self._locations[normalized], []

        # Partial / substring match for suggestions
        suggestions = [
            canonical
            for key, canonical in self._locations.items()
            if normalized in key or key in normalized
        ]

        if suggestions:
            return False, location, suggestions[:5]

        # No match at all — return all locations as hints
        return False, location, sorted(self._locations.values())[:10]

    def validate_cuisine(self, cuisine: str) -> tuple[bool, str, List[str]]:
        """
        Check if the cuisine exists in the dataset.

        Returns:
            (is_valid, canonical_name, suggestions)
        """
        normalized = cuisine.strip().lower()

        # Exact match
        if normalized in self._cuisines:
            return True, self._cuisines[normalized], []

        # Partial match
        suggestions = [
            canonical
            for key, canonical in self._cuisines.items()
            if normalized in key or key in normalized
        ]

        if suggestions:
            return False, cuisine, suggestions[:5]

        return False, cuisine, sorted(self._cuisines.values())[:10]

    def validate(self, prefs: UserPreferences) -> List[str]:
        """
        Full validation against dataset.

        Returns a list of warning messages (empty if everything is valid).
        """
        warnings: List[str] = []

        is_valid, _, suggestions = self.validate_location(prefs.location)
        if not is_valid:
            warnings.append(
                f"Location '{prefs.location}' not found in dataset. "
                f"Did you mean: {', '.join(suggestions)}?"
            )

        if prefs.cuisine:
            is_valid, _, suggestions = self.validate_cuisine(prefs.cuisine)
            if not is_valid:
                warnings.append(
                    f"Cuisine '{prefs.cuisine}' not found in dataset. "
                    f"Similar options: {', '.join(suggestions)}"
                )

        return warnings
