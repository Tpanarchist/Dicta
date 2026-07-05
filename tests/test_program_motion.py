from dicta.core.models import Program
from dicta.core.program import (
    build_agent_edit_demo_program,
    build_arithmetic_demo_program,
    build_counter_revision_demo_program,
    build_file_write_demo_program,
    build_invalid_arithmetic_demo_program,
    build_refused_agent_edit_demo_program,
    build_refused_file_write_demo_program,
    build_supervised_worker_demo_program,
)


def test_hard_coded_arithmetic_demo_produces_program() -> None:
    program = build_arithmetic_demo_program()

    assert isinstance(program, Program)


def test_program_history_contains_revision() -> None:
    program = build_arithmetic_demo_program()

    assert len(program.history) >= 1


def test_resulting_concept_contains_evaluated_arithmetic_dictum() -> None:
    program = build_arithmetic_demo_program()

    assert any(
        dictum.subject == "3 + 4" and dictum.meaning == "7"
        for dictum in program.concept.dicta
    )


def test_demo_represents_full_semantic_chain() -> None:
    program = build_arithmetic_demo_program()
    revision = program.history[-1]
    outcome = revision.outcome
    inference = outcome.inference
    disparity = inference.from_disparity

    assert disparity.datum.value == "3 + 4"
    assert inference.derived == "3 + 4 is 7"
    assert outcome.result == 7
    assert revision.changes == ["concept records evaluated arithmetic dictum"]


def test_invalid_arithmetic_demo_contains_relevant_dicta() -> None:
    program = build_invalid_arithmetic_demo_program()
    displayed_dicta = {
        dictum.metadata["display"]
        for dictum in program.concept.dicta
        if "display" in dictum.metadata
    }

    assert displayed_dicta == {
        "3 is Number",
        '"cat" is Text',
        "+ accepts Number, Number",
    }


def test_invalid_arithmetic_demo_represents_disparity_chain() -> None:
    program = build_invalid_arithmetic_demo_program()
    revision = program.history[-1]
    outcome = revision.outcome
    inference = outcome.inference
    disparity = inference.from_disparity

    assert disparity.datum.value == '3 + "cat"'
    assert disparity.purpose.statement == "evaluate arithmetic expression"
    assert disparity.description == "+ does not qualify for Number, Text"
    assert inference.derived == "reject expression as invalid arithmetic"
    assert outcome.result == "evaluation refused"
    assert outcome.status == "refused"
    assert revision.changes == ["Concept records invalid operand disparity"]


def test_counter_revision_demo_produces_program() -> None:
    program = build_counter_revision_demo_program()

    assert isinstance(program, Program)


def test_counter_revision_demo_history_contains_revision() -> None:
    program = build_counter_revision_demo_program()

    assert len(program.history) >= 1


def test_counter_revision_demo_concept_contains_final_counter_value() -> None:
    program = build_counter_revision_demo_program()

    assert any(
        dictum.subject == "counter" and dictum.meaning == "1"
        for dictum in program.concept.dicta
    )


def test_counter_revision_demo_preserves_counter_type() -> None:
    program = build_counter_revision_demo_program()

    assert any(
        dictum.subject == "counter" and dictum.meaning == "Number"
        for dictum in program.concept.dicta
    )


def test_counter_revision_demo_records_replacement_meaning() -> None:
    program = build_counter_revision_demo_program()
    revision = program.history[-1]

    revision_text = " ".join([*revision.changes, revision.note or ""])

    assert "counter is 0" in revision_text
    assert "counter is 1" in revision_text
    assert "Concept replaces counter is 0 with counter is 1" in revision.changes
    assert "Concept preserves counter is Number" in revision.changes


def test_file_write_demo_produces_program() -> None:
    program = build_file_write_demo_program()

    assert isinstance(program, Program)


def test_file_write_demo_history_contains_revision() -> None:
    program = build_file_write_demo_program()

    assert len(program.history) >= 1


def test_file_write_demo_concept_contains_disk_change_dictum() -> None:
    program = build_file_write_demo_program()

    assert any(
        dictum.subject == "write" and dictum.meaning == "changes Disk"
        for dictum in program.concept.dicta
    )


def test_file_write_demo_concept_contains_permission_requirement() -> None:
    program = build_file_write_demo_program()

    assert any(
        dictum.subject == "write" and dictum.meaning == "requires Permission"
        for dictum in program.concept.dicta
    )


