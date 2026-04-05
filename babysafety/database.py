"""Load and query the compiled ingredient database."""

from __future__ import annotations

import json
from pathlib import Path

from .models import (
    Alternative,
    Confidence,
    EvidenceStrength,
    Ingredient,
    Rating,
    Source,
    Stage,
    StageSafety,
)

COMPILED_DIR = Path(__file__).parent.parent / "data" / "compiled"


def _parse_source(raw: dict) -> Source:
    return Source(
        ref=raw.get("ref"),
        type=raw.get("type"),
        org=raw.get("org"),
        title=raw.get("title"),
        authors=raw.get("authors"),
        journal=raw.get("journal"),
        year=raw.get("year"),
        doi=raw.get("doi"),
        url=raw.get("url"),
        finding=raw.get("finding"),
        note=raw.get("note"),
        primary=raw.get("primary", False),
    )


def _parse_stage_safety(raw: dict) -> StageSafety:
    evidence_str = raw.get("evidence_strength", "moderate")
    evidence_strength = (
        EvidenceStrength(evidence_str)
        if evidence_str in [e.value for e in EvidenceStrength]
        else EvidenceStrength.MODERATE
    )
    return StageSafety(
        rating=Rating(raw["rating"]),
        summary=raw.get("summary", "").strip(),
        details=raw.get("details", "").strip(),
        dose_dependent=raw.get("dose_dependent", False),
        exposure_route=raw.get("exposure_route", "topical"),
        min_safe_age_months=raw.get("min_safe_age_months"),
        evidence_strength=evidence_strength,
    )


def _parse_ingredient(raw: dict) -> Ingredient:
    safety = {}
    for stage_name in ("pregnancy", "nursing", "baby"):
        if stage_name in raw.get("safety", {}):
            safety[stage_name] = _parse_stage_safety(raw["safety"][stage_name])

    sources = [_parse_source(s) for s in raw.get("sources", [])]
    alternatives = [
        Alternative(name=a["name"], id=a.get("id"), note=a.get("note", ""))
        for a in raw.get("safer_alternatives", [])
    ]

    # Accept the new `rating_confidence` field, falling back to the legacy
    # `confidence` key for YAML files that haven't been migrated yet.
    conf_str = raw.get("rating_confidence", raw.get("confidence", "moderate"))
    rating_confidence = (
        Confidence(conf_str)
        if conf_str in [c.value for c in Confidence]
        else Confidence.MODERATE
    )

    return Ingredient(
        id=raw["id"],
        name=raw["name"],
        aliases=raw.get("aliases", []),
        cas_number=raw.get("cas_number"),
        category=raw.get("category", ""),
        product_types=raw.get("product_types", []),
        safety=safety,
        sources=sources,
        safer_alternatives=alternatives,
        notes=raw.get("notes", "").strip(),
        last_reviewed=raw.get("last_reviewed", ""),
        rating_confidence=rating_confidence,
    )


class Database:
    """In-memory ingredient database loaded from compiled JSON."""

    def __init__(self) -> None:
        self.ingredients: dict[str, Ingredient] = {}
        self.alias_index: dict[str, str] = {}

    @classmethod
    def load(cls) -> Database:
        db = cls()
        ingredients_path = COMPILED_DIR / "ingredients.json"
        alias_path = COMPILED_DIR / "alias_index.json"

        if not ingredients_path.exists():
            raise FileNotFoundError(
                "Compiled database not found. Run 'babysafety compile' first."
            )

        with open(ingredients_path) as f:
            raw_ingredients = json.load(f)
        with open(alias_path) as f:
            db.alias_index = json.load(f)

        for ingredient_id, raw in raw_ingredients.items():
            db.ingredients[ingredient_id] = _parse_ingredient(raw)

        return db

    def lookup_by_id(self, ingredient_id: str) -> Ingredient | None:
        return self.ingredients.get(ingredient_id)

    def lookup_by_name(self, name: str) -> Ingredient | None:
        """Look up an ingredient by name or alias."""
        ingredient_id = self.alias_index.get(name.lower())
        if ingredient_id:
            return self.ingredients.get(ingredient_id)
        return None

    def get_all_by_rating(self, stage: Stage, rating: Rating) -> list[Ingredient]:
        """Get all ingredients with a specific rating for a stage."""
        results = []
        for ingredient in self.ingredients.values():
            stage_safety = ingredient.safety.get(stage.value)
            if stage_safety and stage_safety.rating == rating:
                results.append(ingredient)
        return results

    @property
    def ingredient_count(self) -> int:
        return len(self.ingredients)

    @property
    def alias_count(self) -> int:
        return len(self.alias_index)
