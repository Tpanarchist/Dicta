"""Qualification strength ladder and constructors for early Dicta semantics."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dicta.core.models import Qualification


class QualificationStrength(StrEnum):
    """First ladder steps for how a Dictum stands."""

    ASSERTED = "asserted"
    TESTED = "tested"
    CHECKED = "checked"
    PROVED = "proved"


def asserted(
    basis: str = "author assertion",
    conditions: tuple[str, ...] = (),
    timing: str = "author-time",
) -> Qualification:
    """Create an asserted Qualification."""

    from dicta.core.models import Qualification

    return Qualification(
        strength=QualificationStrength.ASSERTED,
        basis=basis,
        conditions=conditions,
        timing=timing,
    )


def tested(
    basis: str = "test witness",
    conditions: tuple[str, ...] = (),
    timing: str = "author-time",
) -> Qualification:
    """Create a tested Qualification."""

    from dicta.core.models import Qualification

    return Qualification(
        strength=QualificationStrength.TESTED,
        basis=basis,
        conditions=conditions,
        timing=timing,
    )


def checked(
    basis: str = "checker result",
    conditions: tuple[str, ...] = (),
    timing: str = "author-time",
) -> Qualification:
    """Create a checked Qualification."""

    from dicta.core.models import Qualification

    return Qualification(
        strength=QualificationStrength.CHECKED,
        basis=basis,
        conditions=conditions,
        timing=timing,
    )


def proved(
    basis: str = "proof",
    conditions: tuple[str, ...] = (),
    timing: str = "author-time",
) -> Qualification:
    """Create a proved Qualification."""

    from dicta.core.models import Qualification

    return Qualification(
        strength=QualificationStrength.PROVED,
        basis=basis,
        conditions=conditions,
        timing=timing,
    )
