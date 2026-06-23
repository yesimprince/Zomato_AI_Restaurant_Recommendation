"""
Prompt builder — constructs structured LLM prompts for restaurant ranking.

Builds a system prompt + user prompt that instructs the LLM to rank
candidates from the provided list and return structured JSON.
"""

from __future__ import annotations

import json
import logging
from typing import List

from src.config import settings
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Constructs structured prompts for the restaurant recommendation LLM.

    The prompt has four logical sections:
    1. System — role, output format, constraints
    2. User preferences — serialized user input
    3. Candidates — compact JSON array of filtered restaurants
    4. Task — ranking instructions with output schema
    """

    def __init__(self, top_k: int | None = None) -> None:
        self.top_k = top_k or settings.top_k

    def build(
        self,
        prefs: UserPreferences,
        candidates: List[Restaurant],
    ) -> tuple[str, str]:
        """
        Build system and user prompts.

        Returns:
            (system_prompt, user_prompt)
        """
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(prefs, candidates)

        logger.info(
            "Built prompt: %d candidates, top_k=%d, user_prompt_len=%d chars",
            len(candidates), self.top_k, len(user_prompt),
        )

        return system_prompt, user_prompt

    def _build_system_prompt(self) -> str:
        """System-level instructions for the LLM."""
        return (
            "You are an expert restaurant recommendation assistant for Indian cities.\n"
            "\n"
            "RULES:\n"
            "1. You MUST only recommend restaurants from the CANDIDATES list provided.\n"
            "2. Do NOT invent or fabricate any restaurant that is not in the list.\n"
            "3. Rank the restaurants based on how well they match the user's preferences.\n"
            "4. Consider the user's 'additional' preferences as soft signals for ranking.\n"
            "5. Provide a clear, concise explanation for each recommendation.\n"
            "6. Return your response as valid JSON matching the exact schema below.\n"
            "\n"
            "OUTPUT JSON SCHEMA:\n"
            "{\n"
            '  "summary": "A brief 1-2 sentence summary of the recommendations",\n'
            '  "recommendations": [\n'
            "    {\n"
            '      "id": "restaurant id from candidates",\n'
            '      "rank": 1,\n'
            '      "explanation": "Why this restaurant is recommended"\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "\n"
            f"Return exactly {self.top_k} recommendations (or fewer if not enough candidates).\n"
            "Sort by rank ascending (1 = best match).\n"
            "Each explanation should be 1-2 sentences, specific to the user's preferences."
        )

    def _build_user_prompt(
        self,
        prefs: UserPreferences,
        candidates: List[Restaurant],
    ) -> str:
        """User-level prompt with preferences and candidate data."""

        # Serialize preferences
        prefs_dict = prefs.to_display_dict()

        # Serialize candidates as compact JSON
        candidates_data = [
            {
                "id": r.id,
                "name": r.name,
                "location": r.location,
                "cuisines": r.cuisines_display,
                "cost_for_two": r.cost_for_two,
                "rating": r.rating,
                "votes": r.votes,
                "type": r.rest_type or "N/A",
            }
            for r in candidates
        ]

        sections = [
            "USER PREFERENCES:",
            json.dumps(prefs_dict, indent=2),
            "",
            f"CANDIDATES ({len(candidates_data)} restaurants):",
            json.dumps(candidates_data, indent=2),
            "",
            "TASK:",
            f"Rank the top {self.top_k} restaurants from the CANDIDATES list above "
            f"that best match the user's preferences. "
            f"Return valid JSON matching the schema from your instructions.",
        ]

        return "\n".join(sections)
