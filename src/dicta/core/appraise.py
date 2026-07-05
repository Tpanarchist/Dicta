"""Tiny mechanical appraisers for structured Dicta data."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from dicta.core.models import (
    Concept,
    Disparity,
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


def _number_dictum(value: int) -> tuple[str, str, str]:
    text = str(value)
    return text, "Number", f"{text} is Number"


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


def _add_number_literal(concept: Concept, value: int) -> None:
    subject, meaning, display = _number_dictum(value)
    literal_qualification = checked(
        basis="structured arithmetic datum",
        conditions=("int operand",),
        timing="appraisal-time",
    )
    add_dictum(
        concept,
        produce_dictum(
            subject,
            meaning,
            literal_qualification,
            display=display,
            kind="type",
            tags=("arithmetic", "number"),
        ),
    )


def _add_text_literal(concept: Concept, value: str) -> None:
    subject = _operand_text(value)
    literal_qualification = checked(
        basis="structured arithmetic datum",
        conditions=("str operand",),
        timing="appraisal-time",
    )
    add_dictum(
        concept,
        produce_dictum(
            subject,
            "Text",
            literal_qualification,
            display=f"{subject} is Text",
            kind="type",
            tags=("arithmetic", "text"),
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
    program = append_revision(
        Program(name="mechanical-refused-counter-revision-appraisal", concept=concept),
        revision,
    )
    return AppraisalResult(
        datum=datum,
        program=program,
        accepted=False,
        summary="counter revision refused",
        disparity=disparity,
        outcome=outcome,
        revision=revision,
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
    program = append_revision(
        Program(name="mechanical-arithmetic-appraisal", concept=concept),
        revision,
    )
    return AppraisalResult(
        datum=datum,
        program=program,
        accepted=True,
        summary="arithmetic expression accepted",
        disparity=disparity,
        outcome=outcome,
        revision=revision,
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
    program = append_revision(
        Program(name="mechanical-invalid-arithmetic-appraisal", concept=concept),
        revision,
    )
    return AppraisalResult(
        datum=datum,
        program=program,
        accepted=False,
        summary="arithmetic expression refused",
        disparity=disparity,
        outcome=outcome,
        revision=revision,
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
    _add_number_literal(concept, datum.left)

    if isinstance(datum.right, int):
        _add_number_literal(concept, datum.right)
    elif isinstance(datum.right, str):
        _add_text_literal(concept, datum.right)
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
    initial_kind = "Number" if isinstance(datum.initial, int) else "Text"
    initial_tag = "number" if isinstance(datum.initial, int) else "text"
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
    program = append_revision(
        Program(name="mechanical-counter-revision-appraisal", concept=concept),
        revision,
    )
    return AppraisalResult(
        datum=datum,
        program=program,
        accepted=True,
        summary="counter revision accepted",
        disparity=disparity,
        outcome=outcome,
        revision=revision,
    )


def appraise_counter_revision_datum(datum: CounterIncrementDatum) -> Program:
    """Appraise one structured counter revision into a Dicta Program."""

    return appraise_counter_revision_result(datum).program
