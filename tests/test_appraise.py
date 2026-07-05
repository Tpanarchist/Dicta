from typer.testing import CliRunner

from dicta.cli import app
from dicta.core.appraise import (
    AppraisalResult,
    ArithmeticDatum,
    CounterIncrementDatum,
    appraise_arithmetic_datum,
    appraise_arithmetic_result,
    appraise_counter_revision_datum,
    appraise_counter_revision_result,
    classify_value,
    typed_dictum,
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


def test_counter_increment_datum_can_be_constructed() -> None:
    datum = CounterIncrementDatum(name="counter", initial=0)

    assert datum.name == "counter"
    assert datum.initial == 0
    assert datum.increment == 1
    assert datum.statement_text() == "counter = 0; counter = counter + 1"


def test_refused_counter_increment_datum_can_be_constructed() -> None:
    datum = CounterIncrementDatum(name="counter", initial="cat")

    assert datum.name == "counter"
    assert datum.initial == "cat"
    assert datum.increment == 1
    assert datum.statement_text() == 'counter = "cat"; counter = counter + 1'


def test_classify_value_identifies_number() -> None:
    assert classify_value(3) == "Number"


def test_classify_value_identifies_text() -> None:
    assert classify_value("cat") == "Text"


def test_typed_dictum_renders_number_visible_text() -> None:
    dictum = typed_dictum(3, tags=("arithmetic",))

    assert dictum.subject == "3"
    assert dictum.meaning == "Number"
    assert dictum.visible_text() == "3 is Number"


def test_appraise_arithmetic_datum_returns_program() -> None:
    program = appraise_arithmetic_datum(ArithmeticDatum(left=3, operator="+", right=4))

    assert isinstance(program, Program)


def test_appraise_arithmetic_result_returns_appraisal_result() -> None:
    result = appraise_arithmetic_result(ArithmeticDatum(left=3, operator="+", right=4))

    assert isinstance(result, AppraisalResult)


def test_appraise_counter_revision_result_returns_appraisal_result() -> None:
    result = appraise_counter_revision_result(
        CounterIncrementDatum(name="counter", initial=0)
    )

    assert isinstance(result, AppraisalResult)


def test_valid_arithmetic_result_is_accepted() -> None:
    result = appraise_arithmetic_result(ArithmeticDatum(left=3, operator="+", right=4))

    assert result.accepted is True
    assert "accepted" in result.summary


def test_counter_revision_result_is_accepted() -> None:
    result = appraise_counter_revision_result(
        CounterIncrementDatum(name="counter", initial=0)
    )

    assert result.accepted is True
    assert "accepted" in result.summary


def test_refused_counter_revision_result_is_refused() -> None:
    result = appraise_counter_revision_result(
        CounterIncrementDatum(name="counter", initial="cat")
    )

    assert isinstance(result, AppraisalResult)
    assert result.accepted is False
    assert "refused" in result.summary


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


def test_appraise_counter_revision_datum_returns_program() -> None:
    program = appraise_counter_revision_datum(
        CounterIncrementDatum(name="counter", initial=0)
    )

    assert isinstance(program, Program)


def test_appraise_refused_counter_revision_datum_returns_program() -> None:
    program = appraise_counter_revision_datum(
        CounterIncrementDatum(name="counter", initial="cat")
    )

    assert isinstance(program, Program)


def test_appraised_arithmetic_program_contains_visible_result() -> None:
    program = appraise_arithmetic_datum(ArithmeticDatum(left=3, operator="+", right=4))

    assert has_dictum_text(program, "3 + 4 is 7")


def test_appraised_arithmetic_program_contains_result_meaning() -> None:
    program = appraise_arithmetic_datum(ArithmeticDatum(left=3, operator="+", right=4))

    assert has_dictum_meaning(program, "7")


def test_appraised_counter_final_concept_contains_new_value() -> None:
    program = appraise_counter_revision_datum(
        CounterIncrementDatum(name="counter", initial=0)
    )

    assert has_dictum_text(program, "counter is 1")


def test_appraised_counter_final_concept_preserves_type() -> None:
    program = appraise_counter_revision_datum(
        CounterIncrementDatum(name="counter", initial=0)
    )

    assert has_dictum_text(program, "counter is Number")


def test_appraised_counter_final_concept_removes_old_current_value() -> None:
    program = appraise_counter_revision_datum(
        CounterIncrementDatum(name="counter", initial=0)
    )

    assert not any(
        dictum.subject == "counter" and dictum.meaning == "0"
        for dictum in program.concept.dicta
    )


def test_appraised_refused_counter_preserves_text_type() -> None:
    program = appraise_counter_revision_datum(
        CounterIncrementDatum(name="counter", initial="cat")
    )

    assert has_dictum_text(program, "counter is Text")


def test_appraised_refused_counter_preserves_text_value() -> None:
    program = appraise_counter_revision_datum(
        CounterIncrementDatum(name="counter", initial="cat")
    )

    assert has_dictum_text(program, 'counter is "cat"')


def test_appraised_refused_counter_contains_number_disparity() -> None:
    result = appraise_counter_revision_result(
        CounterIncrementDatum(name="counter", initial="cat")
    )

    assert result.disparity is not None
    assert result.disparity.description == "counter does not qualify as Number"
    assert result.disparity.kind == "type_mismatch"


def test_appraised_refused_counter_outcome_is_refusal() -> None:
    result = appraise_counter_revision_result(
        CounterIncrementDatum(name="counter", initial="cat")
    )

    assert result.outcome is not None
    assert result.outcome.result == "counter revision refused"
    assert result.outcome.status == "refused"


def test_appraised_refused_counter_final_concept_has_no_numeric_result() -> None:
    program = appraise_counter_revision_datum(
        CounterIncrementDatum(name="counter", initial="cat")
    )

    assert not has_dictum_text(program, "counter is 1")


def test_appraised_refused_counter_revision_records_preservation() -> None:
    result = appraise_counter_revision_result(
        CounterIncrementDatum(name="counter", initial="cat")
    )

    assert result.revision is not None
    assert result.revision.changes == [
        "Concept records refused counter revision",
        'Concept preserves counter is "cat"',
    ]


def test_appraised_counter_disparity_snapshot_contains_old_value() -> None:
    result = appraise_counter_revision_result(
        CounterIncrementDatum(name="counter", initial=0)
    )

    assert result.disparity is not None
    assert any(
        dictum.subject == "counter" and dictum.meaning == "0"
        for dictum in result.disparity.concept.dicta
    )


def test_appraised_counter_revision_has_replace_operation() -> None:
    result = appraise_counter_revision_result(
        CounterIncrementDatum(name="counter", initial=0)
    )

    assert result.revision is not None
    assert len(result.revision.operations) == 1
    operation = result.revision.operations[0]
    assert operation.operation == "replace_dictum"
    assert operation.subject == "counter"
    assert operation.from_meaning == "0"
    assert operation.to_meaning == "1"


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


def test_appraise_counter_cli_renders_expected_visible_text() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["appraise-counter-demo"])

    assert result.exit_code == 0
    assert "Datum: counter = 0; counter = counter + 1" in result.output
    assert "* counter is Number" in result.output
    assert "* counter is 1" in result.output
    assert "* counter may revise from 0 to 1" in result.output
    assert "* Concept replaces counter is 0 with counter is 1" in result.output


def test_appraise_refused_counter_cli_renders_expected_visible_text() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["appraise-refused-counter-demo"])

    assert result.exit_code == 0
    assert 'Datum: counter = "cat"; counter = counter + 1' in result.output
    assert "* counter is Text" in result.output
    assert '* counter is "cat"' in result.output
    assert "* counter does not qualify as Number" in result.output
    assert "* counter revision refused" in result.output
