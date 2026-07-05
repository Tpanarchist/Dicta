"""Small helpers that demonstrate Dicta program motion."""

from __future__ import annotations

from typing import Any

from dicta.core.models import (
    Concept,
    Datum,
    Dictum,
    Disparity,
    Inference,
    Outcome,
    Program,
    Purpose,
    Qualification,
    Revision,
)
from dicta.core.qualification import QualificationStrength


def receive_datum(value: Any, source: str | None = None, note: str | None = None) -> Datum:
    """Receive material before meaning is settled."""

    return Datum(value=value, source=source, note=note)


def produce_dictum(
    subject: str,
    meaning: str,
    qualification: Qualification | None = None,
    metadata: dict[str, Any] | None = None,
) -> Dictum:
    """Produce a bounded statement of meaning."""

    return Dictum(
        subject=subject,
        meaning=meaning,
        qualification=qualification or Qualification(),
        metadata=metadata or {},
    )


def attach_qualification(dictum: Dictum, qualification: Qualification) -> Dictum:
    """Attach a Qualification to a Dictum."""

    return dictum.model_copy(update={"qualification": qualification})


def add_dictum(concept: Concept, dictum: Dictum) -> Concept:
    """Add a Dictum to a Concept."""

    concept.dicta.append(dictum)
    return concept


def create_outcome(inference: Inference, result: Any, status: str = "observed") -> Outcome:
    """Create an Outcome from an Inference."""

    return Outcome(inference=inference, result=result, status=status)


def create_revision(
    outcome: Outcome,
    changes: list[str] | None = None,
    note: str | None = None,
) -> Revision:
    """Create a Revision from an Outcome."""

    return Revision(outcome=outcome, changes=changes or [], note=note)


def append_revision(program: Program, revision: Revision) -> Program:
    """Append a Revision to Program history."""

    program.history.append(revision)
    return program


def dictum_text(dictum: Dictum) -> str:
    """Render a Dictum for the plain-text demo."""

    display = dictum.metadata.get("display")
    if isinstance(display, str):
        return display
    return f"{dictum.subject} is {dictum.meaning}"


def build_arithmetic_demo_program() -> Program:
    """Build the hard-coded semantic representation for 3 + 4."""

    datum = receive_datum("3 + 4", source="dicta demo", note="hard-coded arithmetic")
    purpose = Purpose(
        statement="Represent evaluated arithmetic as qualified meaning.",
        mode="demo",
    )
    concept = Concept(name="arithmetic-demo", purpose=purpose)

    literal_qualification = Qualification(
        strength=QualificationStrength.CHECKED,
        basis="hard-coded literal recognition",
        conditions=["demo input"],
        timing="demo",
    )
    operator_qualification = Qualification(
        strength=QualificationStrength.ASSERTED,
        basis="arithmetic convention",
        conditions=["demo input"],
        timing="demo",
    )
    result_qualification = Qualification(
        strength=QualificationStrength.TESTED,
        basis="evaluation",
        conditions=["integer addition"],
        timing="demo",
    )

    add_dictum(
        concept,
        produce_dictum("3", "Number", literal_qualification, {"display": "3 is Number"}),
    )
    add_dictum(
        concept,
        produce_dictum("4", "Number", literal_qualification, {"display": "4 is Number"}),
    )
    add_dictum(
        concept,
        produce_dictum(
            "+",
            "accepts Number, Number",
            operator_qualification,
            {"display": "+ accepts Number, Number"},
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "3 + 4",
            "7",
            result_qualification,
            {"display": "3 + 4 is 7"},
        ),
    )

    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description="The received arithmetic datum lacks an evaluated result.",
        severity="low",
    )
    inference = Inference(
        from_disparity=disparity,
        derived="3 + 4 is 7",
        basis="integer addition",
    )
    outcome = create_outcome(inference=inference, result=7, status="evaluated")
    revision = create_revision(
        outcome=outcome,
        changes=["concept records evaluated arithmetic dictum"],
        note="result qualifies by evaluation",
    )
    program = Program(name="arithmetic-demo", concept=concept)
    return append_revision(program, revision)


