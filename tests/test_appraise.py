from typer.testing import CliRunner

from dicta.cli import app
from dicta.core.appraise import (
    AppraisalResult,
    ArithmeticDatum,
    appraise_arithmetic_datum,
    appraise_arithmetic_result,
)
from dicta.core.models import Program
from dicta.core.query import has_dictum_meaning, has_dictum_text
from dicta.core.qualification import QualificationStrength


def test_arithmetic_datum_can_be_constructed() -> None:
    datum = ArithmeticDatum(left=3, operator="+", right=4)

    assert datum.left == 3
    assert datum.operator == "+"
    assert datum.right == 4
    assert datum.expression_text() == "3 + 4"


def test_invalid_arithmetic_datum_can_be_constructed() -> None:
    datum = ArithmeticDatum(left=3, operator="+", right="cat")

    assert datum.left == 3
    assert datum.operator == "+"
    assert datum.right == "cat"
    assert datum.expression_text() == '3 + "cat"'


def test_appraise_arithmetic_datum_returns_program() -> None:
    program = appraise_arithmetic_datum(ArithmeticDatum(left=3, operator="+", right=4))

    assert isinstance(program, Program)


def test_appraise_arithmetic_result_returns_appraisal_result() -> None:
    result = appraise_arithmetic_result(ArithmeticDatum(left=3, operator="+", right=4))

    assert isinstance(result, AppraisalResult)


def test_valid_arithmetic_result_is_accepted() -> None:
    result = appraise_arithmetic_result(ArithmeticDatum(left=3, operator="+", right=4))

    assert result.accepted is True
    assert "accepted" in result.summary


def test_valid_arithmetic_result_contains_program_with_visible_result() -> None:
    result = appraise_arithmetic_result(ArithmeticDatum(left=3, operator="+", right=4))

    assert has_dictum_text(result.program, "3 + 4 is 7")
    assert result.outcome is not None
    assert result.revision is not None


def test_appraise_invalid_arithmetic_datum_returns_program() -> None:
    program = appraise_arithmetic_datum(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )

    assert isinstance(program, Program)


def test_invalid_arithmetic_result_is_refused() -> None:
    result = appraise_arithmetic_result(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )

    assert result.accepted is False
    assert "refused" in result.summary


def test_invalid_arithmetic_result_contains_type_mismatch_program() -> None:
    result = appraise_arithmetic_result(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )

    assert result.disparity is not None
    assert result.disparity.kind == "type_mismatch"
    assert result.disparity.description == "+ does not qualify for Number, Text"
    assert result.program.history[-1].outcome.result == "evaluation refused"


def test_appraised_arithmetic_program_contains_visible_result() -> None:
    program = appraise_arithmetic_datum(ArithmeticDatum(left=3, operator="+", right=4))

    assert has_dictum_text(program, "3 + 4 is 7")


def test_appraised_arithmetic_program_contains_result_meaning() -> None:
    program = appraise_arithmetic_datum(ArithmeticDatum(left=3, operator="+", right=4))

    assert has_dictum_meaning(program, "7")


def test_appraised_arithmetic_result_has_checked_qualification() -> None:
    program = appraise_arithmetic_datum(ArithmeticDatum(left=3, operator="+", right=4))
    result_dictum = next(
        dictum
        for dictum in program.concept.dicta
        if dictum.subject == "3 + 4" and dictum.meaning == "7"
    )

    assert result_dictum.qualification.strength == QualificationStrength.CHECKED
    assert result_dictum.qualification.basis == "mechanical integer addition"


def test_appraised_arithmetic_program_history_contains_revision() -> None:
    program = appraise_arithmetic_datum(ArithmeticDatum(left=3, operator="+", right=4))

    assert len(program.history) >= 1


def test_appraised_arithmetic_revision_updates_final_concept() -> None:
    program = appraise_arithmetic_datum(ArithmeticDatum(left=3, operator="+", right=4))

    assert any(
        dictum.subject == "3 + 4" and dictum.meaning == "7"
        for dictum in program.concept.dicta
    )


def test_appraised_invalid_arithmetic_contains_text_operand() -> None:
    program = appraise_arithmetic_datum(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )

    assert has_dictum_text(program, '"cat" is Text')


def test_appraised_invalid_arithmetic_contains_operator_contract() -> None:
    program = appraise_arithmetic_datum(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )

    assert has_dictum_text(program, "+ accepts Number, Number")


def test_appraised_invalid_arithmetic_contains_type_disparity() -> None:
    program = appraise_arithmetic_datum(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )
    disparity = program.history[-1].outcome.inference.from_disparity

    assert disparity.description == "+ does not qualify for Number, Text"
    assert disparity.kind == "type_mismatch"


def test_appraised_invalid_arithmetic_outcome_is_refusal() -> None:
    program = appraise_arithmetic_datum(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )
    outcome = program.history[-1].outcome

    assert outcome.result == "evaluation refused"
    assert outcome.status == "refused"


def test_appraised_invalid_arithmetic_revision_records_disparity() -> None:
    program = appraise_arithmetic_datum(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )
    revision = program.history[-1]

    assert revision.changes == ["Concept records invalid operand disparity"]


def test_appraised_invalid_arithmetic_has_no_success_result_dictum() -> None:
    program = appraise_arithmetic_datum(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )

    assert not any(
        dictum.subject == '3 + "cat"'
        for dictum in program.concept.dicta
    )


def test_appraise_arithmetic_cli_renders_expected_visible_text() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["appraise-arithmetic-demo"])

    assert result.exit_code == 0
    assert "Datum: 3 + 4" in result.output
    assert "* 3 + 4 is 7" in result.output
    assert "* 3 + 4 evaluates to 7" in result.output
    assert "arithmetic expression accepted" not in result.output


def test_appraise_invalid_arithmetic_cli_renders_expected_visible_text() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["appraise-invalid-arithmetic-demo"])

    assert result.exit_code == 0
    assert 'Datum: 3 + "cat"' in result.output
    assert '* "cat" is Text' in result.output
    assert "* + does not qualify for Number, Text" in result.output
    assert "* evaluation refused" in result.output
    assert "arithmetic expression refused" not in result.output
