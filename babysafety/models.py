"""Data models for BabySafety."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Rating(Enum):
    SAFE = "safe"
    CAUTION = "caution"
    AVOID = "avoid"
    INSUFFICIENT_DATA = "insufficient_data"


class Confidence(Enum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    INSUFFICIENT = "insufficient"


class Stage(Enum):
    PREGNANCY = "pregnancy"
    NURSING = "nursing"
    BABY = "baby"


@dataclass
class Source:
    """A citation, either a reference to sources.yaml or inline."""
    ref: str | None = None
    type: str | None = None
    org: str | None = None
    title: str | None = None
    authors: str | None = None
    journal: str | None = None
    year: int | None = None
    doi: str | None = None
    url: str | None = None
    finding: str | None = None
    note: str | None = None


@dataclass
class StageSafety:
    """Safety assessment for a single life stage."""
    rating: Rating
    summary: str
    details: str = ""
    dose_dependent: bool = False
    exposure_route: str = "topical"
    min_safe_age_months: int | None = None


@dataclass
class Alternative:
    """A safer alternative ingredient."""
    name: str
    id: str | None = None
    note: str = ""


@dataclass
class Ingredient:
    """Full ingredient entry from the knowledge base."""
    id: str
    name: str
    aliases: list[str] = field(default_factory=list)
    cas_number: str | None = None
    category: str = ""
    product_types: list[str] = field(default_factory=list)
    safety: dict[str, StageSafety] = field(default_factory=dict)
    sources: list[Source] = field(default_factory=list)
    safer_alternatives: list[Alternative] = field(default_factory=list)
    notes: str = ""
    last_reviewed: str = ""
    confidence: Confidence = Confidence.INSUFFICIENT


@dataclass
class ParsedIngredient:
    """An ingredient parsed from a product label."""
    raw: str
    name: str
    secondary_names: list[str] = field(default_factory=list)
    concentration: str | None = None
    section: str = "general"
    position: int = 0


@dataclass
class MatchResult:
    """Result of matching a parsed ingredient to the knowledge base."""
    parsed: ParsedIngredient
    ingredient: Ingredient | None = None
    matched_via: str = ""  # "exact", "normalized", "alias", "class", ""
