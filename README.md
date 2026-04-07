# BabySafety

Evidence-based ingredient safety checker for pregnancy, nursing, and baby care.

Scan a product's ingredient list and get instant safety ratings backed by sources from ACOG, FDA, AAP, CIR, EU SCCS, WHO, LactMed, and MotherToBaby.

## Why

My wife is expecting (September 2026). She kept asking "is this lotion safe?" and I kept googling the same ingredients. So I built a CLI that does it properly -- with real citations, not mommy-blog fear-mongering.

## Install

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
babysafety compile   # build the ingredient database
```

Requires Python 3.10+.

## Usage

### Check a product's ingredient list

```bash
babysafety check --text "water, glycerin, cetearyl alcohol, fragrance, retinol" --stage pregnancy
```

Output:
```
BabySafety Report -- Pregnancy
5 ingredients parsed: 5/5 recognized (100%) | 2 flagged, 3 safe, 0 unknown

AVOID (1)
  Retinol -- Known teratogen. All retinoids should be avoided during pregnancy.
  Rating: AVOID [strong] | Confidence: High

CAUTION (1)
  Fragrance -- Undisclosed components; potential hidden phthalates.
  Rating: CAUTION [moderate] | Confidence: High

SAFE (3)
  Water, Glycerin, Cetearyl Alcohol
```

### Check from a file

```bash
babysafety check --file label.txt --stage pregnancy
```

### Check all stages at once

```bash
babysafety check --text "benzocaine, zinc oxide" --stage all
```

### Look up a single ingredient

```bash
babysafety lookup retinol
babysafety lookup "zinc oxide"
```

### Get database stats

```bash
babysafety stats
```

## Rating System

| Rating | Meaning |
|---|---|
| `safe` | No known concerns at typical exposure |
| `caution` | Some concern; dose-dependent or limited data |
| `avoid` | Evidence-based recommendation against use |
| `insufficient_data` | Not enough research to determine |

### Evidence Strength

Each rating is backed by an evidence strength assessment:

| Level | What it means |
|---|---|
| `definitive` | Established human harm or binding regulatory prohibition. We've known this for decades. (e.g., mercury, lead) |
| `strong` | Major guideline/regulatory consensus. Clear recommendation from ACOG, FDA, or AAP. (e.g., hydroquinone, formaldehyde) |
| `moderate` | Concerning but indirect evidence. Animal studies, biomonitoring signals, limited human data. (e.g., chemical sunscreens, phthalates) |
| `limited` | Precautionary. Rating driven by unknowns + availability of safer alternatives. (e.g., minoxidil) |

## Coverage

The database currently contains **62 ingredients** with **428 aliases**, covering:

- Common moisturizer/lotion ingredients (100% coverage on typical drugstore lotions)
- Pregnancy AVOID red list (retinoids, hydroquinone, mercury, lead, formaldehyde releasers, phthalates, high-risk essential oils, octinoxate, oxybenzone, minoxidil)
- Baby AVOID red list (benzocaine, lidocaine teething, camphor, methyl salicylate, eucalyptus oil, peppermint/menthol, talc powder)
- Pregnancy CAUTION ingredients (chemical sunscreens, fragrance, benzoyl peroxide, hair dye, triclosan, self-tanner)
- Safe alternatives (niacinamide, azelaic acid, vitamin C, titanium dioxide, zinc oxide)

## Adding Ingredients

1. Create a YAML file in `data/ingredients/<category>/`
2. Follow the schema in existing files (id, name, aliases, safety per stage, sources)
3. Cite minimum 2 sources (at least one regulatory/professional body)
4. Set `evidence_strength` per stage and `rating_confidence` per ingredient
5. Run `babysafety compile` to rebuild the database
6. Run `python -m pytest tests/` to validate

## Sources

All safety ratings cite authoritative sources:

- **ACOG** -- American College of Obstetricians and Gynecologists
- **FDA** -- US Food and Drug Administration
- **AAP** -- American Academy of Pediatrics
- **CIR** -- Cosmetic Ingredient Review (independent expert panel)
- **EU SCCS** -- Scientific Committee on Consumer Safety
- **WHO** -- World Health Organization
- **LactMed** -- NIH Drugs and Lactation Database
- **MotherToBaby** -- Organization of Teratology Information Specialists
- **IARC** -- International Agency for Research on Cancer

## Disclaimer

This tool provides information only, not medical advice. Always consult your healthcare provider about specific products and ingredients during pregnancy, nursing, or for infant care. See [DISCLAIMER.md](DISCLAIMER.md) for full details.

## License

MIT
