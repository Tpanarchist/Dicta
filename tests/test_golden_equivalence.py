from dicta.core.appraise import (
    ArithmeticDatum,
    CounterIncrementDatum,
    FileWriteDatum,
    WorkerFailureDatum,
    appraise_arithmetic_datum,
    appraise_counter_revision_datum,
    appraise_file_write_datum,
    appraise_worker_failure_datum,
)
from dicta.core.models import Program
from dicta.core.program import (
    build_arithmetic_demo_program,
    build_counter_revision_demo_program,
    build_file_write_demo_program,
    build_invalid_arithmetic_demo_program,
    build_refused_file_write_demo_program,
    build_supervised_worker_demo_program,
)


def visible_dicta(program: Program) -> set[str]:
    return {dictum.visible_text() for dictum in program.concept.dicta}


def disparity_descriptions(program: Program) -> set[str]:
    return {
        revision.outcome.inference.from_disparity.description
        for revision in program.history
    }


def outcome_results(program: Program) -> set[str]:
    return {str(revision.outcome.result) for revision in program.history}


def revision_notes_or_changes(program: Program) -> set[str]:
    notes_or_changes: set[str] = set()
    for revision in program.history:
        notes_or_changes.update(revision.changes)
        if revision.note is not None:
            notes_or_changes.add(revision.note)
    return notes_or_changes


def _assert_visible_commitments(
    fixture: Program,
    mechanical: Program,
    expected: set[str],
) -> None:
    assert expected <= visible_dicta(fixture)
    assert expected <= visible_dicta(mechanical)


def _assert_disparity_commitments(
    fixture: Program,
    mechanical: Program,
    expected: set[str],
) -> None:
    assert expected <= disparity_descriptions(fixture)
    assert expected <= disparity_descriptions(mechanical)


def _assert_outcome_commitments(
    fixture: Program,
    mechanical: Program,
    expected: set[str],
) -> None:
    assert expected <= outcome_results(fixture)
    assert expected <= outcome_results(mechanical)


def _assert_revision_commitments(
    fixture: Program,
    mechanical: Program,
    expected: set[str],
) -> None:
    assert expected <= revision_notes_or_changes(fixture)
    assert expected <= revision_notes_or_changes(mechanical)


def test_arithmetic_success_appraiser_preserves_fixture_commitments() -> None:
    fixture = build_arithmetic_demo_program()
    mechanical = appraise_arithmetic_datum(
        ArithmeticDatum(left=3, operator="+", right=4)
    )

    _assert_visible_commitments(
        fixture,
        mechanical,
        {"3 is Number", "4 is Number", "+ accepts Number, Number", "3 + 4 is 7"},
    )
    _assert_outcome_commitments(fixture, mechanical, {"7"})
    assert "Concept records evaluated arithmetic dictum" in revision_notes_or_changes(
        mechanical
    )
    assert "concept records evaluated arithmetic dictum" in {
        text.casefold() for text in revision_notes_or_changes(fixture)
    }


def test_invalid_arithmetic_appraiser_preserves_fixture_commitments() -> None:
    fixture = build_invalid_arithmetic_demo_program()
    mechanical = appraise_arithmetic_datum(
        ArithmeticDatum(left=3, operator="+", right="cat")
    )

    _assert_visible_commitments(
        fixture,
        mechanical,
        {"3 is Number", '"cat" is Text', "+ accepts Number, Number"},
    )
    _assert_disparity_commitments(
        fixture,
        mechanical,
        {"+ does not qualify for Number, Text"},
    )
    _assert_outcome_commitments(fixture, mechanical, {"evaluation refused"})
    _assert_revision_commitments(
        fixture,
        mechanical,
        {"Concept records invalid operand disparity"},
    )


def test_counter_revision_appraiser_preserves_fixture_commitments() -> None:
    fixture = build_counter_revision_demo_program()
    mechanical = appraise_counter_revision_datum(
        CounterIncrementDatum(name="counter", initial=0)
    )

    _assert_visible_commitments(
        fixture,
        mechanical,
        {"counter is Number", "counter is 1"},
    )
    assert "counter is 0" not in visible_dicta(fixture)
    assert "counter is 0" not in visible_dicta(mechanical)
    _assert_revision_commitments(
        fixture,
        mechanical,
        {
            "Concept replaces counter is 0 with counter is 1",
            "Concept preserves counter is Number",
        },
    )
    assert any(
        operation.operation == "replace_dictum"
        and operation.subject == "counter"
        and operation.from_meaning == "0"
        and operation.to_meaning == "1"
        for revision in mechanical.history
        for operation in revision.operations
    )


def test_file_write_appraiser_preserves_fixture_commitments() -> None:
    fixture = build_file_write_demo_program()
    mechanical = appraise_file_write_datum(
        FileWriteDatum(path="report.txt", content="hello")
    )

    _assert_visible_commitments(
        fixture,
        mechanical,
        {
            "report.txt is FilePath",
            '"hello" is Text',
            "write accepts FilePath, Text",
            "write changes Disk",
            "write requires Permission",
            "Permission qualifies for report.txt",
            'report.txt contains "hello"',
        },
    )
    _assert_outcome_commitments(fixture, mechanical, {"write accepted"})
    _assert_revision_commitments(
        fixture,
        mechanical,
        {"Concept records Disk changed by write"},
    )


def test_refused_file_write_appraiser_preserves_fixture_commitments() -> None:
    fixture = build_refused_file_write_demo_program()
    mechanical = appraise_file_write_datum(
        FileWriteDatum(path="protected/report.txt", content="hello")
    )

    _assert_visible_commitments(
        fixture,
        mechanical,
        {
            "protected/report.txt is FilePath",
            '"hello" is Text',
            "write accepts FilePath, Text",
            "write changes Disk",
            "write requires Permission",
            "Permission does not qualify for protected/report.txt",
        },
    )
    _assert_disparity_commitments(
        fixture,
        mechanical,
        {"write lacks Permission for protected/report.txt"},
    )
    _assert_outcome_commitments(fixture, mechanical, {"write refused"})
    _assert_revision_commitments(
        fixture,
        mechanical,
        {"Concept preserves Disk unchanged"},
    )
    assert 'protected/report.txt contains "hello"' not in visible_dicta(fixture)
    assert 'protected/report.txt contains "hello"' not in visible_dicta(mechanical)


def test_supervised_worker_appraiser_preserves_fixture_commitments() -> None:
    fixture = build_supervised_worker_demo_program()
    mechanical = appraise_worker_failure_datum(WorkerFailureDatum())

    _assert_visible_commitments(
        fixture,
        mechanical,
        {
            "worker is Program",
            "worker serves background task",
            "supervisor requires worker Alive",
            "worker Outcome is crash",
            "known-good worker Concept exists",
            "worker restart accepted",
            "worker is Alive",
        },
    )
    assert "worker is not Alive" not in visible_dicta(mechanical)
    _assert_disparity_commitments(
        fixture,
        mechanical,
        {"worker is not Alive under availability Purpose"},
    )
    _assert_outcome_commitments(fixture, mechanical, {"worker restarted"})
    _assert_revision_commitments(
        fixture,
        mechanical,
        {"Concept restores worker is Alive"},
    )
