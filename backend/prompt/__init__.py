"""
Prompt module for CompareMate API.

This package contains prompt templates used by the LangChain LLM chains.
"""

from prompt.prompt import (
    get_comparison_prompt,
    get_followup_prompt,
    get_winner_instructions_with_preferences,
    get_winner_instructions_without_preferences
)

__all__ = [
    "get_comparison_prompt",
    "get_followup_prompt",
    "get_winner_instructions_with_preferences",
    "get_winner_instructions_without_preferences",
]

