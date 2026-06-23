"""
Restaurant filter — deterministic filtering and candidate selection.

Applies hard constraints (location, budget, rating, cuisine) before the LLM
to reduce token cost and hallucination risk.  Includes constraint relaxation
when no candidates match.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional

from src.config import settings
from src.data.repository import RestaurantRepository
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


@dataclass
class FilterResult:
    """
    Result of the filter pipeline, including metadata about what happened.

    Attributes:
        candidates: The filtered, sorted, capped list of restaurants.
        warnings: Any relaxation or informational messages for the user.
        filters_applied: Dict describing which filters were actually used.
        total_before_filter: Number of restaurants before filtering.
        relaxations: List of constraints that were relaxed (if any).
    """
    candidates: List[Restaurant] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    filters_applied: dict = field(default_factory=dict)
    total_before_filter: int = 0
    relaxations: List[str] = field(default_factory=list)


class CandidateSelector:
    """Caps result count and applies tie-breaking sort."""

    def __init__(self, max_candidates: int | None = None) -> None:
        self.max_candidates = max_candidates or settings.max_candidates

    def select(self, restaurants: List[Restaurant]) -> List[Restaurant]:
        """
        Sort by rating DESC → votes DESC, then cap at max_candidates.
        """
        sorted_list = sorted(
            restaurants,
            key=lambda r: (r.rating, r.votes),
            reverse=True,
        )
        return sorted_list[: self.max_candidates]


class RestaurantFilter:
    """
    Executes the deterministic filter pipeline:

        all restaurants
          → filter by location (case-insensitive)
          → filter by budget_tier
          → filter by min_rating
          → filter by cuisine (if provided)
          → sort + cap via CandidateSelector

    If zero candidates remain, relaxes constraints in order:
        cuisine → budget → min_rating
    """

    def __init__(
        self,
        repository: RestaurantRepository,
        max_candidates: int | None = None,
    ) -> None:
        self.repository = repository
        self.selector = CandidateSelector(max_candidates)

    def filter(self, prefs: UserPreferences) -> FilterResult:
        """
        Apply the full filter pipeline and return a FilterResult.

        This is the main entry point for Phase 2.
        """
        all_restaurants = self.repository.get_all()
        total = len(all_restaurants)

        logger.info(
            "Filtering %d restaurants for: location=%s, budget=%s, cuisine=%s, min_rating=%s",
            total, prefs.location, prefs.budget.value, prefs.cuisine, prefs.min_rating,
        )

        # Run pipeline with potential relaxation
        candidates, warnings, relaxations, filters_applied = self._filter_with_relaxation(
            all_restaurants, prefs
        )

        # Sort + cap
        candidates = self.selector.select(candidates)

        logger.info(
            "Filter result: %d candidates (relaxations: %s)",
            len(candidates), relaxations or "none",
        )

        return FilterResult(
            candidates=candidates,
            warnings=warnings,
            filters_applied=filters_applied,
            total_before_filter=total,
            relaxations=relaxations,
        )

    # ── internal pipeline ──

    def _filter_with_relaxation(
        self,
        restaurants: List[Restaurant],
        prefs: UserPreferences,
    ) -> tuple[List[Restaurant], List[str], List[str], dict]:
        """
        Try the full filter pipeline.  If zero results, relax constraints
        in order: cuisine → budget → min_rating.

        Returns:
            (candidates, warnings, relaxations, filters_applied)
        """
        warnings: List[str] = []
        relaxations: List[str] = []

        # Start with full constraints
        use_cuisine: Optional[str] = prefs.cuisine
        use_budget: Optional[str] = prefs.budget.value
        use_min_rating: float = prefs.min_rating

        # Attempt 1: all constraints
        candidates = self._apply_filters(
            restaurants, prefs.location, use_budget, use_min_rating, use_cuisine
        )
        filters_applied = self._build_filters_dict(
            prefs.location, use_budget, use_min_rating, use_cuisine
        )

        if candidates:
            return candidates, warnings, relaxations, filters_applied

        # ── Relaxation cascade ──

        # Relax 1: drop cuisine
        if use_cuisine:
            logger.info("No results — relaxing cuisine constraint")
            relaxations.append("cuisine")
            warnings.append(
                f"No restaurants matched cuisine '{use_cuisine}'. "
                f"Showing results for all cuisines."
            )
            use_cuisine = None
            candidates = self._apply_filters(
                restaurants, prefs.location, use_budget, use_min_rating, use_cuisine
            )
            filters_applied = self._build_filters_dict(
                prefs.location, use_budget, use_min_rating, use_cuisine
            )
            if candidates:
                return candidates, warnings, relaxations, filters_applied

        # Relax 2: drop budget
        if use_budget:
            logger.info("No results — relaxing budget constraint")
            relaxations.append("budget")
            warnings.append(
                f"No restaurants matched budget '{prefs.budget.value}'. "
                f"Showing results for all budgets."
            )
            use_budget = None
            candidates = self._apply_filters(
                restaurants, prefs.location, use_budget, use_min_rating, use_cuisine
            )
            filters_applied = self._build_filters_dict(
                prefs.location, use_budget, use_min_rating, use_cuisine
            )
            if candidates:
                return candidates, warnings, relaxations, filters_applied

        # Relax 3: drop min_rating (set to 0)
        if use_min_rating > 0.0:
            logger.info("No results — relaxing min_rating constraint")
            relaxations.append("min_rating")
            warnings.append(
                f"No restaurants matched min rating {prefs.min_rating}. "
                f"Showing results with any rating."
            )
            use_min_rating = 0.0
            candidates = self._apply_filters(
                restaurants, prefs.location, use_budget, use_min_rating, use_cuisine
            )
            filters_applied = self._build_filters_dict(
                prefs.location, use_budget, use_min_rating, use_cuisine
            )
            if candidates:
                return candidates, warnings, relaxations, filters_applied

        # Still nothing — no restaurants in that location at all
        warnings.append(
            f"No restaurants found for location '{prefs.location}'. "
            f"Try a different location."
        )
        return [], warnings, relaxations, filters_applied

    @staticmethod
    def _apply_filters(
        restaurants: List[Restaurant],
        location: str,
        budget: Optional[str],
        min_rating: float,
        cuisine: Optional[str],
    ) -> List[Restaurant]:
        """Apply all active filters in sequence."""
        result = restaurants

        # 1. Location (case-insensitive)
        location_lower = location.lower()
        result = [r for r in result if r.location.lower() == location_lower]

        # 2. Budget tier
        if budget:
            result = [r for r in result if r.budget_tier == budget]

        # 3. Min rating
        result = [r for r in result if r.rating >= min_rating]

        # 4. Cuisine (case-insensitive, check if cuisine in restaurant's cuisine list)
        if cuisine:
            cuisine_lower = cuisine.lower()
            result = [
                r for r in result
                if any(c.lower() == cuisine_lower for c in r.cuisines)
            ]

        return result

    @staticmethod
    def _build_filters_dict(
        location: str,
        budget: Optional[str],
        min_rating: float,
        cuisine: Optional[str],
    ) -> dict:
        """Build a dict of filters that were actually applied (for metadata)."""
        d: dict = {"location": location}
        if budget:
            d["budget"] = budget
        d["min_rating"] = min_rating
        if cuisine:
            d["cuisine"] = cuisine
        return d
