"""
Models package for Compair API.

This package contains Pydantic models for request/response validation.
"""

from models.model import (
    UserPreferences,
    CompareRequest,
    SaveComparisonRequest,
    ShareComparisonRequest,
    FollowUpRequest,
    ComparisonOutput
)

__all__ = [
    "UserPreferences",
    "CompareRequest",
    "SaveComparisonRequest",
    "ShareComparisonRequest",
    "FollowUpRequest",
    "ComparisonOutput",
]

