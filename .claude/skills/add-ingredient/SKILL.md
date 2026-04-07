---
name: add-ingredient
description: Add a new ingredient to the knowledge base with evidence-based safety ratings
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Agent", "WebSearch", "WebFetch"]
---

# Add Ingredient

Add a new ingredient to the BabySafety knowledge base.

## Instructions

1. The ingredient name is `$ARGUMENTS`. If no arguments, ask the user which ingredient to add.

2. **Research the ingredient** using authoritative sources:
   - CIR (Cosmetic Ingredient Review) expert panel assessments
   - FDA regulatory positions (GRAS, OTC monographs, safety communications)
   - ACOG guidelines (pregnancy-specific)
   - AAP guidelines (baby-specific)
   - LactMed (nursing-specific)
   - MotherToBaby fact sheets
   - EU SCCS opinions

3. **Read the schema rules**: `.claude/rules/ingredient-data.md`

4. **Read a template**: `data/ingredients/skincare/zinc_oxide.yaml` (safe example) or `data/ingredients/skincare/hydroquinone.yaml` (avoid example)

5. **Determine the correct category directory**:
   - `data/ingredients/skincare/` for cosmetic/skincare ingredients
   - `data/ingredients/baby_products/` for baby-specific concerns
   - `data/ingredients/food/` for dietary ingredients
   - `data/ingredients/cleaning/` for cleaning product ingredients

6. **Create the YAML file** following the schema exactly:
   - `id` must match filename
   - All 3 life stages (pregnancy, nursing, baby) with ratings
   - `evidence_strength` per stage (definitive/strong/moderate/limited)
   - `rating_confidence` per ingredient (high/moderate/low/insufficient)
   - Minimum 2 sources with at least 1 regulatory/professional body
   - Add any new source refs to `data/sources.yaml` FIRST

7. **Check for alias conflicts**: grep existing YAML files for any aliases you plan to use.

8. **Compile and test**:
```bash
source venv/bin/activate
babysafety compile
python -m pytest tests/test_data_integrity.py -v
```

9. **Verify**: `babysafety lookup <ingredient_name>`

## Constraints

- NEVER fabricate safety data or citations
- NEVER assign `evidence_strength: definitive` without established human harm or binding regulatory prohibition
- Always add sources to `data/sources.yaml` BEFORE referencing them in ingredient files
