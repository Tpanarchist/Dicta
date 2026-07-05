"""Tiny mechanical appraisers for structured Dicta data."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from dicta.core.models import (
    Concept,
    Disparity,
    Dictum,
    Inference,
    Outcome,
    Program,
    Purpose,
    Revision,
    RevisionOperation,
)
from dicta.core.program import (
    add_dictum,
    append_revision,
    create_outcome,
    create_revision,
    produce_dictum,
    receive_datum,
)
from dicta.core.qualification import asserted, checked


class ArithmeticDatum(BaseModel):
    """Structured arithmetic datum, not source syntax."""

    model_config = ConfigDict(extra="forbid")

    left: int | str
    operator: str
    right: int | str

    def expression_text(self) -> str:
        """Return the visible arithmetic expression."""

        return f"{_operand_text(self.left)} {self.operator} {_operand_text(self.right)}"


class CounterIncrementDatum(BaseModel):
    """Structured counter increment datum, not source syntax."""

    model_config = ConfigDict(extra="forbid")

    name: str
    initial: int | str
    increment: int = 1

    def statement_text(self) -> str:
        """Return the visible counter revision statement."""

        return (
            f"{self.name} = {_operand_text(self.initial)}; "
            f"{self.name} = {self.name} + {self.increment}"
        )


class FileWriteDatum(BaseModel):
    """Structured file write datum, not source syntax or real IO."""

    model_config = ConfigDict(extra="forbid")

    path: str
    content: str

    def statement_text(self) -> str:
        """Return the visible file write statement."""

        return f"write {self.path} {_operand_text(self.content)}"


class WorkerFailureDatum(BaseModel):
    """Structured supervised worker failure datum, not a real process."""

    model_config = ConfigDict(extra="forbid")

    worker_name: str = "worker"
    failure: str = "crash"
    known_good_available: bool = True

    def statement_text(self) -> str:
        """Return the visible worker failure statement."""

        return f"{self.worker_name} Outcome is {self.failure}"


class AppraisalResult(BaseModel):
    """Mechanical appraiser status plus resulting Program."""

    model_config = ConfigDict(extra="forbid")

    datum: object
    program: Program
    accepted: bool
    summary: str
    disparity: Disparity | None = None
    outcome: Outcome | None = None
    revision: Revision | None = None


def _operand_text(value: int | str) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


def classify_value(value: int | str) -> str:
    """Classify a narrow appraiser value."""

    if isinstance(value, int):
        return "Number"
    if isinstance(value, str):
        return "Text"

    msg = "only integer and string values can be classified"
    raise ValueError(msg)


def _value_tag(value: int | str) -> str:
    return classify_value(value).lower()


def _value_condition(value: int | str) -> str:
    if isinstance(value, int):
        return "int operand"
    return "str operand"


def typed_dictum(
    value: int | str,
    *,
    basis: str = "structured appraisal datum",
    tags: tuple[str, ...] = (),
) -> Dictum:
    """Build a typed Dictum for a narrow appraiser value."""

    subject = _operand_text(value)
    meaning = classify_value(value)
    qualification = checked(
        basis=basis,
        conditions=(_value_condition(value),),
        timing="appraisal-time",
    )
    return produce_dictum(
        subject,
        meaning,
        qualification,
        display=f"{subject} is {meaning}",
        kind="type",
        tags=(*tags, _value_tag(value)),
    )


def _appraisal_result(
    *,
    datum: object,
    concept: Concept,
    revision: Revision,
    program_name: str,
    accepted: bool,
    summary: str,
    disparity: Disparity,
    outcome: Outcome,
) -> AppraisalResult:
    program = append_revision(Program(name=program_name, concept=concept), revision)
    return AppraisalResult(
        datum=datum,
        program=program,
        accepted=accepted,
        summary=summary,
        disparity=disparity,
        outcome=outcome,
        revision=revision,
    )


def _accepted_result(
    *,
    datum: object,
    concept: Concept,
    revision: Revision,
    program_name: str,
    summary: str,
    disparity: Disparity,
    outcome: Outcome,
) -> AppraisalResult:
    return _appraisal_result(
        datum=datum,
        concept=concept,
        revision=revision,
        program_name=program_name,
        accepted=True,
        summary=summary,
        disparity=disparity,
        outcome=outcome,
    )


def _refused_result(
    *,
    datum: object,
    concept: Concept,
    revision: Revision,
    program_name: str,
    summary: str,
    disparity: Disparity,
    outcome: Outcome,
) -> AppraisalResult:
    return _appraisal_result(
        datum=datum,
        concept=concept,
        revision=revision,
        program_name=program_name,
        accepted=False,
        summary=summary,
        disparity=disparity,
        outcome=outcome,
    )


def _build_arithmetic_concept() -> tuple[Concept, Purpose]:
    purpose = Purpose(statement="evaluate arithmetic expression", mode="appraisal")
    concept = Concept(name="mechanical-arithmetic-appraisal", purpose=purpose)
    operator_qualification = asserted(
        basis="arithmetic concept",
        conditions=("Number operands",),
        timing="appraisal-time",
    )
    add_dictum(
        concept,
        produce_dictum(
            "+",
            "accepts Number, Number",
            operator_qualification,
            display="+ accepts Number, Number",
            kind="operation",
            tags=("arithmetic",),
        ),
    )
    return concept, purpose


def _add_typed_literal(
    concept: Concept,
    value: int | str,
    *,
    tags: tuple[str, ...],
) -> None:
    add_dictum(
        concept,
        typed_dictum(
            value,
            basis="structured arithmetic datum",
            tags=tags,
        ),
    )


def _find_operator_contract(concept: Concept, operator: str) -> bool:
    return any(
        dictum.subject == operator and dictum.meaning == "accepts Number, Number"
        for dictum in concept.dicta
    )


def _find_number_dictum(concept: Concept, value: int) -> bool:
    return any(
        dictum.subject == str(value) and dictum.meaning == "Number"
        for dictum in concept.dicta
    )


def _remove_dictum(concept: Concept, subject: str, meaning: str) -> None:
    concept.dicta = [
        dictum
        for dictum in concept.dicta
        if not (dictum.subject == subject and dictum.meaning == meaning)
    ]


def _build_file_write_concept(datum: FileWriteDatum) -> tuple[Concept, Purpose]:
    purpose = Purpose(statement="persist text to file", mode="appraisal")
    concept = Concept(name="mechanical-file-write-appraisal", purpose=purpose)
    input_qualification = checked(
        basis="structured file write datum",
        conditions=("demo input",),
        timing="before effect",
    )
    operation_qualification = asserted(
        basis="file write effect contract",
        conditions=("FilePath", "Text"),
        timing="before effect",
    )
    add_dictum(
        concept,
        produce_dictum(
            datum.path,
            "FilePath",
            input_qualification,
            display=f"{datum.path} is FilePath",
            kind="type",
            tags=("file", "path"),
        ),
    )
    add_dictum(
        concept,
        typed_dictum(
            datum.content,
            basis="structured file write datum",
            tags=("file",),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "write",
            "accepts FilePath, Text",
            operation_qualification,
            display="write accepts FilePath, Text",
            kind="operation",
            tags=("file", "write"),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "write",
            "changes Disk",
            operation_qualification,
            display="write changes Disk",
            kind="effect",
            tags=("disk", "write"),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "write",
            "requires Permission",
            operation_qualification,
            display="write requires Permission",
            kind="permission",
            tags=("write",),
        ),
    )
    return concept, purpose


def _appraise_accepted_file_write(
    datum: FileWriteDatum,
    concept: Concept,
    purpose: Purpose,
) -> AppraisalResult:
    permission_qualification = checked(
        basis="demo permission policy",
        conditions=(f"target is {datum.path}",),
        timing="appraisal-time",
    )
    effect_qualification = checked(
        basis="mechanical file write appraisal",
        conditions=(f"Permission qualifies for {datum.path}",),
        timing="after effect",
    )
    add_dictum(
        concept,
        produce_dictum(
            "Permission",
            f"qualifies for {datum.path}",
            permission_qualification,
            display=f"Permission qualifies for {datum.path}",
            kind="permission",
            tags=("write", datum.path),
        ),
    )
    received = receive_datum(
        datum,
        source="dicta appraise-file-write-demo",
        note="structured file write datum",
    )
    disparity = Disparity(
        datum=received,
        concept=concept,
        purpose=purpose,
        description=f"{datum.path} does not yet contain {_operand_text(datum.content)}",
        severity="effect",
        kind="missing_effect",
        tags=("disk", "write"),
    )
    add_dictum(
        concept,
        produce_dictum(
            datum.path,
            f"contains {_operand_text(datum.content)}",
            effect_qualification,
            display=f"{datum.path} contains {_operand_text(datum.content)}",
            kind="effect",
            tags=("disk", datum.path),
        ),
    )
    inference = Inference(
        from_disparity=disparity,
        derived="write may proceed because Permission qualifies",
        basis=f"write requires Permission and Permission qualifies for {datum.path}",
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
            f"Concept records {datum.path} contains {_operand_text(datum.content)}",
            "Concept records Disk changed by write",
        ],
        note="Disk changed by write",
        kind="record_effect",
        tags=("disk", "write"),
    )
    return _accepted_result(
        datum=datum,
        concept=concept,
        revision=revision,
        program_name="mechanical-file-write-appraisal",
        summary="file write accepted",
        disparity=disparity,
        outcome=outcome,
    )


def _appraise_refused_file_write(
    datum: FileWriteDatum,
    concept: Concept,
    purpose: Purpose,
) -> AppraisalResult:
    permission_qualification = checked(
        basis="demo permission policy",
        conditions=(f"target is {datum.path}",),
        timing="appraisal-time",
    )
    add_dictum(
        concept,
        produce_dictum(
            "Permission",
            f"does not qualify for {datum.path}",
            permission_qualification,
            display=f"Permission does not qualify for {datum.path}",
            kind="permission",
            tags=("write", datum.path),
        ),
    )
    received = receive_datum(
        datum,
        source="dicta appraise-refused-file-write-demo",
        note="structured refused file write datum",
    )
    disparity = Disparity(
        datum=received,
        concept=concept,
        purpose=purpose,
        description=f"write lacks Permission for {datum.path}",
        severity="refusing",
        kind="permission_denied",
        tags=("write", datum.path),
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
    return _refused_result(
        datum=datum,
        concept=concept,
        revision=revision,
        program_name="mechanical-refused-file-write-appraisal",
        summary="file write refused",
        disparity=disparity,
        outcome=outcome,
    )


def _appraise_worker_restart(
    datum: WorkerFailureDatum,
    concept: Concept,
    purpose: Purpose,
) -> AppraisalResult:
    restart_qualification = checked(
        basis="known-good worker Concept",
        conditions=(
            f"{datum.worker_name} is Program",
            "known-good worker Concept exists",
        ),
        timing="after restart",
    )
    received = receive_datum(
        datum,
        source="dicta appraise-supervised-worker-demo",
        note="structured worker failure datum",
    )
    disparity = Disparity(
        datum=received,
        concept=concept,
        purpose=purpose,
        description=f"{datum.worker_name} is not Alive under availability Purpose",
        severity="recovering",
        kind="worker_unavailable",
        tags=(datum.worker_name, "supervision"),
    )

    _remove_dictum(concept, datum.worker_name, "not Alive")
    add_dictum(
        concept,
        produce_dictum(
            f"{datum.worker_name} restart",
            "accepted",
            restart_qualification,
            display=f"{datum.worker_name} restart accepted",
            kind="supervision",
            tags=(datum.worker_name, "supervision"),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            datum.worker_name,
            "Alive",
            restart_qualification,
            display=f"{datum.worker_name} is Alive",
            kind="status",
            tags=(datum.worker_name, "supervision"),
        ),
    )

    inference = Inference(
        from_disparity=disparity,
        derived="restart worker from known-good Concept",
        basis=f"supervisor requires {datum.worker_name} Alive",
    )
    outcome = create_outcome(
        inference=inference,
        result="worker restarted",
        status="restarted",
        kind="restart",
        tags=(datum.worker_name, "supervision"),
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
        tags=(datum.worker_name, "supervision"),
    )
    return _accepted_result(
        datum=datum,
        concept=concept,
        revision=revision,
        program_name="mechanical-supervised-worker-appraisal",
        summary="worker restart accepted",
        disparity=disparity,
        outcome=outcome,
    )


def _appraise_refused_counter_revision(
    datum: CounterIncrementDatum,
    concept: Concept,
    purpose: Purpose,
) -> AppraisalResult:
    received = receive_datum(
        datum,
        source="dicta appraise-refused-counter-demo",
        note="structured refused counter revision datum",
    )
    disparity = Disparity(
        datum=received,
        concept=concept,
        purpose=purpose,
        description=f"{datum.name} does not qualify as Number",
        severity="refusing",
        kind="type_mismatch",
        tags=("counter",),
    )
    inference = Inference(
        from_disparity=disparity,
        derived="refuse counter revision because current value does not qualify",
        basis=f"{datum.name} is Text and + accepts Number, Number",
    )
    outcome = create_outcome(
        inference=inference,
        result="counter revision refused",
        status="refused",
        kind="refusal",
        tags=("counter",),
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            "Concept records refused counter revision",
            f"Concept preserves {datum.name} is {_operand_text(datum.initial)}",
        ],
        note=(
            "counter revision refused; "
            f"preserves {datum.name} is {_operand_text(datum.initial)}"
        ),
        kind="preserve_state",
        tags=("counter", "refusal"),
    )
    return _refused_result(
        datum=datum,
        concept=concept,
        revision=revision,
        program_name="mechanical-refused-counter-revision-appraisal",
        summary="counter revision refused",
        disparity=disparity,
        outcome=outcome,
    )


def _appraise_integer_addition(
    datum: ArithmeticDatum,
    concept: Concept,
    purpose: Purpose,
) -> AppraisalResult:
    if not isinstance(datum.left, int) or not isinstance(datum.right, int):
        msg = "integer addition appraisal requires two integer operands"
        raise ValueError(msg)

    expression = datum.expression_text()
    result = datum.left + datum.right
    received = receive_datum(
        datum,
        source="dicta appraise-arithmetic-demo",
        note="structured arithmetic datum",
    )
    disparity = Disparity(
        datum=received,
        concept=concept,
        purpose=purpose,
        description=f"{expression} lacks evaluated result",
        severity="low",
        kind="unevaluated_expression",
        tags=("arithmetic",),
    )

    result_qualification = checked(
        basis="mechanical integer addition",
        conditions=("Number operands", "+ accepts Number, Number"),
        timing="appraisal-time",
    )
    add_dictum(
        concept,
        produce_dictum(
            expression,
            str(result),
            result_qualification,
            display=f"{expression} is {result}",
            kind="value",
            tags=("arithmetic",),
        ),
    )

    inference = Inference(
        from_disparity=disparity,
        derived=f"{expression} evaluates to {result}",
        basis="+ accepts Number, Number and both operands are Number",
    )
    outcome = create_outcome(
        inference=inference,
        result=result,
        status="evaluated",
        kind="value",
        tags=("arithmetic",),
    )
    revision = create_revision(
        outcome=outcome,
        changes=["Concept records evaluated arithmetic dictum"],
        note="result qualifies by mechanical appraisal",
        kind="record_result",
        tags=("arithmetic",),
    )
    return _accepted_result(
        datum=datum,
        concept=concept,
        revision=revision,
        program_name="mechanical-arithmetic-appraisal",
        summary="arithmetic expression accepted",
        disparity=disparity,
        outcome=outcome,
    )


def _appraise_invalid_integer_text_addition(
    datum: ArithmeticDatum,
    concept: Concept,
    purpose: Purpose,
) -> AppraisalResult:
    received = receive_datum(
        datum,
        source="dicta appraise-invalid-arithmetic-demo",
        note="structured invalid arithmetic datum",
    )
    disparity = Disparity(
        datum=received,
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
    return _refused_result(
        datum=datum,
        concept=concept,
        revision=revision,
        program_name="mechanical-invalid-arithmetic-appraisal",
        summary="arithmetic expression refused",
        disparity=disparity,
        outcome=outcome,
    )


def appraise_arithmetic_result(datum: ArithmeticDatum) -> AppraisalResult:
    """Appraise one structured arithmetic datum into a result shape."""

    if datum.operator != "+":
        msg = "only + is supported by the first arithmetic appraiser"
        raise ValueError(msg)
    if not isinstance(datum.left, int):
        msg = "only integer left operands are supported by the first appraiser"
        raise ValueError(msg)

    concept, purpose = _build_arithmetic_concept()
    _add_typed_literal(concept, datum.left, tags=("arithmetic",))

    if isinstance(datum.right, int):
        _add_typed_literal(concept, datum.right, tags=("arithmetic",))
    elif isinstance(datum.right, str):
        _add_typed_literal(concept, datum.right, tags=("arithmetic",))
    else:
        msg = "only integer or string right operands are supported"
        raise ValueError(msg)

    if not _find_number_dictum(concept, datum.left):
        msg = "left operand did not qualify as Number in the arithmetic Concept"
        raise ValueError(msg)
    if not _find_operator_contract(concept, datum.operator):
        msg = "+ operator contract is absent from the arithmetic Concept"
        raise ValueError(msg)

    if isinstance(datum.right, int):
        if not _find_number_dictum(concept, datum.right):
            msg = "right operand did not qualify as Number in the arithmetic Concept"
            raise ValueError(msg)
        return _appraise_integer_addition(datum, concept, purpose)

    return _appraise_invalid_integer_text_addition(datum, concept, purpose)


def appraise_arithmetic_datum(datum: ArithmeticDatum) -> Program:
    """Appraise one structured arithmetic datum into a Dicta Program."""

    return appraise_arithmetic_result(datum).program


def appraise_counter_revision_result(
    datum: CounterIncrementDatum,
) -> AppraisalResult:
    """Appraise one structured counter revision into a result shape."""

    if datum.increment != 1:
        msg = "only increment by 1 is supported by the first counter appraiser"
        raise ValueError(msg)

    purpose = Purpose(statement="revise counter by valid increment", mode="appraisal")
    concept = Concept(name="mechanical-counter-revision-appraisal", purpose=purpose)
    type_qualification = checked(
        basis="counter binding",
        conditions=("structured counter datum",),
        timing="before revision",
    )
    value_qualification = checked(
        basis="counter state",
        conditions=("structured counter datum",),
        timing="before revision",
    )
    operator_qualification = asserted(
        basis="arithmetic concept",
        conditions=("Number operands",),
        timing="during revision",
    )
    revision_qualification = checked(
        basis="mechanical counter increment",
        conditions=(
            f"{datum.name} is Number",
            f"{datum.name} is {_operand_text(datum.initial)}",
        ),
        timing="after revision",
    )
    initial_kind = classify_value(datum.initial)
    initial_tag = _value_tag(datum.initial)
    initial_value = _operand_text(datum.initial)

    add_dictum(
        concept,
        produce_dictum(
            datum.name,
            initial_kind,
            type_qualification,
            display=f"{datum.name} is {initial_kind}",
            kind="type",
            tags=("counter", initial_tag),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            datum.name,
            initial_value,
            value_qualification,
            display=f"{datum.name} is {initial_value}",
            kind="value",
            tags=("counter",),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "+",
            "accepts Number, Number",
            operator_qualification,
            display="+ accepts Number, Number",
            kind="operation",
            tags=("counter", "arithmetic"),
        ),
    )

    if isinstance(datum.initial, str):
        return _appraise_refused_counter_revision(datum, concept, purpose)

    revised_value = datum.initial + datum.increment
    received = receive_datum(
        datum,
        source="dicta appraise-counter-demo",
        note="structured counter revision datum",
    )
    disparity = Disparity(
        datum=received,
        concept=concept,
        purpose=purpose,
        description=f"{datum.name} is {datum.initial} before valid increment",
        severity="revision",
        kind="current_value_revision",
        tags=("counter",),
    )

    _remove_dictum(concept, datum.name, str(datum.initial))
    add_dictum(
        concept,
        produce_dictum(
            f"{datum.name} + {datum.increment}",
            str(revised_value),
            revision_qualification,
            display=f"{datum.name} + {datum.increment} is {revised_value}",
            kind="value",
            tags=("counter", "arithmetic"),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            datum.name,
            str(revised_value),
            revision_qualification,
            display=f"{datum.name} is {revised_value}",
            kind="value",
            tags=("counter",),
        ),
    )

    inference = Inference(
        from_disparity=disparity,
        derived=f"{datum.name} may revise from {datum.initial} to {revised_value}",
        basis=f"{datum.name} is Number and + accepts Number, Number",
    )
    outcome = create_outcome(
        inference=inference,
        result=f"{datum.name} is {revised_value}",
        status="revised",
        kind="value",
        tags=("counter",),
    )
    operation = RevisionOperation(
        operation="replace_dictum",
        subject=datum.name,
        from_meaning=str(datum.initial),
        to_meaning=str(revised_value),
        note=f"{datum.name} current value revised",
    )
    revision = create_revision(
        outcome=outcome,
        changes=[
            f"Concept replaces {datum.name} is {datum.initial} "
            f"with {datum.name} is {revised_value}",
            f"Concept preserves {datum.name} is Number",
        ],
        note=f"{datum.name} is {datum.initial} to {datum.name} is {revised_value}",
        kind="replace_value",
        tags=("counter",),
        operations=(operation,),
    )
    return _accepted_result(
        datum=datum,
        concept=concept,
        revision=revision,
        program_name="mechanical-counter-revision-appraisal",
        summary="counter revision accepted",
        disparity=disparity,
        outcome=outcome,
    )


def appraise_counter_revision_datum(datum: CounterIncrementDatum) -> Program:
    """Appraise one structured counter revision into a Dicta Program."""

    return appraise_counter_revision_result(datum).program


def appraise_file_write_result(datum: FileWriteDatum) -> AppraisalResult:
    """Appraise one structured file write datum into a result shape."""

    concept, purpose = _build_file_write_concept(datum)
    if datum.path == "report.txt":
        return _appraise_accepted_file_write(datum, concept, purpose)
    if datum.path == "protected/report.txt":
        return _appraise_refused_file_write(datum, concept, purpose)

    msg = "only report.txt and protected/report.txt are supported by this appraiser"
    raise ValueError(msg)


def appraise_file_write_datum(datum: FileWriteDatum) -> Program:
    """Appraise one structured file write datum into a Dicta Program."""

    return appraise_file_write_result(datum).program


def appraise_worker_failure_result(datum: WorkerFailureDatum) -> AppraisalResult:
    """Appraise one structured worker failure into a result shape."""

    if not datum.known_good_available:
        msg = "worker failure without known-good Concept is not implemented yet"
        raise ValueError(msg)

    purpose = Purpose(statement="keep worker available", mode="appraisal")
    concept = Concept(name="mechanical-supervised-worker-appraisal", purpose=purpose)
    worker_qualification = checked(
        basis="supervisor concept",
        conditions=("structured worker datum",),
        timing="before crash",
    )
    supervision_qualification = asserted(
        basis="availability purpose",
        conditions=(datum.worker_name,),
        timing="before crash",
    )
    failure_qualification = checked(
        basis="observed child outcome",
        conditions=(f"{datum.worker_name} Outcome",),
        timing="after crash",
    )
    add_dictum(
        concept,
        produce_dictum(
            datum.worker_name,
            "Program",
            worker_qualification,
            display=f"{datum.worker_name} is Program",
            kind="type",
            tags=(datum.worker_name, "program"),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            datum.worker_name,
            "Alive",
            worker_qualification,
            display=f"{datum.worker_name} is Alive",
            kind="status",
            tags=(datum.worker_name, "supervision"),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            datum.worker_name,
            "serves background task",
            worker_qualification,
            display=f"{datum.worker_name} serves background task",
            kind="behavior",
            tags=(datum.worker_name, "supervision"),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            "supervisor",
            f"requires {datum.worker_name} Alive",
            supervision_qualification,
            display=f"supervisor requires {datum.worker_name} Alive",
            kind="supervision",
            tags=("supervisor", datum.worker_name),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            f"{datum.worker_name} Outcome",
            datum.failure,
            failure_qualification,
            display=f"{datum.worker_name} Outcome is {datum.failure}",
            kind="status",
            tags=(datum.worker_name, "failure"),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            datum.worker_name,
            "not Alive",
            failure_qualification,
            display=f"{datum.worker_name} is not Alive",
            kind="status",
            tags=(datum.worker_name, "failure"),
        ),
    )
    add_dictum(
        concept,
        produce_dictum(
            f"known-good {datum.worker_name} Concept",
            "exists",
            supervision_qualification,
            display=f"known-good {datum.worker_name} Concept exists",
            kind="supervision",
            tags=(datum.worker_name, "supervision"),
        ),
    )
    return _appraise_worker_restart(datum, concept, purpose)


def appraise_worker_failure_datum(datum: WorkerFailureDatum) -> Program:
    """Appraise one structured worker failure into a Dicta Program."""

    return appraise_worker_failure_result(datum).program


def appraise_structured_datum(datum: object) -> AppraisalResult:
    """Route one supported structured Datum to its mechanical appraiser."""

    if isinstance(datum, ArithmeticDatum):
        return appraise_arithmetic_result(datum)
    if isinstance(datum, CounterIncrementDatum):
        return appraise_counter_revision_result(datum)
    if isinstance(datum, FileWriteDatum):
        return appraise_file_write_result(datum)
    if isinstance(datum, WorkerFailureDatum):
        return appraise_worker_failure_result(datum)

    msg = f"unsupported structured Datum: {type(datum).__name__}"
    raise ValueError(msg)


def appraise_structured_program(datum: object) -> Program:
    """Route one supported structured Datum and return its Program."""

    return appraise_structured_datum(datum).program
