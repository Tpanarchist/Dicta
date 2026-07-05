"""Qualification strength ladder for early Dicta semantics."""

from enum import StrEnum


class QualificationStrength(StrEnum):
    """First ladder steps for how a Dictum stands."""

    ASSERTED = "asserted"
    TESTED = "tested"
    CHECKED = "checked"
    PROVED = "proved"
