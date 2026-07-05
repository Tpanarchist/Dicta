"""Core semantic contracts for Dicta."""

from dicta.core.models import (
    Concept,
    Datum,
    Dictum,
    Disparity,
    Inference,
    Outcome,
    Program,
    Purpose,
    Qualification,
    Revision,
)
from dicta.core.qualification import (
    QualificationStrength,
    asserted,
    checked,
    proved,
    tested,
)
from dicta.core.query import (
    dicta_by_kind,
    dicta_by_qualification_strength,
    dicta_with_tag,
    disparities_by_kind,
    has_dictum_meaning,
    outcomes_by_kind,
    revisions_by_kind,
)

__all__ = [
    "Concept",
    "Datum",
    "Dictum",
    "Disparity",
    "Inference",
    "Outcome",
    "Program",
    "Purpose",
    "Qualification",
    "QualificationStrength",
    "Revision",
    "asserted",
    "checked",
    "dicta_by_kind",
    "dicta_by_qualification_strength",
    "dicta_with_tag",
    "disparities_by_kind",
    "has_dictum_meaning",
    "outcomes_by_kind",
    "proved",
    "revisions_by_kind",
    "tested",
]
