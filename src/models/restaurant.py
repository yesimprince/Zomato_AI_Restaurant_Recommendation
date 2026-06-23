"""
Restaurant data model — canonical schema.

Every restaurant record flowing through the system is represented by this
Pydantic model.  Raw dataset rows are mapped into this shape by the
DataPreprocessor.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Restaurant(BaseModel):
    """Canonical restaurant record used across all layers."""

    id: str = Field(
        ...,
        description="Stable identifier (dataset index as string)",
    )
    name: str = Field(
        ...,
        description="Restaurant name",
    )
    location: str = Field(
        ...,
        description="City or locality (normalized, title-case)",
    )
    cuisines: List[str] = Field(
        default_factory=list,
        description="List of cuisine tags, e.g. ['Italian', 'Continental']",
    )
    cost_for_two: int = Field(
        ...,
        description="Approximate cost for two people (INR)",
    )
    rating: float = Field(
        ...,
        description="Aggregate rating on a 0–5 scale",
    )
    votes: int = Field(
        default=0,
        description="Number of user votes / reviews",
    )
    rest_type: Optional[str] = Field(
        default=None,
        description="Restaurant type, e.g. 'Casual Dining', 'Café'",
    )
    budget_tier: str = Field(
        ...,
        description="Derived tier: 'low', 'medium', or 'high'",
    )

    class Config:
        frozen = True  # immutable after creation

    @property
    def cuisines_display(self) -> str:
        """Comma-separated cuisine string for UI display."""
        return ", ".join(self.cuisines) if self.cuisines else "N/A"
