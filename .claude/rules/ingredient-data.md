---
paths:
  - "data/ingredients/**/*.yaml"
---

## Ingredient YAML Schema Rules

When creating or editing ingredient YAML files:

### Structure
- `id` MUST match the filename (without .yaml extension)
- All three life stages (pregnancy, nursing, baby) MUST have safety entries
- aliases should include all common names, INCI names, and trade names

### Per-stage fields (under `safety.{pregnancy|nursing|baby}`)
- `rating` MUST be one of: safe, caution, avoid, insufficient_data
- `exposure_route` MUST be one of: topical, oral, inhalation, multiple
- `evidence_strength` MUST be one of: definitive, strong, moderate, limited
  - `definitive`: established human harm OR binding regulatory prohibition + strong mechanism (e.g. mercury, lead, inert emollients like petrolatum)
  - `strong`: major guideline/regulatory consensus, but not direct human causal evidence (e.g. hydroquinone per ACOG, IARC Group 1)
  - `moderate`: concerning but indirect/incomplete human evidence; animal studies, biomonitoring, limited epidemiology
  - `limited`: precaution driven mostly by uncertainty + availability of safer alternatives
  - Use `definitive` sparingly — it should signal "we've known this for decades." Most cosmetic pregnancy calls are `strong` or `moderate`.

### Per-ingredient fields (top level)
- `rating_confidence` MUST be one of: high, moderate, low, insufficient
  - This is the curator's confidence in the assigned rating given the evidence and interpretation. Distinct from `evidence_strength` which measures underlying evidence quality. Previously named `confidence`.

### Sources
- `sources` MUST have at least 2 entries (at least one regulatory/professional body)
- Source refs MUST resolve to an entry in data/sources.yaml
- Sources that represent direct empirical evidence (peer-reviewed studies, IARC monographs, CIR reviews, biomonitoring data) should be marked `primary: true` in data/sources.yaml. Regulatory positions and guideline summaries are NOT marked primary.
- Every stage rating should ideally be backed by at least one regulatory/guideline source (the "basis") AND at least one primary source (the direct evidence). During migration this is a goal, not yet enforced.

### Verification
After editing, always run:
```bash
babysafety compile && python -m pytest tests/test_data_integrity.py
```
