"""Typer command-line interface for Dicta."""

from importlib.metadata import PackageNotFoundError, version as metadata_version

import typer

from dicta import __version__
from dicta.core.program import (
    build_arithmetic_demo_program,
    build_counter_revision_demo_program,
    build_invalid_arithmetic_demo_program,
    dictum_text,
)

app = typer.Typer(help="Dicta semantic-kernel prototype.")


def package_version() -> str:
    """Return installed package version, falling back to source version."""

    try:
        return metadata_version("dicta")
    except PackageNotFoundError:
        return __version__


@app.command()
def version() -> None:
    """Print the package version."""

    typer.echo(package_version())


@app.command()
def demo() -> None:
    """Run the hard-coded 3 + 4 semantic demo."""

    program = build_arithmetic_demo_program()
    revision = program.history[-1]
    outcome = revision.outcome

    typer.echo("Datum: 3 + 4")
    typer.echo("")
    typer.echo("Dicta:")
    for dictum in program.concept.dicta:
        typer.echo(f"* {dictum_text(dictum)}")
    typer.echo("")
    typer.echo("Qualification:")
    typer.echo(f"* {revision.note}")
    typer.echo("")
    typer.echo("Outcome:")
    typer.echo(f"* {outcome.result}")
    typer.echo("")
    typer.echo("Revision:")
    for change in revision.changes:
        typer.echo(f"* {change}")


@app.command()
def invalid_demo() -> None:
    """Run the hard-coded 3 + "cat" disparity demo."""

    program = build_invalid_arithmetic_demo_program()
    revision = program.history[-1]
    outcome = revision.outcome
    inference = outcome.inference
    disparity = inference.from_disparity

    typer.echo('Datum: 3 + "cat"')
    typer.echo("")
    typer.echo("Dicta:")
    for dictum in program.concept.dicta:
        typer.echo(f"* {dictum_text(dictum)}")
    typer.echo("")
    typer.echo("Purpose:")
    typer.echo(f"* {program.concept.purpose.statement}")
    typer.echo("")
    typer.echo("Disparity:")
    typer.echo(f"* {disparity.description}")
    typer.echo("")
    typer.echo("Inference:")
    typer.echo(f"* {inference.derived}")
    typer.echo("")
    typer.echo("Outcome:")
    typer.echo(f"* {outcome.result}")
    typer.echo("")
    typer.echo("Revision:")
    for change in revision.changes:
        typer.echo(f"* {change}")


@app.command()
def counter_demo() -> None:
    """Run the hard-coded counter revision demo."""

    program = build_counter_revision_demo_program()
    revision = program.history[-1]
    outcome = revision.outcome
    inference = outcome.inference

    typer.echo("Datum: counter = 0; counter = counter + 1")
    typer.echo("")
    typer.echo("Dicta:")
    for dictum in program.concept.dicta:
        typer.echo(f"* {dictum_text(dictum)}")
    typer.echo("")
    typer.echo("Purpose:")
    typer.echo(f"* {program.concept.purpose.statement}")
    typer.echo("")
    typer.echo("Inference:")
    typer.echo(f"* {inference.derived}")
    typer.echo("")
    typer.echo("Outcome:")
    typer.echo(f"* {outcome.result}")
    typer.echo("")
    typer.echo("Revision:")
    for change in revision.changes:
        typer.echo(f"* {change}")
