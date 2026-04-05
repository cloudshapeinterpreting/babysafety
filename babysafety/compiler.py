"""Compile YAML ingredient files into JSON for fast runtime loading."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).parent.parent / "data"
INGREDIENTS_DIR = DATA_DIR / "ingredients"
COMPILED_DIR = DATA_DIR / "compiled"


def compile_database() -> tuple[dict, dict]:
    """Read all ingredient YAML files and produce compiled JSON.

    Returns (ingredients_dict, alias_index) where:
    - ingredients_dict maps ingredient ID -> full ingredient data
    - alias_index maps lowercase alias -> ingredient ID
    """
    ingredients: dict[str, dict] = {}
    alias_index: dict[str, str] = {}

    for yaml_path in sorted(INGREDIENTS_DIR.rglob("*.yaml")):
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        if not data or "id" not in data:
            continue

        ingredient_id = data["id"]
        ingredients[ingredient_id] = data

        # Index the canonical name
        alias_index[data["name"].lower()] = ingredient_id

        # Index all aliases
        for alias in data.get("aliases", []):
            alias_lower = alias.lower()
            if alias_lower in alias_index and alias_index[alias_lower] != ingredient_id:
                print(
                    f"WARNING: Alias conflict for '{alias}' -- "
                    f"claimed by both '{alias_index[alias_lower]}' and '{ingredient_id}'"
                )
            alias_index[alias_lower] = ingredient_id

    return ingredients, alias_index


def write_compiled(ingredients: dict, alias_index: dict) -> None:
    """Write compiled JSON files to data/compiled/."""
    COMPILED_DIR.mkdir(parents=True, exist_ok=True)

    with open(COMPILED_DIR / "ingredients.json", "w") as f:
        json.dump(ingredients, f, indent=2, ensure_ascii=False)

    with open(COMPILED_DIR / "alias_index.json", "w") as f:
        json.dump(alias_index, f, indent=2, ensure_ascii=False)


def run_compile() -> tuple[int, int]:
    """Full compile pipeline. Returns (ingredient_count, alias_count)."""
    ingredients, alias_index = compile_database()
    write_compiled(ingredients, alias_index)
    return len(ingredients), len(alias_index)
