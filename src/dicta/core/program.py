"""Small helpers that demonstrate Dicta program motion."""

from __future__ import annotations

from dataclasses import dataclass
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
    RevisionOperation,
)
from dicta.core.qualification import QualificationStrength


def receive_datum(
    value: Any,
    source: str | None = None,
    note: str | None = None,
) -> Datum:
    """Receive material before meaning is settled."""

    return Datum(value=value, source=source, note=note)


def produce_dictum(
    subject: str,
    meaning: str,
    qualification: Qualification | None = None,
    display: str | None = None,
    metadata: dict[str, Any] | None = None,
    kind: str | None = None,
    tags: tuple[str, ...] = (),
) -> Dictum:
    """Produce a bounded statement of meaning."""

    return Dictum(
        subject=subject,
        meaning=meaning,
        qualification=qualification or Qualification(),
        display=display,
        metadata=metadata or {},
        kind=kind,
        tags=tags,
    )


def add_dictum(concept: Concept, dictum: Dictum) -> Concept:
    """Add a Dictum to a Concept."""

    concept.dicta.append(dictum)
    return concept


def create_outcome(
    inference: Inference,
    result: Any,
    status: str = "observed",
    kind: str | None = None,
    tags: tuple[str, ...] = (),
) -> Outcome:
    """Create an Outcome from an Inference."""

    return Outcome(
        inference=inference,
        result=result,
        status=status,
        kind=kind,
        tags=tags,
    )


def create_revision(
    outcome: Outcome,
    changes: list[str] | None = None,
    note: str | None = None,
    kind: str | None = None,
    tags: tuple[str, ...] = (),
    operations: tuple[RevisionOperation, ...] = (),
) -> Revision:
    """Create a Revision from an Outcome."""

    return Revision(
        outcome=outcome,
        changes=changes or [],
        note=note,
        kind=kind,
        tags=tags,
        operations=operations,
    )


def append_revision(program: Program, revision: Revision) -> Program:
    """Append a Revision to Program history."""

    program.history.append(revision)
    return program


def dictum_text(dictum: Dictum) -> str:
    """Render a Dictum for the plain-text demo."""

    return dictum.visible_text()


@dataclass(frozen=True)
class _DictumSpec:
    subject: str
    meaning: str
    qualification: Qualification
    display: str
    kind: str | None = None
    tags: tuple[str, ...] = ()


def _make_qualification(
    strength: QualificationStrength,
    basis: str,
    conditions: tuple[str, ...],
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
    kind: str | None = None,
    tags: tuple[str, ...] = (),
) -> Dictum:
    return produce_dictum(
        subject,
        meaning,
        qualification,
        display=display,
        kind=kind,
        tags=tags,
    )


