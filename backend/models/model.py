"""
Pydantic models for the Compair API.

This module contains all Pydantic models used for request/response validation
and data serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class UserPreferences(BaseModel):
    """User preferences for personalized comparisons."""
    priorities: Optional[List[str]] = Field(
        default=None,
        description="Features user cares about most"
    )
    budget: Optional[str] = Field(
        default=None, 
        description="Budget constraint"
    )
    use_case: Optional[str] = Field(
        default=None, 
        description="How user plans to use it"
    )


class CompareRequest(BaseModel):
    """Request model for comparing items."""
    category: str
    items: List[str]
    criteria: Optional[str] = None
    user_preferences: Optional[UserPreferences] = None


class SaveComparisonRequest(BaseModel):
    """Request model for saving a comparison."""
    user_id: str
    category: str
    items: List[str]
    result: dict


class ShareComparisonRequest(BaseModel):
    """Request model for sharing a comparison."""
    category: str
    items: List[str]
    result: dict
    user_id: Optional[str] = None


class FollowUpRequest(BaseModel):
    """Request model for follow-up questions."""
    comparison_id: str
    question: str


class ComparisonOutput(BaseModel):
    """Output model for comparison results."""
    introduction: Optional[str] = Field(
        default=None, 
        description="2-3 sentence introduction to the comparison"
    )
    table: Optional[List[dict]] = Field(
        default=None, 
        description="List of comparison features as dictionaries"
    )
    pros: Optional[List[str]] = Field(
        default=None, 
        description="List of 3-5 specific advantages"
    )
    cons: Optional[List[str]] = Field(
        default=None, 
        description="List of 3-5 specific disadvantages"
    )
    recommendation: Optional[str] = Field(
        default=None, 
        description="Clear, balanced recommendation"
    )
    personalized_winner: Optional[str] = Field(
        default=None, 
        description="Winner based on user preferences"
    )
    winner_reason: Optional[str] = Field(
        default=None,
        description="Explanation of why this item won"
    )
    message: Optional[str] = Field(
        default=None, 
        description="Error or informational message"
    )

