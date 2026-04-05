"""Match parsed ingredient names to the knowledge base."""

from __future__ import annotations

import re

from .database import Database
from .models import Ingredient, MatchResult, ParsedIngredient


def _normalize(name: str) -> str:
    """Normalize a name for comparison: lowercase, strip hyphens/spaces/punctuation."""
    name = name.lower()
    name = re.sub(r"[-\s_.,]+", "", name)
    return name


def _try_exact(db: Database, name: str) -> Ingredient | None:
    """Exact case-insensitive lookup against the alias index."""
    return db.lookup_by_name(name)


def _try_normalized(db: Database, name: str) -> Ingredient | None:
    """Normalized lookup: strip hyphens, spaces, etc."""
    target = _normalize(name)
    for alias, ingredient_id in db.alias_index.items():
        if _normalize(alias) == target:
            return db.ingredients.get(ingredient_id)
    return None


def _try_contains(db: Database, name: str) -> Ingredient | None:
    """Check if any known alias is contained in the parsed name, or vice versa."""
    name_norm = _normalize(name)

    # Only try contains matching for names longer than 4 chars to avoid false positives
    if len(name_norm) < 5:
        return None

    for alias, ingredient_id in db.alias_index.items():
        alias_norm = _normalize(alias)
        # Skip very short aliases for contains matching
        if len(alias_norm) < 5:
            continue
        if alias_norm in name_norm or name_norm in alias_norm:
            return db.ingredients.get(ingredient_id)

    return None


def match_ingredient(db: Database, parsed: ParsedIngredient) -> MatchResult:
    """Try to match a parsed ingredient to the knowledge base.

    Tries multiple matching strategies in order of confidence:
    1. Exact match on primary name
    2. Exact match on secondary names
    3. Normalized match on primary name
    4. Contains match on primary name
    """
    # 1. Exact match on primary name
    ingredient = _try_exact(db, parsed.name)
    if ingredient:
        return MatchResult(parsed=parsed, ingredient=ingredient, matched_via="exact")

    # 2. Exact match on secondary names
    for secondary in parsed.secondary_names:
        ingredient = _try_exact(db, secondary)
        if ingredient:
            return MatchResult(parsed=parsed, ingredient=ingredient, matched_via="alias")

    # 3. Normalized match on primary name
    ingredient = _try_normalized(db, parsed.name)
    if ingredient:
        return MatchResult(parsed=parsed, ingredient=ingredient, matched_via="normalized")

    # 4. Normalized match on secondary names
    for secondary in parsed.secondary_names:
        ingredient = _try_normalized(db, secondary)
        if ingredient:
            return MatchResult(parsed=parsed, ingredient=ingredient, matched_via="normalized")

    # 5. Contains match
    ingredient = _try_contains(db, parsed.name)
    if ingredient:
        return MatchResult(parsed=parsed, ingredient=ingredient, matched_via="contains")

    # No match found
    return MatchResult(parsed=parsed)


def match_all(db: Database, parsed_list: list[ParsedIngredient]) -> list[MatchResult]:
    """Match all parsed ingredients against the database."""
    return [match_ingredient(db, p) for p in parsed_list]
