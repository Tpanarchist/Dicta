import pytest

from dicta.core.models import (
    Concept,
    Datum,
    Disparity,
    Inference,
    Outcome,
    Purpose,
    Revision,
    RevisionOperation,
)
from dicta.core.program import produce_dictum
from dicta.core.projection import project_concept


def _revision_with_operations(*operations: RevisionOperation) -> Revision:
    purpose = Purpose(statement="test projection")
    concept = Concept(name="projection-history", purpose=purpose)
    disparity = Disparity(
        datum=Datum(value="test datum"),
        concept=concept,
        purpose=purpose,
        description="test disparity",
    )
    inference = Inference(from_disparity=disparity, derived="test inference")
    outcome = Outcome(inference=inference, result="test outcome")
    return Revision(outcome=outcome, operations=operations)


def _visible_dicta(concept: Concept) -> set[str]:
    return {dictum.visible_text() for dictum in concept.dicta}


def test_project_concept_add_dictum_appends_visible_dictum() -> None:
    initial = Concept(name="projection-test")
    added = produce_dictum("counter", "1", display="counter is 1")
    revision = _revision_with_operations(
        RevisionOperation(
            operation="add_dictum",
            subject="counter",
            to_meaning="1",
            dictum=added,
        )
    )

    projected = project_concept(initial, [revision])

    assert "counter is 1" in _visible_dicta(projected)


def test_project_concept_remove_dictum_removes_matching_meaning() -> None:
    initial = Concept(
        name="projection-test",
        dicta=[produce_dictum("worker", "not Alive", display="worker is not Alive")],
    )
    revision = _revision_with_operations(
        RevisionOperation(
            operation="remove_dictum",
            subject="worker",
            from_meaning="not Alive",
        )
    )

    projected = project_concept(initial, [revision])

    assert "worker is not Alive" not in _visible_dicta(projected)


def test_project_concept_remove_dictum_removes_all_matching_dicta() -> None:
    initial = Concept(
        name="projection-test",
        dicta=[
            produce_dictum("worker", "not Alive", display="worker is not Alive"),
            produce_dictum("worker", "not Alive", display="worker is not Alive"),
            produce_dictum("worker", "Program", display="worker is Program"),
        ],
    )
    revision = _revision_with_operations(
        RevisionOperation(
            operation="remove_dictum",
            subject="worker",
            from_meaning="not Alive",
        )
    )

    projected = project_concept(initial, [revision])

    assert "worker is not Alive" not in _visible_dicta(projected)
    assert "worker is Program" in _visible_dicta(projected)


def test_project_concept_replace_dictum_removes_old_and_adds_new() -> None:
    initial = Concept(
        name="projection-test",
        dicta=[produce_dictum("counter", "0", display="counter is 0")],
    )
    replacement = produce_dictum("counter", "1", display="counter is 1")
    revision = _revision_with_operations(
        RevisionOperation(
            operation="replace_dictum",
            subject="counter",
            from_meaning="0",
            to_meaning="1",
            dictum=replacement,
        )
    )

    projected = project_concept(initial, [revision])

    assert "counter is 0" not in _visible_dicta(projected)
    assert "counter is 1" in _visible_dicta(projected)


def test_project_concept_does_not_mutate_initial_concept() -> None:
    initial = Concept(
        name="projection-test",
        dicta=[produce_dictum("counter", "0", display="counter is 0")],
    )
    replacement = produce_dictum("counter", "1", display="counter is 1")
    revision = _revision_with_operations(
        RevisionOperation(
            operation="replace_dictum",
            subject="counter",
            from_meaning="0",
            to_meaning="1",
            dictum=replacement,
        )
    )

    project_concept(initial, [revision])

    assert "counter is 0" in _visible_dicta(initial)


def test_project_concept_isolates_operation_payload_from_projection() -> None:
    initial = Concept(name="projection-test")
    payload = produce_dictum("counter", "1", display="counter is 1")
    operation = RevisionOperation(
        operation="add_dictum",
        subject="counter",
        to_meaning="1",
        dictum=payload,
    )
    revision = _revision_with_operations(operation)

    projected = project_concept(initial, [revision])
    assert operation.dictum is not None
    operation.dictum.meaning = "2"
    assert projected.dicta[0].meaning == "1"

    projected.dicta[0].meaning = "3"

    assert projected.dicta[0].meaning == "3"
    assert operation.dictum.meaning == "2"


def test_project_concept_folds_revisions_in_order() -> None:
    initial = Concept(
        name="projection-test",
        dicta=[produce_dictum("counter", "0", display="counter is 0")],
    )
    counter_one = produce_dictum("counter", "1", display="counter is 1")
    counter_two = produce_dictum("counter", "2", display="counter is 2")
    first_revision = _revision_with_operations(
        RevisionOperation(
            operation="replace_dictum",
            subject="counter",
            from_meaning="0",
            to_meaning="1",
            dictum=counter_one,
        )
    )
    second_revision = _revision_with_operations(
        RevisionOperation(
            operation="replace_dictum",
            subject="counter",
            from_meaning="1",
            to_meaning="2",
            dictum=counter_two,
        )
    )

    projected = project_concept(initial, [first_revision, second_revision])

    assert "counter is 0" not in _visible_dicta(projected)
    assert "counter is 1" not in _visible_dicta(projected)
    assert "counter is 2" in _visible_dicta(projected)


def test_project_concept_remove_missing_target_raises() -> None:
    initial = Concept(name="projection-test")
    revision = _revision_with_operations(
        RevisionOperation(
            operation="remove_dictum",
            subject="counter",
            from_meaning="0",
        )
    )

    with pytest.raises(ValueError, match="remove_dictum target not found"):
        project_concept(initial, [revision])


def test_project_concept_replace_missing_target_raises() -> None:
    initial = Concept(name="projection-test")
    replacement = produce_dictum("counter", "1", display="counter is 1")
    revision = _revision_with_operations(
        RevisionOperation(
            operation="replace_dictum",
            subject="counter",
            from_meaning="0",
            to_meaning="1",
            dictum=replacement,
        )
    )

    with pytest.raises(ValueError, match="replace_dictum target not found"):
        project_concept(initial, [revision])


def test_project_concept_unknown_operation_raises() -> None:
    initial = Concept(name="projection-test")
    revision = _revision_with_operations(
        RevisionOperation(operation="rename_dictum", subject="counter")
    )

    with pytest.raises(ValueError, match="unsupported RevisionOperation"):
        project_concept(initial, [revision])


def test_project_concept_rejects_payload_meaning_mismatch() -> None:
    initial = Concept(name="projection-test")
    payload = produce_dictum("counter", "2", display="counter is 2")
    revision = _revision_with_operations(
        RevisionOperation(
            operation="add_dictum",
            subject="counter",
            to_meaning="1",
            dictum=payload,
        )
    )

    with pytest.raises(ValueError, match="Dictum meaning does not match"):
        project_concept(initial, [revision])


def test_project_concept_rejects_payload_subject_mismatch() -> None:
    initial = Concept(name="projection-test")
    payload = produce_dictum("other", "1", display="other is 1")
    revision = _revision_with_operations(
        RevisionOperation(
            operation="add_dictum",
            subject="counter",
            to_meaning="1",
            dictum=payload,
        )
    )

    with pytest.raises(ValueError, match="Dictum subject does not match"):
        project_concept(initial, [revision])