def test_file_write_demo_concept_contains_permission_qualification() -> None:
    program = build_file_write_demo_program()

    assert any(
        dictum.subject == "Permission"
        and dictum.meaning == "qualifies for report.txt"
        for dictum in program.concept.dicta
    )


def test_file_write_demo_concept_contains_written_content() -> None:
    program = build_file_write_demo_program()

    assert any(
        dictum.subject == "report.txt" and dictum.meaning == 'contains "hello"'
        for dictum in program.concept.dicta
    )


def test_file_write_demo_revision_notes_disk_changed_by_write() -> None:
    program = build_file_write_demo_program()
    revision = program.history[-1]

    revision_text = " ".join([*revision.changes, revision.note or ""])

    assert "Disk changed by write" in revision_text


def test_refused_file_write_demo_produces_program() -> None:
    program = build_refused_file_write_demo_program()

    assert isinstance(program, Program)


def test_refused_file_write_demo_history_contains_revision() -> None:
    program = build_refused_file_write_demo_program()

    assert len(program.history) >= 1


def test_refused_file_write_demo_concept_contains_disk_change_dictum() -> None:
    program = build_refused_file_write_demo_program()

    assert any(
        dictum.subject == "write" and dictum.meaning == "changes Disk"
        for dictum in program.concept.dicta
    )


def test_refused_file_write_demo_concept_contains_permission_requirement() -> None:
    program = build_refused_file_write_demo_program()

    assert any(
        dictum.subject == "write" and dictum.meaning == "requires Permission"
        for dictum in program.concept.dicta
    )


def test_refused_file_write_demo_concept_contains_denied_permission() -> None:
    program = build_refused_file_write_demo_program()

    assert any(
        dictum.subject == "Permission"
        and dictum.meaning == "does not qualify for protected/report.txt"
        for dictum in program.concept.dicta
    )


def test_refused_file_write_demo_revision_mentions_denied_write_attempt() -> None:
    program = build_refused_file_write_demo_program()
    revision = program.history[-1]

    revision_text = " ".join([*revision.changes, revision.note or ""])

    assert "denied write attempt" in revision_text


def test_refused_file_write_demo_revision_mentions_disk_unchanged() -> None:
    program = build_refused_file_write_demo_program()
    revision = program.history[-1]

    revision_text = " ".join([*revision.changes, revision.note or ""])

    assert "Disk unchanged" in revision_text


def test_refused_file_write_demo_disparity_mentions_missing_permission() -> None:
    program = build_refused_file_write_demo_program()
    disparity = program.history[-1].outcome.inference.from_disparity

    assert "write lacks Permission" in disparity.description


def test_supervised_worker_demo_produces_program() -> None:
    program = build_supervised_worker_demo_program()

    assert isinstance(program, Program)


def test_supervised_worker_demo_history_contains_revision() -> None:
    program = build_supervised_worker_demo_program()

    assert len(program.history) >= 1


def test_supervised_worker_demo_concept_contains_worker_program_dictum() -> None:
    program = build_supervised_worker_demo_program()

    assert any(
        dictum.subject == "worker" and dictum.meaning == "Program"
        for dictum in program.concept.dicta
    )


def test_supervised_worker_demo_concept_contains_supervisor_requirement() -> None:
    program = build_supervised_worker_demo_program()

    assert any(
        dictum.subject == "supervisor"
        and dictum.meaning == "requires worker Alive"
        for dictum in program.concept.dicta
    )


def test_supervised_worker_demo_concept_contains_worker_crash() -> None:
    program = build_supervised_worker_demo_program()

    assert any(
        dictum.subject == "worker Outcome" and dictum.meaning == "crash"
        for dictum in program.concept.dicta
    )


def test_supervised_worker_demo_concept_contains_worker_not_alive() -> None:
    program = build_supervised_worker_demo_program()

    assert any(
        dictum.subject == "worker" and dictum.meaning == "not Alive"
        for dictum in program.concept.dicta
    )


def test_supervised_worker_demo_concept_contains_known_good_concept() -> None:
    program = build_supervised_worker_demo_program()

    assert any(
        dictum.subject == "known-good worker Concept"
        and dictum.meaning == "exists"
        for dictum in program.concept.dicta
    )


def test_supervised_worker_demo_concept_contains_worker_alive_after_restart() -> None:
    program = build_supervised_worker_demo_program()
    alive_dicta = [
        dictum
        for dictum in program.concept.dicta
        if dictum.subject == "worker" and dictum.meaning == "Alive"
    ]

    assert len(alive_dicta) >= 2


