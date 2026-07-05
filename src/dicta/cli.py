"""Typer command-line interface for Dicta."""

from importlib.metadata import PackageNotFoundError, version as metadata_version

import typer

from dicta import __version__
from dicta.core.appraise import (
    ArithmeticDatum,
    CounterIncrementDatum,
    appraise_arithmetic_datum,
    appraise_counter_revision_datum,
)
from dicta.core.models import Program
from dicta.core.program import (
    build_agent_edit_demo_program,
    build_arithmetic_demo_program,
    build_counter_revision_demo_program,
    build_file_write_demo_program,
    build_invalid_arithmetic_demo_program,
    build_refused_agent_edit_demo_program,
    build_refused_file_write_demo_program,
    build_supervised_worker_demo_program,
    dictum_text,
)

app = typer.Typer(help="Dicta semantic-kernel prototype.")


def package_version() -> str:
    """Return installed package version, falling back to source version."""

    try:
        return metadata_version("dicta")
    except PackageNotFoundError:
        return __version__


def _echo_section(title: str, items: list[object]) -> None:
    typer.echo("")
    typer.echo(f"{title}:")
    for item in items:
        typer.echo(f"* {item}")


def _qualification_text(program: Program) -> list[str]:
    items: list[str] = []
    for dictum in program.concept.dicta:
        qualification = dictum.qualification
        conditions = ", ".join(qualification.conditions) or "none"
        items.append(
            f"{dictum.visible_text()}: "
            f"{qualification.strength.value}; "
            f"basis={qualification.basis or 'unspecified'}; "
            f"conditions={conditions}; "
            f"timing={qualification.timing}"
        )
    return items


def _render_demo(
    program: Program,
    datum: str,
    *,
    show_qualification: bool = False,
    show_purpose: bool = True,
    show_disparity: bool = False,
    show_inference: bool = True,
) -> None:
    revision = program.history[-1]
    outcome = revision.outcome
    inference = outcome.inference

    typer.echo(f"Datum: {datum}")
    _echo_section("Dicta", [dictum_text(dictum) for dictum in program.concept.dicta])
    if show_qualification:
        _echo_section("Qualification", _qualification_text(program))
    if show_purpose and program.concept.purpose is not None:
        _echo_section("Purpose", [program.concept.purpose.statement])
    if show_disparity:
        _echo_section("Disparity", [inference.from_disparity.description])
    if show_inference:
        _echo_section("Inference", [inference.derived])
    _echo_section("Outcome", [outcome.result])
    _echo_section("Revision", revision.changes)


@app.command()
def version() -> None:
    """Print the package version."""

    typer.echo(package_version())


@app.command()
def demo() -> None:
    """Run the hard-coded 3 + 4 semantic demo."""

    _render_demo(
        build_arithmetic_demo_program(),
        "3 + 4",
        show_qualification=True,
        show_purpose=False,
        show_inference=False,
    )


@app.command()
def appraise_arithmetic_demo() -> None:
    """Run the mechanically appraised structured arithmetic demo."""

    datum = ArithmeticDatum(left=3, operator="+", right=4)
    _render_demo(
        appraise_arithmetic_datum(datum),
        datum.expression_text(),
        show_qualification=True,
        show_purpose=True,
        show_inference=True,
    )


@app.command()
def appraise_invalid_arithmetic_demo() -> None:
    """Run the mechanically appraised structured invalid arithmetic demo."""

    datum = ArithmeticDatum(left=3, operator="+", right="cat")
    _render_demo(
        appraise_arithmetic_datum(datum),
        datum.expression_text(),
        show_purpose=True,
        show_disparity=True,
        show_inference=True,
    )


@app.command()
def invalid_demo() -> None:
    """Run the hard-coded 3 + "cat" disparity demo."""

    _render_demo(
        build_invalid_arithmetic_demo_program(),
        '3 + "cat"',
        show_disparity=True,
    )


@app.command()
def counter_demo() -> None:
    """Run the hard-coded counter revision demo."""

    _render_demo(
        build_counter_revision_demo_program(),
        "counter = 0; counter = counter + 1",
    )


@app.command()
def appraise_counter_demo() -> None:
    """Run the mechanically appraised structured counter revision demo."""

    datum = CounterIncrementDatum(name="counter", initial=0, increment=1)
    _render_demo(
        appraise_counter_revision_datum(datum),
        datum.statement_text(),
        show_qualification=True,
        show_purpose=True,
        show_inference=True,
    )


@app.command()
def appraise_refused_counter_demo() -> None:
    """Run the mechanically refused structured counter revision demo."""

    datum = CounterIncrementDatum(name="counter", initial="cat", increment=1)
    _render_demo(
        appraise_counter_revision_datum(datum),
        datum.statement_text(),
        show_purpose=True,
        show_disparity=True,
        show_inference=True,
    )


@app.command()
def file_write_demo() -> None:
    """Run the hard-coded file write effect demo."""

    _render_demo(build_file_write_demo_program(), 'write report.txt "hello"')


@app.command()
def refused_file_write_demo() -> None:
    """Run the hard-coded refused file write effect demo."""

    _render_demo(
        build_refused_file_write_demo_program(),
        'write protected/report.txt "hello"',
        show_disparity=True,
    )


@app.command()
def supervised_worker_demo() -> None:
    """Run the hard-coded supervised worker failure demo."""

    _render_demo(
        build_supervised_worker_demo_program(),
        "worker Outcome is crash",
        show_disparity=True,
    )


@app.command()
def agent_edit_demo() -> None:
    """Run the hard-coded AI agent edit demo."""

    _render_demo(
        build_agent_edit_demo_program(),
        "agent proposes replace add_one(x) = x + 1 with add_one(x) = 1 + x",
    )


@app.command()
def refused_agent_edit_demo() -> None:
    """Run the hard-coded refused AI agent edit demo."""

    _render_demo(
        build_refused_agent_edit_demo_program(),
        "agent proposes replace add_one(x) = x + 1 with add_one(x) = x + 2",
        show_disparity=True,
    )