def _add_dicta(
    concept: Concept,
    dicta: list[_DictumSpec],
) -> None:
    for spec in dicta:
        add_dictum(
            concept,
            _make_dictum(
                spec.subject,
                spec.meaning,
                spec.qualification,
                spec.display,
                spec.kind,
                spec.tags,
            ),
        )


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
        conditions=("demo input",),
        timing="demo-time",
    )
    operator_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="arithmetic concept",
        conditions=("Number operands",),
        timing="demo-time",
    )
    result_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="hard-coded arithmetic evaluation",
        conditions=("Number operands",),
        timing="demo-time",
    )

    _add_dicta(
        concept,
        [
            _DictumSpec("3", "Number", literal_qualification, "3 is Number"),
            _DictumSpec("4", "Number", literal_qualification, "4 is Number"),
            _DictumSpec(
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
        description="The received arithmetic datum lacks an evaluated result.",
        severity="low",
    )
    _add_dicta(
        concept,
        [
            _DictumSpec(
                "3 + 4",
                "7",
                result_qualification,
                "3 + 4 is 7",
            ),
        ],
    )
    inference = Inference(
        from_disparity=disparity,
        derived="3 + 4 is 7",
        basis="integer addition",
    )
    outcome = create_outcome(
        inference=inference,
        result=7,
        status="evaluated",
        kind="value",
        tags=("arithmetic",),
    )
    revision = create_revision(
        outcome=outcome,
        changes=["concept records evaluated arithmetic dictum"],
        note="result qualifies by evaluation",
        kind="record_result",
        tags=("arithmetic",),
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
        conditions=("demo input",),
        timing="demo-time",
    )
    operator_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="arithmetic concept",
        conditions=("Number operands",),
        timing="demo-time",
    )

    _add_dicta(
        concept,
        [
            _DictumSpec("3", "Number", literal_qualification, "3 is Number"),
            _DictumSpec('"cat"', "Text", literal_qualification, '"cat" is Text'),
            _DictumSpec(
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
        kind="type_mismatch",
        tags=("arithmetic",),
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
        kind="refusal",
        tags=("arithmetic",),
    )
    revision = create_revision(
        outcome=outcome,
        changes=["Concept records invalid operand disparity"],
        note="disparity qualifies refusal",
        kind="record_result",
        tags=("arithmetic", "refusal"),
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
        conditions=("demo input",),
        timing="before revision",
    )
    value_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="counter state",
        conditions=("demo input",),
        timing="before revision",
    )
    operator_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="arithmetic convention",
        conditions=("Number, Number",),
        timing="during revision",
    )
    revision_qualification = _make_qualification(
        strength=QualificationStrength.TESTED,
        basis="valid increment",
        conditions=("counter is Number", "counter is 0"),
        timing="after revision",
    )

    _add_dicta(
        concept,
        [
            _DictumSpec(
                "counter",
                "Number",
                type_qualification,
                "counter is Number",
            ),
            _DictumSpec("counter", "0", value_qualification, "counter is 0"),
            _DictumSpec(
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
        description="counter is 0 before a valid increment revision",
        severity="revision",
    )
    concept.dicta = [
        dictum
        for dictum in concept.dicta
        if not (dictum.subject == "counter" and dictum.meaning == "0")
    ]
    _add_dicta(
        concept,
        [
            _DictumSpec(
                "counter + 1",
                "1",
                revision_qualification,
                "counter + 1 is 1",
            ),
            _DictumSpec("counter", "1", revision_qualification, "counter is 1"),
        ],
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
        kind="value",
        tags=("counter",),
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            "Concept replaces counter is 0 with counter is 1",
            "Concept preserves counter is Number",
        ],
        note="counter is 0 to counter is 1",
        kind="replace_value",
        tags=("counter",),
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
        conditions=("demo input",),
        timing="before effect",
    )
    operation_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="file write effect contract",
        conditions=("FilePath", "Text"),
        timing="before effect",
    )
    permission_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="demo permission policy",
        conditions=("target is report.txt",),
        timing="demo-time",
    )
    effect_qualification = _make_qualification(
        strength=QualificationStrength.TESTED,
        basis="accepted write effect",
        conditions=("Permission qualifies for report.txt",),
        timing="after effect",
    )

    _add_dicta(
        concept,
        [
            _DictumSpec(
                "report.txt",
                "FilePath",
                input_qualification,
                "report.txt is FilePath",
            ),
            _DictumSpec('"hello"', "Text", input_qualification, '"hello" is Text'),
            _DictumSpec(
                "write",
                "accepts FilePath, Text",
                operation_qualification,
                "write accepts FilePath, Text",
            ),
            _DictumSpec(
                "write",
                "changes Disk",
                operation_qualification,
                "write changes Disk",
                "effect",
                ("disk", "write"),
            ),
            _DictumSpec(
                "write",
                "requires Permission",
                operation_qualification,
                "write requires Permission",
                "permission",
                ("write",),
            ),
            _DictumSpec(
                "Permission",
                "qualifies for report.txt",
                permission_qualification,
                "Permission qualifies for report.txt",
                "permission",
                ("write", "report.txt"),
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
    _add_dicta(
        concept,
        [
            _DictumSpec(
                "report.txt",
                'contains "hello"',
                effect_qualification,
                'report.txt contains "hello"',
                "effect",
                ("disk", "report.txt"),
            ),
        ],
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
        kind="effect_accepted",
        tags=("disk", "write"),
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            'Concept records report.txt contains "hello"',
            "Concept records Disk changed by write",
        ],
        note="Disk changed by write",
        kind="record_effect",
        tags=("disk", "write"),
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
        conditions=("demo input",),
        timing="before refusal",
    )
    operation_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="file write effect contract",
        conditions=("FilePath", "Text"),
        timing="before refusal",
    )
    permission_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="demo permission policy",
        conditions=("target is protected/report.txt",),
        timing="demo-time",
    )

    _add_dicta(
        concept,
        [
            _DictumSpec(
                "protected/report.txt",
                "FilePath",
                input_qualification,
                "protected/report.txt is FilePath",
            ),
            _DictumSpec('"hello"', "Text", input_qualification, '"hello" is Text'),
            _DictumSpec(
                "write",
                "accepts FilePath, Text",
                operation_qualification,
                "write accepts FilePath, Text",
            ),
            _DictumSpec(
                "write",
                "changes Disk",
                operation_qualification,
                "write changes Disk",
                "effect",
                ("disk", "write"),
            ),
            _DictumSpec(
                "write",
                "requires Permission",
                operation_qualification,
                "write requires Permission",
                "permission",
                ("write",),
            ),
            _DictumSpec(
                "Permission",
                "does not qualify for protected/report.txt",
                permission_qualification,
                "Permission does not qualify for protected/report.txt",
                "permission",
                ("write", "protected/report.txt"),
            ),
        ],
    )

    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description="write lacks Permission for protected/report.txt",
        severity="refusing",
        kind="permission_denied",
        tags=("write", "protected/report.txt"),
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
        kind="effect_refused",
        tags=("disk", "write"),
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            "Concept records denied write attempt",
            "Concept preserves Disk unchanged",
        ],
        note="denied write attempt; Disk unchanged",
        kind="preserve_state",
        tags=("disk", "write"),
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
        conditions=("demo input",),
        timing="before crash",
    )
    supervision_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="availability purpose",
        conditions=("worker",),
        timing="before crash",
    )
    failure_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="observed child outcome",
        conditions=("worker Outcome",),
        timing="after crash",
    )
    restart_qualification = _make_qualification(
        strength=QualificationStrength.TESTED,
        basis="known-good worker Concept",
        conditions=("worker is Program", "known-good worker Concept exists"),
        timing="after restart",
    )

    _add_dicta(
        concept,
        [
            _DictumSpec("worker", "Program", worker_qualification, "worker is Program"),
            _DictumSpec("worker", "Alive", worker_qualification, "worker is Alive"),
            _DictumSpec(
                "worker",
                "serves background task",
                worker_qualification,
                "worker serves background task",
            ),
            _DictumSpec(
                "supervisor",
                "requires worker Alive",
                supervision_qualification,
                "supervisor requires worker Alive",
            ),
            _DictumSpec(
                "worker Outcome",
                "crash",
                failure_qualification,
                "worker Outcome is crash",
            ),
            _DictumSpec(
                "worker",
                "not Alive",
                failure_qualification,
                "worker is not Alive",
            ),
            _DictumSpec(
                "known-good worker Concept",
                "exists",
                supervision_qualification,
                "known-good worker Concept exists",
            ),
        ],
    )

    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description="worker is not Alive under availability Purpose",
        severity="recovering",
        kind="worker_unavailable",
        tags=("worker", "supervision"),
    )
    _add_dicta(
        concept,
        [
            _DictumSpec(
                "worker restart",
                "accepted",
                restart_qualification,
                "worker restart accepted",
            ),
            _DictumSpec("worker", "Alive", restart_qualification, "worker is Alive"),
        ],
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
        kind="restart",
        tags=("worker", "supervision"),
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            "Concept records worker crash",
            "Concept records worker restarted",
            "Concept restores worker is Alive",
        ],
        note="worker restarted; restores worker is Alive",
        kind="restore_state",
        tags=("worker", "supervision"),
    )
    return _make_program("supervised-worker-demo", concept, revision)


