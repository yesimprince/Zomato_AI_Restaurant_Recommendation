"""
Recommendation service — orchestrator, response parser, and enricher.

Wires together:
    Filter → PromptBuilder → LLMClient → ResponseParser → Enricher

Falls back to heuristic ranking if the LLM is unavailable.
"""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional

from src.config import settings
from src.data.repository import RestaurantRepository
from src.models.preferences import UserPreferences
from src.models.recommendation import (
    Recommendation,
    RecommendationMetadata,
    RecommendationResponse,
)
from src.models.restaurant import Restaurant
from src.services.filter import FilterResult, RestaurantFilter
from src.services.llm_client import LLMClient, LLMError
from src.services.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


# ── Response Parser ──


class ParseError(Exception):
    """Raised when LLM JSON output cannot be parsed into expected schema."""
    pass


class ResponseParser:
    """
    Parses raw JSON text from the LLM into a structured dict.

    Expected LLM output:
    {
        "summary": "...",
        "recommendations": [
            {"id": "...", "rank": 1, "explanation": "..."},
            ...
        ]
    }
    """

    @staticmethod
    def parse(raw_json: str) -> Dict:
        """
        Parse and validate the LLM JSON response.

        Returns:
            Dict with 'summary' and 'recommendations' keys.

        Raises:
            ParseError: If JSON is invalid or missing required fields.
        """
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            raise ParseError(f"Invalid JSON from LLM: {e}") from e

        if not isinstance(data, dict):
            raise ParseError(f"Expected JSON object, got {type(data).__name__}")

        # Validate recommendations list exists
        recs = data.get("recommendations")
        if not isinstance(recs, list):
            raise ParseError("Missing or invalid 'recommendations' array in LLM response")

        # Validate each recommendation has required fields
        for i, rec in enumerate(recs):
            if not isinstance(rec, dict):
                raise ParseError(f"Recommendation {i} is not a dict")
            if "id" not in rec and "name" not in rec:
                raise ParseError(
                    f"Recommendation {i} missing both 'id' and 'name' — "
                    f"cannot match to a candidate"
                )

        return data


# ── Recommendation Enricher ──


class RecommendationEnricher:
    """
    Joins LLM-returned ranks and explanations with full Restaurant records.

    Matches by 'id' first, then falls back to name matching.
    """

    @staticmethod
    def enrich(
        parsed: Dict,
        candidates: List[Restaurant],
    ) -> tuple[Optional[str], List[Recommendation]]:
        """
        Merge LLM output with candidate restaurant data.

        Returns:
            (summary, list_of_Recommendation)
        """
        summary = parsed.get("summary")
        llm_recs = parsed.get("recommendations", [])

        # Build lookup maps
        by_id = {r.id: r for r in candidates}
        by_name = {r.name.lower(): r for r in candidates}

        enriched: List[Recommendation] = []

        for llm_rec in llm_recs:
            # Find the matching restaurant
            restaurant = None

            # Try by id first
            rec_id = str(llm_rec.get("id", ""))
            if rec_id and rec_id in by_id:
                restaurant = by_id[rec_id]

            # Fallback: match by name
            if not restaurant:
                rec_name = str(llm_rec.get("name", "")).lower()
                if rec_name and rec_name in by_name:
                    restaurant = by_name[rec_name]

            if restaurant:
                enriched.append(
                    Recommendation(
                        rank=llm_rec.get("rank", len(enriched) + 1),
                        name=restaurant.name,
                        cuisine=restaurant.cuisines_display,
                        rating=restaurant.rating,
                        estimated_cost=restaurant.cost_for_two,
                        explanation=llm_rec.get("explanation", "Recommended based on your preferences."),
                    )
                )
            else:
                logger.warning(
                    "LLM recommended unknown restaurant (id=%s, name=%s) — skipping",
                    llm_rec.get("id"), llm_rec.get("name"),
                )

        # Re-number ranks sequentially
        for i, rec in enumerate(enriched, 1):
            rec.rank = i

        return summary, enriched


