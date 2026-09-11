"""Data layer package for support_agent."""

from support_agent.data.loader import (
    DEFAULT_CSV_FILE,
    DEFAULT_PARQUET_FILE,
    REQUIRED_COLUMNS,
    load_cases,
    to_support_cases,
    validate_cases,
)
from support_agent.data.schema import (
    ABSENT_COLUMNS,
    CANONICAL_COLUMNS,
    SupportCase,
    TurnContext,
)

__all__ = [
    "TurnContext",
    "SupportCase",
    "CANONICAL_COLUMNS",
    "ABSENT_COLUMNS",
    "REQUIRED_COLUMNS",
    "DEFAULT_PARQUET_FILE",
    "DEFAULT_CSV_FILE",
    "load_cases",
    "validate_cases",
    "to_support_cases",
]
