"""Parse ingredient lists from product labels."""

from __future__ import annotations

import re

from .models import ParsedIngredient

# Patterns for section headers in ingredient lists
SECTION_PATTERNS = [
    (re.compile(r"^active\s+ingredients?\s*:?\s*", re.IGNORECASE), "active"),
    (re.compile(r"^inactive\s+ingredients?\s*:?\s*", re.IGNORECASE), "inactive"),
    (re.compile(r"^other\s+ingredients?\s*:?\s*", re.IGNORECASE), "inactive"),
    (re.compile(r"^may\s+contain\s*:?\s*", re.IGNORECASE), "may_contain"),
    (re.compile(r"^ingredients?\s*:?\s*", re.IGNORECASE), "general"),
]

# Pattern for concentration/percentage annotations
CONCENTRATION_RE = re.compile(r"\(?\s*(\d+\.?\d*\s*%)\s*\)?")

# Pattern for parenthetical synonyms like (Vitamin B3)
PAREN_SYNONYM_RE = re.compile(r"\(([^)]+)\)")

# Pattern for "less than X% of:" prefix
LESS_THAN_RE = re.compile(r"less\s+than\s+\d+\.?\d*\s*%\s+of\s*:?\s*", re.IGNORECASE)


def _preprocess(text: str) -> str:
    """Normalize the raw input text."""
    # Replace various line breaks with commas
    text = re.sub(r"[\r\n]+", ", ", text)
    # Normalize unicode punctuation
    text = text.replace("\u2022", ",")  # bullet
    text = text.replace("\u2013", "-")  # en-dash
    text = text.replace("\u2014", "-")  # em-dash
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    # Collapse multiple commas/spaces
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _detect_section(text: str) -> tuple[str, str]:
    """Check if text starts with a section header. Returns (section, remaining_text)."""
    for pattern, section in SECTION_PATTERNS:
        match = pattern.match(text)
        if match:
            return section, text[match.end():].strip()
    return "", text


def _extract_concentration(text: str) -> tuple[str, str | None]:
    """Extract percentage concentration from ingredient text."""
    match = CONCENTRATION_RE.search(text)
    if match:
        concentration = match.group(1).strip()
        cleaned = CONCENTRATION_RE.sub("", text).strip()
        return cleaned, concentration
    return text, None


def _extract_secondary_names(text: str) -> tuple[str, list[str]]:
    """Extract parenthetical synonyms from ingredient name."""
    secondary = []
    for match in PAREN_SYNONYM_RE.finditer(text):
        inner = match.group(1).strip()
        # Skip if it looks like a concentration or number
        if re.match(r"^\d", inner):
            continue
        # Skip very short content that's likely an abbreviation
        if len(inner) <= 1:
            continue
        secondary.append(inner)

    # Remove the parenthetical parts from the primary name
    primary = PAREN_SYNONYM_RE.sub("", text).strip()
    # Clean up double spaces
    primary = re.sub(r"\s+", " ", primary)
    return primary, secondary


def _split_slash_names(name: str, secondary: list[str]) -> tuple[str, list[str]]:
    """Handle slash-separated names like Aqua/Water/Eau."""
    if "/" in name:
        parts = [p.strip() for p in name.split("/") if p.strip()]
        if len(parts) > 1 and all(len(p) > 1 for p in parts):
            return parts[0], secondary + parts[1:]
    return name, secondary


def parse_ingredient_list(text: str) -> list[ParsedIngredient]:
    """Parse a raw ingredient list into structured ParsedIngredient objects."""
    text = _preprocess(text)
    if not text:
        return []

    current_section = "general"
    results: list[ParsedIngredient] = []
    position = 0

    # Check for "less than X% of:" prefix and strip it
    text = LESS_THAN_RE.sub("", text)

    # Detect and strip section header
    detected_section, text = _detect_section(text)
    if detected_section:
        current_section = detected_section

    # Split on commas and semicolons
    # But be careful not to split inside parentheses
    tokens = _split_respecting_parens(text)

    for token in tokens:
        token = token.strip().rstrip(".")
        if not token:
            continue

        # Check if this token is a new section header
        detected_section, remainder = _detect_section(token)
        if detected_section:
            current_section = detected_section
            token = remainder
            if not token:
                continue

        # Strip "less than X% of:" within the list
        token = LESS_THAN_RE.sub("", token).strip()
        if not token:
            continue

        raw = token
        token, concentration = _extract_concentration(token)

        # Handle (and) connectors BEFORE secondary name extraction:
        # "A (and) B" -> split into two ingredients
        and_parts = re.split(r"\s*\(and\)\s*", token, flags=re.IGNORECASE)
        for part in and_parts:
            part = part.strip()
            if not part:
                continue
            primary_name, secondary_names = _extract_secondary_names(part)
            primary_name, secondary_names = _split_slash_names(primary_name, secondary_names)
            results.append(ParsedIngredient(
                raw=raw,
                name=primary_name,
                secondary_names=secondary_names,
                concentration=concentration,
                section=current_section,
                position=position,
            ))
            position += 1

    return results


def _split_respecting_parens(text: str) -> list[str]:
    """Split on commas and semicolons, but not inside parentheses."""
    tokens: list[str] = []
    depth = 0
    current: list[str] = []

    for char in text:
        if char == "(":
            depth += 1
            current.append(char)
        elif char == ")":
            depth = max(0, depth - 1)
            current.append(char)
        elif char in (",", ";") and depth == 0:
            tokens.append("".join(current))
            current = []
        else:
            current.append(char)

    if current:
        tokens.append("".join(current))

    return tokens
