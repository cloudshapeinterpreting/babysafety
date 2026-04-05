"""Format safety reports for terminal output using Rich."""

from __future__ import annotations

import json

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .models import Ingredient, MatchResult, Rating, Stage, StageSafety

RATING_COLORS = {
    Rating.SAFE: "green",
    Rating.CAUTION: "yellow",
    Rating.AVOID: "red",
    Rating.INSUFFICIENT_DATA: "dim",
}

RATING_LABELS = {
    Rating.SAFE: "SAFE",
    Rating.CAUTION: "CAUTION",
    Rating.AVOID: "AVOID",
    Rating.INSUFFICIENT_DATA: "INSUFFICIENT DATA",
}


def _format_aliases(ingredient: Ingredient, max_shown: int = 3) -> str:
    if not ingredient.aliases:
        return ""
    shown = ingredient.aliases[:max_shown]
    suffix = f" +{len(ingredient.aliases) - max_shown} more" if len(ingredient.aliases) > max_shown else ""
    return f"(also: {', '.join(shown)}{suffix})"


def _format_sources(ingredient: Ingredient) -> str:
    parts = []
    for source in ingredient.sources:
        if source.ref:
            parts.append(source.ref)
        elif source.authors and source.journal and source.year:
            parts.append(f"{source.authors} ({source.journal}, {source.year})")
        elif source.title:
            parts.append(source.title)
    return "; ".join(parts) if parts else "No sources cited"


def _render_ingredient_block(
    console: Console,
    ingredient: Ingredient,
    stage_safety: StageSafety,
    detailed: bool,
) -> None:
    color = RATING_COLORS[stage_safety.rating]
    label = RATING_LABELS[stage_safety.rating]
    aliases = _format_aliases(ingredient)

    name_line = Text()
    name_line.append(f"  {ingredient.name} ", style=f"bold {color}")
    if aliases:
        name_line.append(aliases, style="dim")
    console.print(name_line)

    info_parts = [
        f"Rating: {label}",
        f"Confidence: {ingredient.rating_confidence.value.title()}",
        f"Exposure: {stage_safety.exposure_route.title()}",
    ]
    console.print(f"  {' | '.join(info_parts)}", style="dim")

    console.print(f"  {stage_safety.summary}")

    if stage_safety.dose_dependent:
        console.print("  Note: Dose-dependent -- concentration matters.", style="italic yellow")

    if detailed and stage_safety.details:
        console.print(f"  {stage_safety.details}", style="dim")

    sources = _format_sources(ingredient)
    console.print(f"  Sources: {sources}", style="dim")

    if ingredient.safer_alternatives:
        alt_names = [a.name for a in ingredient.safer_alternatives[:3]]
        console.print(f"  Alternatives: {', '.join(alt_names)}", style="green")

    console.print()


def print_report(
    results: list[MatchResult],
    stage: Stage,
    detailed: bool = False,
) -> None:
    """Print a formatted safety report to the terminal."""
    console = Console()

    # Group results by rating
    avoid = []
    caution = []
    safe = []
    insufficient = []
    unrecognized = []

    for result in results:
        if result.ingredient is None:
            unrecognized.append(result)
            continue

        stage_safety = result.ingredient.safety.get(stage.value)
        if stage_safety is None:
            unrecognized.append(result)
            continue

        match stage_safety.rating:
            case Rating.AVOID:
                avoid.append((result, stage_safety))
            case Rating.CAUTION:
                caution.append((result, stage_safety))
            case Rating.SAFE:
                safe.append((result, stage_safety))
            case Rating.INSUFFICIENT_DATA:
                insufficient.append((result, stage_safety))

    # Header
    total = len(results)
    flagged = len(avoid) + len(caution)
    safe_count = len(safe)
    unknown = len(unrecognized) + len(insufficient)

    header = Text()
    header.append(f" BabySafety Report -- {stage.value.title()}\n", style="bold")
    header.append(
        f" {total} ingredients parsed: "
        f"{flagged} flagged, {safe_count} safe, {unknown} unrecognized/insufficient"
    )
    console.print(Panel(header, border_style="blue"))

    # AVOID section
    if avoid:
        console.print(f"\n [bold red]AVOID ({len(avoid)})[/bold red]")
        console.print(" " + "-" * 60)
        for result, stage_safety in avoid:
            _render_ingredient_block(console, result.ingredient, stage_safety, detailed)

    # CAUTION section
    if caution:
        console.print(f"\n [bold yellow]CAUTION ({len(caution)})[/bold yellow]")
        console.print(" " + "-" * 60)
        for result, stage_safety in caution:
            _render_ingredient_block(console, result.ingredient, stage_safety, detailed)

    # SAFE section
    if safe:
        console.print(f"\n [bold green]SAFE ({len(safe)})[/bold green]")
        console.print(" " + "-" * 60)
        if detailed:
            for result, stage_safety in safe:
                _render_ingredient_block(console, result.ingredient, stage_safety, detailed)
        else:
            names = [r.ingredient.name for r, _ in safe]
            console.print(f"  {', '.join(names)}\n")

    # INSUFFICIENT DATA section
    if insufficient:
        console.print(f"\n [dim]INSUFFICIENT DATA ({len(insufficient)})[/dim]")
        console.print(" " + "-" * 60)
        for result, stage_safety in insufficient:
            console.print(f"  {result.ingredient.name} -- not enough research to determine safety")
        console.print()

    # UNRECOGNIZED section
    if unrecognized:
        console.print(f"\n [dim]UNRECOGNIZED ({len(unrecognized)})[/dim]")
        console.print(" " + "-" * 60)
        for result in unrecognized:
            console.print(f'  "{result.parsed.name}" -- not in knowledge base')
        console.print()

    # Disclaimer
    console.print(
        " [dim italic]Disclaimer: This tool provides information only, not medical "
        "advice. Always consult your healthcare provider.[/dim italic]"
    )
    console.print()


