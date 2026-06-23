"""
API Schemas — Pydantic models for request and response validation.
"""

from typing import List

from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(..., description="API Status")
    dataset_loaded: bool = Field(..., description="Is the dataset loaded in repository")
    restaurant_count: int = Field(0, description="Number of restaurants loaded")

class LocationsResponse(BaseModel):
    locations: List[str] = Field(..., description="List of unique location names")

class CuisinesResponse(BaseModel):
    cuisines: List[str] = Field(..., description="List of unique cuisine names")