# ── Recommendation Service (Orchestrator) ──


class RecommendationService:
    """
    End-to-end recommendation orchestrator.

    Pipeline:
        UserPreferences
          → RestaurantFilter.filter(prefs)        → candidates
          → PromptBuilder.build(prefs, candidates) → prompt
          → LLMClient.complete(prompt)             → raw JSON
          → ResponseParser.parse(raw)              → parsed response
          → RecommendationEnricher.enrich(parsed)  → RecommendationResponse

    Falls back to heuristic top-K if LLM fails.
    """

    def __init__(
        self,
        repository: Optional[RestaurantRepository] = None,
    ) -> None:
        self.repository = repository or RestaurantRepository()
        self.filter = RestaurantFilter(self.repository)
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient()
        self.parser = ResponseParser()
        self.enricher = RecommendationEnricher()

    def recommend(self, prefs: UserPreferences) -> RecommendationResponse:
        """
        Generate restaurant recommendations for the given preferences.

        This is the main entry point for Phase 3.
        """
        # Step 1: Filter candidates
        filter_result: FilterResult = self.filter.filter(prefs)

        if not filter_result.candidates:
            return self._empty_response(filter_result)

        # Step 2 & 3: Try LLM path
        try:
            return self._llm_recommend(prefs, filter_result)
        except (LLMError, ParseError) as e:
            logger.warning("LLM path failed: %s — falling back to heuristic", e)
            return self._fallback_recommend(filter_result)

    def _llm_recommend(
        self,
        prefs: UserPreferences,
        filter_result: FilterResult,
    ) -> RecommendationResponse:
        """Full LLM-powered recommendation path."""

        # Build prompt
        system_prompt, user_prompt = self.prompt_builder.build(
            prefs, filter_result.candidates
        )

        # Call LLM
        raw_json = self.llm_client.complete(system_prompt, user_prompt)

        # Parse response
        parsed = self.parser.parse(raw_json)

        # Enrich with full restaurant data
        summary, recommendations = self.enricher.enrich(
            parsed, filter_result.candidates
        )

        return RecommendationResponse(
            summary=summary,
            recommendations=recommendations,
            metadata=RecommendationMetadata(
                candidates_considered=len(filter_result.candidates),
                filters_applied=filter_result.filters_applied,
                model=self.llm_client.model,
                is_fallback=False,
            ),
            warnings=filter_result.warnings,
        )

    def _fallback_recommend(
        self,
        filter_result: FilterResult,
    ) -> RecommendationResponse:
        """
        Heuristic fallback: return top-K by rating with generic explanations.

        Used when the LLM is unavailable or returns unparseable output.
        """
        top_k = settings.top_k
        candidates = filter_result.candidates[:top_k]

        recommendations = [
            Recommendation(
                rank=i + 1,
                name=r.name,
                cuisine=r.cuisines_display,
                rating=r.rating,
                estimated_cost=r.cost_for_two,
                explanation="Ranked by rating and popularity. AI explanation unavailable.",
            )
            for i, r in enumerate(candidates)
        ]

        warnings = filter_result.warnings + [
            "⚠️ AI-powered explanations are temporarily unavailable. "
            "Results are ranked by rating and popularity."
        ]

        return RecommendationResponse(
            summary="Top restaurants ranked by rating and popularity (AI unavailable).",
            recommendations=recommendations,
            metadata=RecommendationMetadata(
                candidates_considered=len(filter_result.candidates),
                filters_applied=filter_result.filters_applied,
                model="heuristic-fallback",
                is_fallback=True,
            ),
            warnings=warnings,
        )

    @staticmethod
    def _empty_response(filter_result: FilterResult) -> RecommendationResponse:
        """Return an empty response when no candidates survive filtering."""
        return RecommendationResponse(
            summary=None,
            recommendations=[],
            metadata=RecommendationMetadata(
                candidates_considered=0,
                filters_applied=filter_result.filters_applied,
                model="none",
                is_fallback=False,
            ),
            warnings=filter_result.warnings,
        )