def print_lookup(ingredient: Ingredient) -> None:
    """Print detailed info for a single ingredient lookup."""
    console = Console()

    header = Text()
    header.append(f"{ingredient.name}", style="bold")
    if ingredient.cas_number:
        header.append(f"  CAS: {ingredient.cas_number}", style="dim")
    console.print(Panel(header, border_style="blue"))

    if ingredient.aliases:
        console.print(f"Aliases: {', '.join(ingredient.aliases)}", style="dim")
    console.print(f"Category: {ingredient.category}")
    console.print(f"Product types: {', '.join(ingredient.product_types)}")
    console.print(f"Confidence: {ingredient.rating_confidence.value.title()}")
    console.print(f"Last reviewed: {ingredient.last_reviewed}")
    console.print()

    for stage_name in ("pregnancy", "nursing", "baby"):
        stage_safety = ingredient.safety.get(stage_name)
        if not stage_safety:
            continue

        color = RATING_COLORS[stage_safety.rating]
        label = RATING_LABELS[stage_safety.rating]

        console.print(f"[bold]{stage_name.title()}[/bold]: [{color}]{label}[/{color}]")
        console.print(f"  {stage_safety.summary}")
        if stage_safety.details:
            console.print(f"  {stage_safety.details}", style="dim")
        if stage_safety.dose_dependent:
            console.print("  Dose-dependent: Yes", style="italic yellow")
        console.print(f"  Exposure route: {stage_safety.exposure_route}")
        if stage_safety.min_safe_age_months is not None:
            console.print(f"  Min safe age: {stage_safety.min_safe_age_months} months")
        console.print()

    if ingredient.safer_alternatives:
        console.print("[bold]Safer alternatives:[/bold]")
        for alt in ingredient.safer_alternatives:
            note = f" -- {alt.note}" if alt.note else ""
            console.print(f"  - {alt.name}{note}")
        console.print()

    if ingredient.sources:
        console.print("[bold]Sources:[/bold]")
        for source in ingredient.sources:
            if source.ref:
                console.print(f"  - {source.ref}")
            else:
                parts = []
                if source.authors:
                    parts.append(source.authors)
                if source.title:
                    parts.append(f'"{source.title}"')
                if source.journal:
                    parts.append(source.journal)
                if source.year:
                    parts.append(str(source.year))
                console.print(f"  - {', '.join(parts)}")
                if source.finding:
                    console.print(f"    Finding: {source.finding}", style="dim")
        console.print()

    if ingredient.notes:
        console.print(f"[bold]Notes:[/bold] {ingredient.notes}")

    console.print(
        "\n[dim italic]Disclaimer: This tool provides information only, not medical "
        "advice. Always consult your healthcare provider.[/dim italic]"
    )


def results_to_json(results: list[MatchResult], stage: Stage) -> str:
    """Convert results to JSON string."""
    output = []
    for result in results:
        entry: dict = {"name": result.parsed.name, "raw": result.parsed.raw}
        if result.ingredient:
            stage_safety = result.ingredient.safety.get(stage.value)
            entry["matched"] = True
            entry["ingredient_id"] = result.ingredient.id
            entry["matched_via"] = result.matched_via
            if stage_safety:
                entry["rating"] = stage_safety.rating.value
                entry["summary"] = stage_safety.summary
                entry["dose_dependent"] = stage_safety.dose_dependent
        else:
            entry["matched"] = False
        output.append(entry)
    return json.dumps(output, indent=2)