def build_invalid_arithmetic_demo_program() -> Program:
    """Build the hard-coded disparity representation for 3 + "cat"."""

    datum = receive_datum(
        '3 + "cat"',
        source="dicta demo",
        note="hard-coded invalid arithmetic",
    )
    purpose = Purpose(statement="evaluate arithmetic expression", mode="demo")
    concept = Concept(name="invalid-arithmetic-demo", purpose=purpose)

    literal_qualification = Qualification(
        strength=QualificationStrength.CHECKED,
        basis="hard-coded literal recognition",
        conditions=["demo input"],
        timing="demo",
    )
    operator_qualification = Qualification(
        strength=QualificationStrength.ASSERTED,
        basis="arithmetic convention",
        conditions=["demo input"],
        timing="demo",
    )

    add_dictum(
        concept,
        produce_dictum("3", "Number", literal_qualification, {"display": "3 is Number"}),
    )
    add_dictum(
        concept,
        produce_dictum(
            '"cat"',
            "Text",
            literal_qualification,
            {"display": '"cat" is Text'},
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "+",
            "accepts Number, Number",
            operator_qualification,
            {"display": "+ accepts Number, Number"},
        ),
    )

    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description="+ does not qualify for Number, Text",
        severity="rejecting",
    )
    inference = Inference(
        from_disparity=disparity,
        derived="reject expression as invalid arithmetic",
        basis="operand qualification mismatch",
    )
    outcome = create_outcome(
        inference=inference,
        result="evaluation refused",
        status="refused",
    )
    revision = create_revision(
        outcome=outcome,
        changes=["Concept records invalid operand disparity"],
        note="disparity qualifies refusal",
    )
    program = Program(name="invalid-arithmetic-demo", concept=concept)
    return append_revision(program, revision)


def build_counter_revision_demo_program() -> Program:
    """Build the hard-coded revision representation for counter increment."""

    datum = receive_datum(
        "counter = 0; counter = counter + 1",
        source="dicta demo",
        note="hard-coded counter revision",
    )
    purpose = Purpose(statement="revise counter by valid increment", mode="demo")
    concept = Concept(name="counter-revision-demo", purpose=purpose)

    type_qualification = Qualification(
        strength=QualificationStrength.CHECKED,
        basis="counter binding",
        conditions=["demo input"],
        timing="before revision",
    )
    value_qualification = Qualification(
        strength=QualificationStrength.CHECKED,
        basis="counter state",
        conditions=["demo input"],
        timing="before revision",
    )
    operator_qualification = Qualification(
        strength=QualificationStrength.ASSERTED,
        basis="arithmetic convention",
        conditions=["Number, Number"],
        timing="during revision",
    )
    revision_qualification = Qualification(
        strength=QualificationStrength.TESTED,
        basis="valid increment",
        conditions=["counter is Number", "counter is 0"],
        timing="after revision",
    )

    add_dictum(
        concept,
        produce_dictum(
            "counter",
            "Number",
            type_qualification,
            {"display": "counter is Number"},
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "counter",
            "0",
            value_qualification,
            {"display": "counter is 0"},
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "+",
            "accepts Number, Number",
            operator_qualification,
            {"display": "+ accepts Number, Number"},
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "counter + 1",
            "1",
            revision_qualification,
            {"display": "counter + 1 is 1"},
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "counter",
            "1",
            revision_qualification,
            {"display": "counter is 1"},
        ),
    )

    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description="counter is 0 before a valid increment revision",
        severity="revision",
    )
    inference = Inference(
        from_disparity=disparity,
        derived="counter may revise from 0 to 1",
        basis="counter is Number and + accepts Number, Number",
    )
    outcome = create_outcome(
        inference=inference,
        result="counter is 1",
        status="revised",
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            "Concept replaces counter is 0 with counter is 1",
            "Concept preserves counter is Number",
        ],
        note="counter is 0 to counter is 1",
    )
    program = Program(name="counter-revision-demo", concept=concept)
    return append_revision(program, revision)
