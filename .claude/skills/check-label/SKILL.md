---
name: check-label
description: Check a product ingredient list for safety across all life stages (pregnancy, nursing, baby)
allowed-tools: ["Read", "Bash", "Grep"]
---

# Check Label

Evaluate a product's ingredient list for safety during pregnancy, nursing, and baby care.

## Instructions

1. If `$ARGUMENTS` is provided, use it as the ingredient list text.
2. If no arguments, ask the user to paste or type the ingredient list.
3. Activate venv and run the check across all stages:

```bash
source venv/bin/activate
babysafety check --text "$ARGUMENTS" --stage all
```

4. After the report, offer:
   - "Want me to look up any specific ingredient in detail?" (`babysafety lookup <name>`)
   - If coverage is below 80%, note which unrecognized ingredients could be added to the KB.

## Examples

```
/check-label water, glycerin, retinol, fragrance, dimethicone
/check-label Cetearyl Alcohol, Caprylic/Capric Triglyceride, Phenoxyethanol
```
