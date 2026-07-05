"""Small semantic inspection helpers for Dicta Programs."""

from dicta.core.models import Dictum, Disparity, Outcome, Program, Revision
from dicta.core.qualification import QualificationStrength


def _visible_dictum_text(dictum: Dictum) -> str:
    return dictum.visible_text()


def dicta_by_kind(program: Program, kind: str) -> tuple[Dictum, ...]:
    """Return Dicta in the Program Concept with a matching kind."""

    return tuple(dictum for dictum in program.concept.dicta if dictum.kind == kind)


def dicta_with_tag(program: Program, tag: str) -> tuple[Dictum, ...]:
    """Return Dicta in the Program Concept whose tags contain tag."""

    return tuple(dictum for dictum in program.concept.dicta if tag in dictum.tags)


def dicta_by_qualification_strength(
    program: Program,
    strength: QualificationStrength | str,
) -> tuple[Dictum, ...]:
    """Return Dicta whose Qualification strength matches strength."""

    target = QualificationStrength(strength)
    return tuple(
        dictum
        for dictum in program.concept.dicta
        if dictum.qualification.strength == target
    )


def has_dictum_meaning(program: Program, meaning: str) -> bool:
    """Return whether any Dictum has the requested semantic meaning."""

    return any(dictum.meaning == meaning for dictum in program.concept.dicta)


def has_dictum_text(program: Program, text: str) -> bool:
    """Return whether any Dictum has the requested visible text."""

    return any(_visible_dictum_text(dictum) == text for dictum in program.concept.dicta)


def disparities_by_kind(program: Program, kind: str) -> tuple[Disparity, ...]:
    """Return Disparities reachable from Program history with a matching kind."""

    return tuple(
        revision.outcome.inference.from_disparity
        for revision in program.history
        if revision.outcome.inference.from_disparity.kind == kind
    )


def outcomes_by_kind(program: Program, kind: str) -> tuple[Outcome, ...]:
    """Return Outcomes in Program history with a matching kind."""

    return tuple(
        revision.outcome
        for revision in program.history
        if revision.outcome.kind == kind
    )


def revisions_by_kind(program: Program, kind: str) -> tuple[Revision, ...]:
    """Return Revisions in Program history with a matching kind."""

    return tuple(revision for revision in program.history if revision.kind == kind)
