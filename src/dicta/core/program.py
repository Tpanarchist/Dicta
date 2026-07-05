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


def _make_qualification(
    strength: QualificationStrength,
    basis: str,
    conditions: list[str],
    timing: str,
) -> Qualification:
    return Qualification(
        strength=strength,
        basis=basis,
        conditions=conditions,
        timing=timing,
    )


def _make_concept(
    name: str,
    purpose_statement: str,
    mode: str = "demo",
) -> tuple[Concept, Purpose]:
    purpose = Purpose(statement=purpose_statement, mode=mode)
    return Concept(name=name, purpose=purpose), purpose


def _make_dictum(
    subject: str,
    meaning: str,
    qualification: Qualification,
    display: str,
) -> Dictum:
    return produce_dictum(subject, meaning, qualification, {"display": display})


def _add_dicta(
    concept: Concept,
    dicta: list[tuple[str, str, Qualification, str]],
) -> None:
    for subject, meaning, qualification, display in dicta:
        add_dictum(concept, _make_dictum(subject, meaning, qualification, display))


def _make_program(name: str, concept: Concept, revision: Revision) -> Program:
    program = Program(name=name, concept=concept)
    return append_revision(program, revision)


def build_arithmetic_demo_program() -> Program:
    """Build the hard-coded semantic representation for 3 + 4."""

    datum = receive_datum("3 + 4", source="dicta demo", note="hard-coded arithmetic")
    concept, purpose = _make_concept(
        "arithmetic-demo",
        "Represent evaluated arithmetic as qualified meaning.",
    )

    literal_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="hard-coded literal recognition",
        conditions=["demo input"],
        timing="demo",
    )
    operator_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="arithmetic convention",
        conditions=["demo input"],
        timing="demo",
    )
    result_qualification = _make_qualification(
        strength=QualificationStrength.TESTED,
        basis="evaluation",
        conditions=["integer addition"],
        timing="demo",
    )

    _add_dicta(
        concept,
        [
            ("3", "Number", literal_qualification, "3 is Number"),
            ("4", "Number", literal_qualification, "4 is Number"),
            (
                "+",
                "accepts Number, Number",
                operator_qualification,
                "+ accepts Number, Number",
            ),
            ("3 + 4", "7", result_qualification, "3 + 4 is 7"),
        ],
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
    return _make_program("arithmetic-demo", concept, revision)


def build_invalid_arithmetic_demo_program() -> Program:
    """Build the hard-coded disparity representation for 3 + "cat"."""

    datum = receive_datum(
        '3 + "cat"',
        source="dicta demo",
        note="hard-coded invalid arithmetic",
    )
    concept, purpose = _make_concept(
        "invalid-arithmetic-demo",
        "evaluate arithmetic expression",
    )

    literal_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="hard-coded literal recognition",
        conditions=["demo input"],
        timing="demo",
    )
    operator_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="arithmetic convention",
        conditions=["demo input"],
        timing="demo",
    )

    _add_dicta(
        concept,
        [
            ("3", "Number", literal_qualification, "3 is Number"),
            ('"cat"', "Text", literal_qualification, '"cat" is Text'),
            (
                "+",
                "accepts Number, Number",
                operator_qualification,
                "+ accepts Number, Number",
            ),
        ],
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
    return _make_program("invalid-arithmetic-demo", concept, revision)


def build_counter_revision_demo_program() -> Program:
    """Build the hard-coded revision representation for counter increment."""

    datum = receive_datum(
        "counter = 0; counter = counter + 1",
        source="dicta demo",
        note="hard-coded counter revision",
    )
    concept, purpose = _make_concept(
        "counter-revision-demo",
        "revise counter by valid increment",
    )

    type_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="counter binding",
        conditions=["demo input"],
        timing="before revision",
    )
    value_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="counter state",
        conditions=["demo input"],
        timing="before revision",
    )
    operator_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="arithmetic convention",
        conditions=["Number, Number"],
        timing="during revision",
    )
    revision_qualification = _make_qualification(
        strength=QualificationStrength.TESTED,
        basis="valid increment",
        conditions=["counter is Number", "counter is 0"],
        timing="after revision",
    )

    _add_dicta(
        concept,
        [
            ("counter", "Number", type_qualification, "counter is Number"),
            ("counter", "0", value_qualification, "counter is 0"),
            (
                "+",
                "accepts Number, Number",
                operator_qualification,
                "+ accepts Number, Number",
            ),
            ("counter + 1", "1", revision_qualification, "counter + 1 is 1"),
            ("counter", "1", revision_qualification, "counter is 1"),
        ],
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
    return _make_program("counter-revision-demo", concept, revision)


def build_file_write_demo_program() -> Program:
    """Build the hard-coded effect representation for an accepted file write."""

    datum = receive_datum(
        'write report.txt "hello"',
        source="dicta demo",
        note="hard-coded file write effect",
    )
    concept, purpose = _make_concept("file-write-demo", "persist text to file")

    input_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="hard-coded write input",
        conditions=["demo input"],
        timing="before effect",
    )
    operation_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="file write effect contract",
        conditions=["FilePath", "Text"],
        timing="before effect",
    )
    permission_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="demo permission grant",
        conditions=["report.txt"],
        timing="before effect",
    )
    effect_qualification = _make_qualification(
        strength=QualificationStrength.TESTED,
        basis="accepted write effect",
        conditions=["Permission qualifies for report.txt"],
        timing="after effect",
    )

    _add_dicta(
        concept,
        [
            ("report.txt", "FilePath", input_qualification, "report.txt is FilePath"),
            ('"hello"', "Text", input_qualification, '"hello" is Text'),
            (
                "write",
                "accepts FilePath, Text",
                operation_qualification,
                "write accepts FilePath, Text",
            ),
            ("write", "changes Disk", operation_qualification, "write changes Disk"),
            (
                "write",
                "requires Permission",
                operation_qualification,
                "write requires Permission",
            ),
            (
                "Permission",
                "qualifies for report.txt",
                permission_qualification,
                "Permission qualifies for report.txt",
            ),
            (
                "report.txt",
                'contains "hello"',
                effect_qualification,
                'report.txt contains "hello"',
            ),
        ],
    )

    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description='report.txt does not yet contain "hello"',
        severity="effect",
    )
    inference = Inference(
        from_disparity=disparity,
        derived="write may proceed because Permission qualifies",
        basis="write requires Permission and Permission qualifies for report.txt",
    )
    outcome = create_outcome(
        inference=inference,
        result="write accepted",
        status="accepted",
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            'Concept records report.txt contains "hello"',
            "Concept records Disk changed by write",
        ],
        note="Disk changed by write",
    )
    return _make_program("file-write-demo", concept, revision)


