from pathlib import Path

import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner

from dicta.cli import app
from dicta.core.appraise import (
    AppraisalResult,
    ArithmeticDatum,
    CounterIncrementDatum,
    FileWriteDatum,
    WorkerFailureDatum,
    appraise_arithmetic_datum,
    appraise_arithmetic_result,
    appraise_counter_revision_datum,
    appraise_counter_revision_result,
    appraise_file_write_datum,
    appraise_file_write_result,
    appraise_structured_datum,
    appraise_structured_program,
    appraise_worker_failure_datum,
    appraise_worker_failure_result,
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


def test_file_write_datum_can_be_constructed() -> None:
    datum = FileWriteDatum(path="report.txt", content="hello")

    assert datum.path == "report.txt"
    assert datum.content == "hello"
    assert datum.statement_text() == 'write report.txt "hello"'


def test_worker_failure_datum_can_be_constructed() -> None:
    datum = WorkerFailureDatum()

    assert datum.worker_name == "worker"
    assert datum.failure == "crash"
    assert datum.known_good_available is True
    assert datum.statement_text() == "worker Outcome is crash"


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


def test_appraise_file_write_result_returns_appraisal_result() -> None:
    result = appraise_file_write_result(
        FileWriteDatum(path="report.txt", content="hello")
    )

    assert isinstance(result, AppraisalResult)


def test_appraise_worker_failure_result_returns_appraisal_result() -> None:
    result = appraise_worker_failure_result(WorkerFailureDatum())

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


def test_file_write_result_is_accepted() -> None:
    result = appraise_file_write_result(
        FileWriteDatum(path="report.txt", content="hello")
    )

    assert result.accepted is True
    assert "accepted" in result.summary


def test_worker_failure_result_is_recovery_accepted() -> None:
    result = appraise_worker_failure_result(WorkerFailureDatum())

    assert result.accepted is True
    assert "accepted" in result.summary


def test_refused_counter_revision_result_is_refused() -> None:
    result = appraise_counter_revision_result(
        CounterIncrementDatum(name="counter", initial="cat")
    )

    assert isinstance(result, AppraisalResult)
    assert result.accepted is False
    assert "refused" in result.summary


def test_refused_file_write_result_is_refused() -> None:
    result = appraise_file_write_result(
        FileWriteDatum(path="protected/report.txt", content="hello")
    )

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


def test_appraise_file_write_datum_returns_program() -> None:
    program = appraise_file_write_datum(
        FileWriteDatum(path="report.txt", content="hello")
    )

    assert isinstance(program, Program)


def test_appraise_worker_failure_datum_returns_program() -> None:
    program = appraise_worker_failure_datum(WorkerFailureDatum())

    assert isinstance(program, Program)


def test_structured_datum_routes_arithmetic_success() -> None:
    result = appraise_structured_datum(
        ArithmeticDatum(left=3, operator="+", right=4)
    )

    assert result.accepted is True
    assert has_dictum_text(result.program, "3 + 4 is 7")


def test_structured_datum_routes_arithmetic_refusal() -> None:
    result = appraise_structured_datum(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )

    assert result.accepted is False
    assert result.disparity is not None
    assert result.disparity.kind == "type_mismatch"


def test_structured_datum_routes_counter_success() -> None:
    result = appraise_structured_datum(
        CounterIncrementDatum(name="counter", initial=0)
    )

    assert result.accepted is True
    assert has_dictum_text(result.program, "counter is 1")


def test_structured_datum_routes_counter_refusal() -> None:
    result = appraise_structured_datum(
        CounterIncrementDatum(name="counter", initial="cat")
    )

    assert result.accepted is False
    assert has_dictum_text(result.program, 'counter is "cat"')


def test_structured_datum_routes_file_write_success() -> None:
    result = appraise_structured_datum(
        FileWriteDatum(path="report.txt", content="hello")
    )

    assert result.accepted is True
    assert has_dictum_text(result.program, 'report.txt contains "hello"')


def test_structured_datum_routes_file_write_refusal() -> None:
    result = appraise_structured_datum(
        FileWriteDatum(path="protected/report.txt", content="hello")
    )

    assert result.accepted is False
    assert result.disparity is not None
    assert result.disparity.description == (
        "write lacks Permission for protected/report.txt"
    )


def test_structured_datum_routes_worker_recovery() -> None:
    result = appraise_structured_datum(WorkerFailureDatum())

    assert result.accepted is True
    assert result.outcome is not None
    assert result.outcome.result == "worker restarted"


def test_structured_datum_rejects_unsupported_objects() -> None:
    with pytest.raises(ValueError, match="unsupported structured Datum"):
        appraise_structured_datum(object())


def test_appraise_structured_program_returns_program() -> None:
    program = appraise_structured_program(
        ArithmeticDatum(left=3, operator="+", right=4)
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


def test_appraised_file_write_contains_disk_change() -> None:
    program = appraise_file_write_datum(
        FileWriteDatum(path="report.txt", content="hello")
    )

    assert has_dictum_text(program, "write changes Disk")


def test_appraised_file_write_contains_permission_qualification() -> None:
    program = appraise_file_write_datum(
        FileWriteDatum(path="report.txt", content="hello")
    )

    assert has_dictum_text(program, "Permission qualifies for report.txt")


def test_appraised_file_write_final_concept_contains_written_content() -> None:
    program = appraise_file_write_datum(
        FileWriteDatum(path="report.txt", content="hello")
    )

    assert has_dictum_text(program, 'report.txt contains "hello"')


def test_appraised_worker_failure_contains_worker_program() -> None:
    program = appraise_worker_failure_datum(WorkerFailureDatum())

    assert has_dictum_text(program, "worker is Program")


def test_appraised_worker_failure_contains_supervisor_requirement() -> None:
    program = appraise_worker_failure_datum(WorkerFailureDatum())

    assert has_dictum_text(program, "supervisor requires worker Alive")


def test_appraised_worker_failure_contains_disparity() -> None:
    result = appraise_worker_failure_result(WorkerFailureDatum())

    assert result.disparity is not None
    assert result.disparity.description == (
        "worker is not Alive under availability Purpose"
    )
    assert result.disparity.kind == "worker_unavailable"


def test_appraised_worker_failure_outcome_records_restart() -> None:
    result = appraise_worker_failure_result(WorkerFailureDatum())

    assert result.outcome is not None
    assert result.outcome.result == "worker restarted"


def test_appraised_worker_failure_revision_records_restart() -> None:
    result = appraise_worker_failure_result(WorkerFailureDatum())

    assert result.revision is not None
    revision_text = " ".join([*result.revision.changes, result.revision.note or ""])
    assert "worker restarted" in revision_text


def test_appraised_worker_failure_final_concept_contains_alive() -> None:
    program = appraise_worker_failure_datum(WorkerFailureDatum())

    assert has_dictum_text(program, "worker is Alive")


def test_appraised_worker_failure_final_concept_removes_not_alive() -> None:
    program = appraise_worker_failure_datum(WorkerFailureDatum())

    assert not any(
        dictum.subject == "worker" and dictum.meaning == "not Alive"
        for dictum in program.concept.dicta
    )


def test_appraised_worker_failure_disparity_snapshot_contains_not_alive() -> None:
    result = appraise_worker_failure_result(WorkerFailureDatum())

    assert result.disparity is not None
    assert any(
        dictum.subject == "worker" and dictum.meaning == "not Alive"
        for dictum in result.disparity.concept.dicta
    )


def test_appraised_refused_file_write_contains_denied_permission() -> None:
    program = appraise_file_write_datum(
        FileWriteDatum(path="protected/report.txt", content="hello")
    )

    assert has_dictum_text(
        program,
        "Permission does not qualify for protected/report.txt",
    )


def test_appraised_refused_file_write_contains_permission_disparity() -> None:
    result = appraise_file_write_result(
        FileWriteDatum(path="protected/report.txt", content="hello")
    )

    assert result.disparity is not None
    assert result.disparity.description == (
        "write lacks Permission for protected/report.txt"
    )
    assert result.disparity.kind == "permission_denied"


def test_appraised_refused_file_write_final_concept_has_no_written_content() -> None:
    program = appraise_file_write_datum(
        FileWriteDatum(path="protected/report.txt", content="hello")
    )

    assert not has_dictum_text(program, 'protected/report.txt contains "hello"')


def test_appraised_refused_file_write_records_disk_unchanged() -> None:
    result = appraise_file_write_result(
        FileWriteDatum(path="protected/report.txt", content="hello")
    )

    assert result.revision is not None
    revision_text = " ".join([*result.revision.changes, result.revision.note or ""])
    assert "Disk unchanged" in revision_text


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


def test_appraise_file_write_cli_renders_expected_visible_text() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["appraise-file-write-demo"])

    assert result.exit_code == 0
    assert 'Datum: write report.txt "hello"' in result.output
    assert "* write changes Disk" in result.output
    assert "* Permission qualifies for report.txt" in result.output
    assert '* report.txt contains "hello"' in result.output
    assert "* write accepted" in result.output


def test_appraise_refused_file_write_cli_renders_expected_visible_text() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["appraise-refused-file-write-demo"])

    assert result.exit_code == 0
    assert 'Datum: write protected/report.txt "hello"' in result.output
    assert "* Permission does not qualify for protected/report.txt" in result.output
    assert "* write lacks Permission for protected/report.txt" in result.output
    assert "* write refused" in result.output


def test_appraise_supervised_worker_cli_renders_expected_visible_text() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["appraise-supervised-worker-demo"])

    assert result.exit_code == 0
    assert "Datum: worker Outcome is crash" in result.output
    assert "* worker is Program" in result.output
    assert "* supervisor requires worker Alive" in result.output
    assert "* worker is not Alive under availability Purpose" in result.output
    assert "* restart worker from known-good Concept" in result.output
    assert "* worker restarted" in result.output
    assert "* Concept restores worker is Alive" in result.output


def test_file_write_appraiser_does_not_create_real_files(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    appraise_file_write_datum(FileWriteDatum(path="report.txt", content="hello"))
    appraise_file_write_datum(
        FileWriteDatum(path="protected/report.txt", content="hello")
    )

    assert not Path("report.txt").exists()
    assert not Path("protected").exists()
