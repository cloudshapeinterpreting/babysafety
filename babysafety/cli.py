"""CLI entry point for BabySafety."""

from __future__ import annotations

import sys

import click
from rich.console import Console

from .compiler import run_compile
from .database import Database
from .matcher import match_all
from .models import Stage
from .parser import parse_ingredient_list
from .reporter import print_lookup, print_report, results_to_json


@click.group()
def cli() -> None:
    """BabySafety -- Evidence-based ingredient safety checker for pregnancy, nursing, and baby care."""
    pass


@cli.command()
@click.option("--text", "-t", help="Ingredient list as text (comma-separated)")
@click.option("--file", "-f", "filepath", type=click.Path(exists=True), help="File containing ingredient list")
@click.option(
    "--stage", "-s",
    type=click.Choice(["pregnancy", "nursing", "baby", "all"], case_sensitive=False),
    default="pregnancy",
    help="Life stage to evaluate (default: pregnancy)",
)
@click.option("--detailed", "-d", is_flag=True, help="Show full details and evidence")
@click.option("--json-output", "--json", "as_json", is_flag=True, help="Output as JSON")
def check(text: str | None, filepath: str | None, stage: str, detailed: bool, as_json: bool) -> None:
    """Evaluate an ingredient list for safety."""
    # Get ingredient text from --text, --file, or stdin
    if text:
        ingredient_text = text
    elif filepath:
        with open(filepath) as f:
            ingredient_text = f.read()
    elif not sys.stdin.isatty():
        ingredient_text = sys.stdin.read()
    else:
        ingredient_text = click.prompt("Paste ingredient list")

    db = Database.load()
    parsed = parse_ingredient_list(ingredient_text)

    if not parsed:
        click.echo("No ingredients found in input.")
        return

    results = match_all(db, parsed)

    if stage == "all":
        for s in Stage:
            if as_json:
                click.echo(results_to_json(results, s))
            else:
                print_report(results, s, detailed=detailed)
    else:
        s = Stage(stage)
        if as_json:
            click.echo(results_to_json(results, s))
        else:
            print_report(results, s, detailed=detailed)


@cli.command()
@click.argument("name")
def lookup(name: str) -> None:
    """Look up a single ingredient by name."""
    db = Database.load()
    ingredient = db.lookup_by_name(name)
    if not ingredient:
        # Try case variations
        for key in db.alias_index:
            if key.lower() == name.lower():
                ingredient = db.lookup_by_name(key)
                break

    if ingredient:
        print_lookup(ingredient)
    else:
        console = Console()
        console.print(f'[red]Ingredient "{name}" not found in knowledge base.[/red]')
        console.print("\nDid you mean one of these?")
        # Show ingredients with partial name match
        name_lower = name.lower()
        suggestions = [
            alias for alias in db.alias_index
            if name_lower in alias.lower() or alias.lower() in name_lower
        ]
        if suggestions:
            for s in suggestions[:5]:
                console.print(f"  - {s}")
        else:
            console.print("  (no close matches found)")


@cli.command(name="compile")
def compile_cmd() -> None:
    """Rebuild compiled JSON from YAML ingredient files."""
    console = Console()
    console.print("Compiling ingredient database...")
    ingredient_count, alias_count = run_compile()
    console.print(
        f"[green]Done.[/green] {ingredient_count} ingredients, {alias_count} aliases indexed."
    )


@cli.command()
def stats() -> None:
    """Show knowledge base statistics."""
    db = Database.load()
    console = Console()

    console.print(f"[bold]BabySafety Knowledge Base[/bold]")
    console.print(f"  Ingredients: {db.ingredient_count}")
    console.print(f"  Aliases indexed: {db.alias_count}")

    # Count by rating per stage
    for stage in Stage:
        ratings: dict[str, int] = {}
        for ingredient in db.ingredients.values():
            stage_safety = ingredient.safety.get(stage.value)
            if stage_safety:
                label = stage_safety.rating.value
                ratings[label] = ratings.get(label, 0) + 1
        parts = [f"{k}: {v}" for k, v in sorted(ratings.items())]
        console.print(f"  {stage.value.title()}: {', '.join(parts)}")
