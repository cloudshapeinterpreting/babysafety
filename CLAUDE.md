# BabySafety

Evidence-based ingredient safety checker for pregnancy, nursing, and baby care.

## Build & Test

```bash
source venv/bin/activate     # Always activate venv first
pip install -e ".[dev]"      # Install/update deps
babysafety compile           # Build compiled JSON from YAML
python -m pytest tests/ -v   # Run tests
```

## Quick reference

- `babysafety check --text "ingredient1, ingredient2" --stage pregnancy` -- evaluate ingredients
- `babysafety check --file label.txt --stage all` -- from file, all stages
- `babysafety lookup <ingredient>` -- deep-dive on one ingredient
- `babysafety compile` -- rebuild compiled JSON from YAML sources
- `babysafety stats` -- knowledge base statistics

## When a user pastes an ingredient list

1. Read `data/compiled/ingredients.json` for the full database
2. Read `data/compiled/alias_index.json` for name lookups
3. Parse the ingredient list (comma-separated, strip parenthetical percentages and notes)
4. Look up each ingredient in the alias index
5. Report findings grouped by rating: avoid, caution, safe, unrecognized
6. Always include the disclaimer that this is informational, not medical advice

## Rating system

| Rating | Meaning |
|---|---|
| safe | No known concerns at typical exposure |
| caution | Some concern; dose-dependent or limited data |
| avoid | Evidence-based recommendation against use |
| insufficient_data | Not enough research |

## Evidence System

Each ingredient has two orthogonal quality axes:

| Axis | Lives on | Values | Measures |
|------|----------|--------|----------|
| `evidence_strength` | Per-stage | definitive, strong, moderate, limited | Strength of published/regulatory evidence |
| `rating_confidence` | Per-ingredient | high, moderate, low, insufficient | Curator confidence in the assigned rating |

Evidence strength definitions:
- **definitive**: established human harm or binding regulatory prohibition (mercury, lead, inert emollients)
- **strong**: major guideline/regulatory consensus (hydroquinone per ACOG, IARC Group 1)
- **moderate**: indirect/incomplete evidence (chemical sunscreens, phthalates)
- **limited**: precaution driven by unknowns (minoxidil, grouped EO classes)

Full schema rules: `.claude/rules/ingredient-data.md`

## Important

- Always cite the sources listed in each ingredient entry
- Always mention dose-dependent context when the flag is set
- Always recommend consulting a healthcare provider
- YAML source files live in `data/ingredients/<category>/`
- Compiled JSON is auto-generated via `babysafety compile`

## Constraints

- NEVER fabricate safety data or citations -- every rating must trace to a real source
- NEVER edit files in `data/compiled/` by hand -- always use `babysafety compile`
- Always activate venv before running commands: `source venv/bin/activate`
- Run `babysafety compile` after adding/editing any YAML ingredient file
- Run tests after any code changes

## Adding new ingredients

1. Create YAML file in `data/ingredients/<category>/`
2. Follow schema from existing files (id, name, aliases, safety per stage, sources)
3. Cite minimum 2 sources (at least one regulatory/professional body)
4. Run `babysafety compile` to rebuild index
5. Run `python -m pytest tests/test_data_integrity.py` to validate

## Task Routing

| Trigger | Action |
|---------|--------|
| check/analyze/evaluate ingredients | `/check-label` skill |
| lookup/search ingredient | `babysafety lookup` CLI command |
| add ingredient/expand KB | `/add-ingredient` skill |
| research ingredient safety | `@ingredient-researcher` agent |
| plan/design | enter plan mode |
| review/audit/check project | `/best-practices` |

## Project structure

- `babysafety/` -- Python package (CLI, parser, matcher, compiler, reporter)
- `data/ingredients/` -- YAML ingredient files (source of truth)
- `data/compiled/` -- Auto-generated JSON (do not edit by hand)
- `data/sources.yaml` -- Shared citation library
- `data/categories.yaml` -- Product category definitions
- `tests/` -- pytest test suite
