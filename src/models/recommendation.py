"""
Recommendation data models — output schema for the recommendation engine.

Defines the Recommendation (single ranked restaurant) and
RecommendationResponse (full API response) models.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    """A single ranked restaurant recommendation with LLM explanation."""

    rank: int = Field(..., description="1-based rank in the recommendation list")
    name: str = Field(..., description="Restaurant name")
    cuisine: str = Field(..., description="Comma-separated cuisine string for display")
    rating: float = Field(..., description="Restaurant rating (0–5)")
    estimated_cost: int = Field(..., description="Approximate cost for two (INR)")
    explanation: str = Field(..., description="LLM-generated reasoning for this pick")


class RecommendationMetadata(BaseModel):
    """Metadata about the recommendation request for transparency."""

    candidates_considered: int = Field(
        ..., description="Number of restaurants sent to the LLM"
    )
    filters_applied: Dict = Field(
        default_factory=dict,
        description="Active filters (location, budget, etc.)",
    )
    model: str = Field(default="", description="LLM model identifier used")
    is_fallback: bool = Field(
        default=False,
        description="True if heuristic fallback was used instead of LLM",
    )


class RecommendationResponse(BaseModel):
    """Complete recommendation response returned to the UI / API."""

    summary: Optional[str] = Field(
        default=None,
        description="LLM-generated summary of the recommendations",
    )
    recommendations: List[Recommendation] = Field(
        default_factory=list,
        description="Ordered list of restaurant recommendations",
    )
    metadata: RecommendationMetadata = Field(
        ..., description="Request metadata for transparency"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Any warnings (e.g. constraint relaxation messages)",
    )
