"""Tests for ingredient matching."""

from babysafety.database import Database
from babysafety.matcher import match_all, match_ingredient
from babysafety.models import ParsedIngredient


def _get_db() -> Database:
    return Database.load()


def test_exact_match():
    db = _get_db()
    parsed = ParsedIngredient(raw="Retinol", name="Retinol", position=0)
    result = match_ingredient(db, parsed)
    assert result.ingredient is not None
    assert result.ingredient.id == "retinol"
    assert result.matched_via == "exact"


def test_alias_match():
    db = _get_db()
    parsed = ParsedIngredient(raw="Benzophenone-3", name="Benzophenone-3", position=0)
    result = match_ingredient(db, parsed)
    assert result.ingredient is not None
    assert result.ingredient.id == "oxybenzone"


def test_case_insensitive():
    db = _get_db()
    parsed = ParsedIngredient(raw="RETINOL", name="RETINOL", position=0)
    result = match_ingredient(db, parsed)
    assert result.ingredient is not None
    assert result.ingredient.id == "retinol"


def test_secondary_name_match():
    db = _get_db()
    parsed = ParsedIngredient(
        raw="Mysteryamine (Vitamin A)",
        name="Mysteryamine",
        secondary_names=["Vitamin A"],
        position=0,
    )
    result = match_ingredient(db, parsed)
    assert result.ingredient is not None
    assert result.ingredient.id == "retinol"
    assert result.matched_via == "alias"


def test_no_match():
    db = _get_db()
    parsed = ParsedIngredient(
        raw="Unobtanium Extract", name="Unobtanium Extract", position=0
    )
    result = match_ingredient(db, parsed)
    assert result.ingredient is None
    assert result.matched_via == ""


def test_normalized_match():
    db = _get_db()
    parsed = ParsedIngredient(raw="Zinc-Oxide", name="Zinc-Oxide", position=0)
    result = match_ingredient(db, parsed)
    assert result.ingredient is not None
    assert result.ingredient.id == "zinc_oxide"


def test_match_all():
    db = _get_db()
    parsed_list = [
        ParsedIngredient(raw="Retinol", name="Retinol", position=0),
        ParsedIngredient(
            raw="Unobtanium Extract", name="Unobtanium Extract", position=1
        ),
        ParsedIngredient(raw="Zinc Oxide", name="Zinc Oxide", position=2),
    ]
    results = match_all(db, parsed_list)
    assert len(results) == 3
    assert results[0].ingredient is not None
    assert results[1].ingredient is None
    assert results[2].ingredient is not None


def test_bha_matches_salicylic_acid():
    db = _get_db()
    parsed = ParsedIngredient(raw="BHA", name="BHA", position=0)
    result = match_ingredient(db, parsed)
    assert result.ingredient is not None
    assert result.ingredient.id == "salicylic_acid"


def test_guarana_matches_caffeine():
    db = _get_db()
    parsed = ParsedIngredient(raw="Guarana Extract", name="Guarana Extract", position=0)
    result = match_ingredient(db, parsed)
    assert result.ingredient is not None
    assert result.ingredient.id == "caffeine"