def build_agent_edit_demo_program() -> Program:
    """Build the hard-coded representation for appraising an AI edit proposal."""

    datum = receive_datum(
        "agent proposes: replace add_one(x) = x + 1 with add_one(x) = 1 + x",
        source="dicta demo",
        note="hard-coded AI agent edit proposal",
    )
    concept, purpose = _make_concept(
        "agent-edit-demo",
        "preserve behavior while improving form",
    )

    proposal_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="agent proposal",
        conditions=("untrusted input",),
        timing="before appraisal",
    )
    behavior_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="add_one contract",
        conditions=("Number",),
        timing="during appraisal",
    )
    equivalence_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="commutative addition for Number",
        conditions=("x is Number",),
        timing="during appraisal",
    )
    acceptance_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="commutativity over Number",
        conditions=("x is Number",),
        timing="demo-time",
    )

    _add_dicta(
        concept,
        [
            _DictumSpec(
                "agent edit",
                "Datum",
                proposal_qualification,
                "agent edit is Datum",
                "agent",
                ("proposal",),
            ),
            _DictumSpec(
                "add_one",
                "accepts Number",
                behavior_qualification,
                "add_one accepts Number",
            ),
            _DictumSpec(
                "add_one",
                "returns Number",
                behavior_qualification,
                "add_one returns Number",
            ),
            _DictumSpec(
                "x + 1",
                "equals 1 + x for Number",
                equivalence_qualification,
                "x + 1 equals 1 + x for Number",
                "equivalence",
                ("add_one", "number"),
            ),
        ],
    )

    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description="agent edit is Datum before behavior Qualification",
        severity="appraising",
    )
    _add_dicta(
        concept,
        [
            _DictumSpec(
                "agent edit",
                "preserves add_one behavior",
                acceptance_qualification,
                "agent edit preserves add_one behavior",
                "behavior",
                ("agent", "add_one"),
            ),
            _DictumSpec(
                "agent edit",
                "qualifies by checked equivalence",
                acceptance_qualification,
                "agent edit qualifies by checked equivalence",
                "agent",
                ("checked_equivalence",),
            ),
        ],
    )
    inference = Inference(
        from_disparity=disparity,
        derived="accept agent edit because behavior qualifies",
        basis="checked equivalence preserves add_one behavior",
    )
    outcome = create_outcome(
        inference=inference,
        result="agent edit accepted",
        status="accepted",
        kind="agent_acceptance",
        tags=("agent", "add_one"),
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            "Concept records accepted agent edit",
            "Concept preserves add_one behavior",
        ],
        note="agent edit accepted; preserves add_one behavior",
        kind="accept_agent_edit",
        tags=("agent", "add_one"),
    )
    return _make_program("agent-edit-demo", concept, revision)