def test_supervised_worker_demo_disparity_mentions_worker_not_alive() -> None:
    program = build_supervised_worker_demo_program()
    disparity = program.history[-1].outcome.inference.from_disparity

    assert "worker is not Alive" in disparity.description


def test_supervised_worker_demo_revision_mentions_restart_or_restore() -> None:
    program = build_supervised_worker_demo_program()
    revision = program.history[-1]

    revision_text = " ".join([*revision.changes, revision.note or ""])

    assert "worker restarted" in revision_text
    assert "restores worker is Alive" in revision_text


def test_agent_edit_demo_produces_program() -> None:
    program = build_agent_edit_demo_program()

    assert isinstance(program, Program)


def test_agent_edit_demo_history_contains_revision() -> None:
    program = build_agent_edit_demo_program()

    assert len(program.history) >= 1


def test_agent_edit_demo_concept_contains_agent_edit_as_datum() -> None:
    program = build_agent_edit_demo_program()

    assert any(
        dictum.subject == "agent edit" and dictum.meaning == "Datum"
        for dictum in program.concept.dicta
    )


def test_agent_edit_demo_concept_contains_behavior_preservation() -> None:
    program = build_agent_edit_demo_program()

    assert any(
        dictum.subject == "agent edit"
        and dictum.meaning == "preserves add_one behavior"
        for dictum in program.concept.dicta
    )


def test_agent_edit_demo_concept_contains_checked_equivalence_qualification() -> None:
    program = build_agent_edit_demo_program()

    assert any(
        dictum.subject == "agent edit"
        and dictum.meaning == "qualifies by checked equivalence"
        for dictum in program.concept.dicta
    )


def test_agent_edit_demo_outcome_or_revision_mentions_acceptance() -> None:
    program = build_agent_edit_demo_program()
    revision = program.history[-1]

    revision_text = " ".join([*revision.changes, revision.note or ""])

    assert "agent edit accepted" in str(revision.outcome.result) or (
        "agent edit accepted" in revision_text
    )


def test_agent_edit_demo_revision_mentions_preserved_behavior() -> None:
    program = build_agent_edit_demo_program()
    revision = program.history[-1]

    revision_text = " ".join([*revision.changes, revision.note or ""])

    assert "preserves add_one behavior" in revision_text


def test_refused_agent_edit_demo_produces_program() -> None:
    program = build_refused_agent_edit_demo_program()

    assert isinstance(program, Program)


def test_refused_agent_edit_demo_history_contains_revision() -> None:
    program = build_refused_agent_edit_demo_program()

    assert len(program.history) >= 1


def test_refused_agent_edit_demo_concept_contains_agent_edit_as_datum() -> None:
    program = build_refused_agent_edit_demo_program()

    assert any(
        dictum.subject == "agent edit" and dictum.meaning == "Datum"
        for dictum in program.concept.dicta
    )


def test_refused_agent_edit_demo_concept_contains_behavior_change() -> None:
    program = build_refused_agent_edit_demo_program()

    assert any(
        dictum.subject == "agent edit"
        and dictum.meaning == "changes add_one behavior"
        for dictum in program.concept.dicta
    )


def test_refused_agent_edit_demo_concept_contains_failed_equivalence() -> None:
    program = build_refused_agent_edit_demo_program()

    assert any(
        dictum.subject == "agent edit"
        and dictum.meaning == "does not qualify by checked equivalence"
        for dictum in program.concept.dicta
    )


def test_refused_agent_edit_demo_disparity_mentions_behavior_violation() -> None:
    program = build_refused_agent_edit_demo_program()
    disparity = program.history[-1].outcome.inference.from_disparity

    assert "violates behavior preservation Purpose" in disparity.description


def test_refused_agent_edit_demo_outcome_or_revision_mentions_refusal() -> None:
    program = build_refused_agent_edit_demo_program()
    revision = program.history[-1]

    revision_text = " ".join([*revision.changes, revision.note or ""])

    assert "agent edit refused" in str(revision.outcome.result) or (
        "agent edit refused" in revision_text
    )


def test_refused_agent_edit_demo_revision_preserves_original_behavior() -> None:
    program = build_refused_agent_edit_demo_program()
    revision = program.history[-1]

    revision_text = " ".join([*revision.changes, revision.note or ""])

    assert "preserves original add_one behavior" in revision_text