def build_refused_file_write_demo_program() -> Program:
    """Build the hard-coded effect representation for a refused file write."""

    datum = receive_datum(
        'write protected/report.txt "hello"',
        source="dicta demo",
        note="hard-coded refused file write effect",
    )
    concept, purpose = _make_concept(
        "refused-file-write-demo",
        "persist text to file",
    )

    input_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="hard-coded write input",
        conditions=["demo input"],
        timing="before refusal",
    )
    operation_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="file write effect contract",
        conditions=["FilePath", "Text"],
        timing="before refusal",
    )
    permission_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="demo permission denial",
        conditions=["protected/report.txt"],
        timing="before refusal",
    )

    _add_dicta(
        concept,
        [
            (
                "protected/report.txt",
                "FilePath",
                input_qualification,
                "protected/report.txt is FilePath",
            ),
            ('"hello"', "Text", input_qualification, '"hello" is Text'),
            (
                "write",
                "accepts FilePath, Text",
                operation_qualification,
                "write accepts FilePath, Text",
            ),
            ("write", "changes Disk", operation_qualification, "write changes Disk"),
            (
                "write",
                "requires Permission",
                operation_qualification,
                "write requires Permission",
            ),
            (
                "Permission",
                "does not qualify for protected/report.txt",
                permission_qualification,
                "Permission does not qualify for protected/report.txt",
            ),
        ],
    )

    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description="write lacks Permission for protected/report.txt",
        severity="refusing",
    )
    inference = Inference(
        from_disparity=disparity,
        derived="refuse write because Permission does not qualify",
        basis="write requires Permission and Permission does not qualify",
    )
    outcome = create_outcome(
        inference=inference,
        result="write refused",
        status="refused",
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            "Concept records denied write attempt",
            "Concept preserves Disk unchanged",
        ],
        note="denied write attempt; Disk unchanged",
    )
    return _make_program("refused-file-write-demo", concept, revision)


def build_supervised_worker_demo_program() -> Program:
    """Build the hard-coded representation for supervised worker recovery."""

    datum = receive_datum(
        "worker Outcome is crash",
        source="dicta demo",
        note="hard-coded supervised worker failure",
    )
    concept, purpose = _make_concept(
        "supervised-worker-demo",
        "keep worker available",
    )

    worker_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="supervisor concept",
        conditions=["demo input"],
        timing="before crash",
    )
    supervision_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="availability purpose",
        conditions=["worker"],
        timing="before crash",
    )
    failure_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="observed child outcome",
        conditions=["worker Outcome"],
        timing="after crash",
    )
    restart_qualification = _make_qualification(
        strength=QualificationStrength.TESTED,
        basis="known-good worker Concept",
        conditions=["worker is Program", "known-good worker Concept exists"],
        timing="after restart",
    )

    _add_dicta(
        concept,
        [
            ("worker", "Program", worker_qualification, "worker is Program"),
            ("worker", "Alive", worker_qualification, "worker is Alive"),
            (
                "worker",
                "serves background task",
                worker_qualification,
                "worker serves background task",
            ),
            (
                "supervisor",
                "requires worker Alive",
                supervision_qualification,
                "supervisor requires worker Alive",
            ),
            (
                "worker Outcome",
                "crash",
                failure_qualification,
                "worker Outcome is crash",
            ),
            ("worker", "not Alive", failure_qualification, "worker is not Alive"),
            (
                "known-good worker Concept",
                "exists",
                supervision_qualification,
                "known-good worker Concept exists",
            ),
            (
                "worker restart",
                "accepted",
                restart_qualification,
                "worker restart accepted",
            ),
            ("worker", "Alive", restart_qualification, "worker is Alive"),
        ],
    )

    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description="worker is not Alive under availability Purpose",
        severity="recovering",
    )
    inference = Inference(
        from_disparity=disparity,
        derived="restart worker from known-good Concept",
        basis="supervisor requires worker Alive",
    )
    outcome = create_outcome(
        inference=inference,
        result="worker restarted",
        status="restarted",
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            "Concept records worker crash",
            "Concept records worker restarted",
            "Concept restores worker is Alive",
        ],
        note="worker restarted; restores worker is Alive",
    )
    return _make_program("supervisor-demo", concept, revision)