def build_refused_agent_edit_demo_program() -> Program:
    """Build the hard-coded representation for refusing an AI edit proposal."""

    datum = receive_datum(
        "agent proposes: replace add_one(x) = x + 1 with add_one(x) = x + 2",
        source="dicta demo",
        note="hard-coded refused AI agent edit proposal",
    )
    concept, purpose = _make_concept(
        "refused-agent-edit-demo",
        "preserve behavior while improving form",
    )

    proposal_qualification = _make_qualification(
        strength=QualificationStrength.ASSERTED,
        basis="agent proposal",
        conditions=("untrusted input",),
        timing="before appraisal",
    )
    behavior_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="add_one contract",
        conditions=("Number",),
        timing="during appraisal",
    )
    disparity_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="checked non-equivalence",
        conditions=("x is Number",),
        timing="during appraisal",
    )
    refusal_qualification = _make_qualification(
        strength=QualificationStrength.CHECKED,
        basis="non-equivalence over Number",
        conditions=("x is Number",),
        timing="demo-time",
    )

    _add_dicta(
        concept,
        [
            _DictumSpec(
                "agent edit",
                "Datum",
                proposal_qualification,
                "agent edit is Datum",
                "agent",
                ("proposal",),
            ),
            _DictumSpec(
                "add_one",
                "accepts Number",
                behavior_qualification,
                "add_one accepts Number",
            ),
            _DictumSpec(
                "add_one",
                "returns Number",
                behavior_qualification,
                "add_one returns Number",
            ),
            _DictumSpec(
                "x + 1",
                "does not equal x + 2 for Number",
                disparity_qualification,
                "x + 1 does not equal x + 2 for Number",
                "equivalence",
                ("add_one", "number"),
            ),
            _DictumSpec(
                "agent edit",
                "changes add_one behavior",
                refusal_qualification,
                "agent edit changes add_one behavior",
                "behavior",
                ("agent", "add_one"),
            ),
            _DictumSpec(
                "agent edit",
                "does not qualify by checked equivalence",
                refusal_qualification,
                "agent edit does not qualify by checked equivalence",
                "agent",
                ("checked_equivalence",),
            ),
        ],
    )

    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description="agent edit violates behavior preservation Purpose",
        severity="refusing",
        kind="behavior_changed",
        tags=("agent", "add_one"),
    )
    inference = Inference(
        from_disparity=disparity,
        derived="refuse agent edit because behavior does not qualify",
        basis="checked equivalence fails for add_one behavior",
    )
    outcome = create_outcome(
        inference=inference,
        result="agent edit refused",
        status="refused",
        kind="agent_refusal",
        tags=("agent", "add_one"),
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            "Concept records refused agent edit",
            "Concept preserves original add_one behavior",
        ],
        note="agent edit refused; preserves original add_one behavior",
        kind="refuse_agent_edit",
        tags=("agent", "add_one"),
    )
    return _make_program("refused-agent-edit-demo", concept, revision)
