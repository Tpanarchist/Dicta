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
