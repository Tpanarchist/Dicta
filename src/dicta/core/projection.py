"""Projection helpers for deriving live Concept state from Revisions."""

from dicta.core.models import Concept, Dictum, Revision, RevisionOperation


def project_concept(
    initial: Concept,
    revisions: tuple[Revision, ...] | list[Revision],
) -> Concept:
    """Fold structured Revision operations over a Concept copy."""

    concept = initial.model_copy(deep=True)
    for revision in revisions:
        for operation in revision.operations:
            _apply_operation(concept, operation)
    return concept


def _apply_operation(concept: Concept, operation: RevisionOperation) -> None:
    if operation.operation == "add_dictum":
        concept.dicta.append(_require_dictum(operation))
        return

    if operation.operation == "remove_dictum":
        _remove_dictum(concept, operation)
        return

    if operation.operation == "replace_dictum":
        _remove_dictum(concept, operation)
        concept.dicta.append(_require_dictum(operation))
        return

    msg = f"unsupported RevisionOperation: {operation.operation}"
    raise ValueError(msg)


def _require_dictum(operation: RevisionOperation) -> Dictum:
    if operation.dictum is None:
        msg = f"{operation.operation} requires a Dictum payload"
        raise ValueError(msg)
    return operation.dictum.model_copy(deep=True)


def _remove_dictum(concept: Concept, operation: RevisionOperation) -> None:
    if operation.from_meaning is None:
        msg = f"{operation.operation} requires from_meaning"
        raise ValueError(msg)

    concept.dicta = [
        dictum
        for dictum in concept.dicta
        if not (
            dictum.subject == operation.subject
            and dictum.meaning == operation.from_meaning
        )
    ]
