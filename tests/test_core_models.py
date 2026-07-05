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
    asserted as make_asserted,
    checked as make_checked,
    proved as make_proved,
    tested as make_tested,
)


def _make_inference_with_disparity(
    *,
    disparity_kind: str | None = None,
    disparity_tags: tuple[str, ...] = (),
) -> Inference:
    datum = Datum(value="demo")
    purpose = Purpose(statement="test structured semantics")
    concept = Concept(name="test-concept", purpose=purpose)
    disparity = Disparity(
        datum=datum,
        concept=concept,
        purpose=purpose,
        description="demo disparity",
        kind=disparity_kind,
        tags=disparity_tags,
    )
    return Inference(from_disparity=disparity, derived="demo inference")


def test_qualification_can_be_created() -> None:
    qualification = Qualification(
        strength=QualificationStrength.ASSERTED,
        basis="given",
        conditions=["demo"],
        timing="now",
    )

    assert qualification.strength == QualificationStrength.ASSERTED
    assert qualification.basis == "given"
    assert qualification.conditions == ("demo",)
    assert qualification.timing == "now"


def test_qualification_defaults_record_author_time() -> None:
    qualification = Qualification()

    assert qualification.strength == QualificationStrength.ASSERTED
    assert qualification.conditions == ()
    assert qualification.timing == "author-time"


def test_qualification_constructors_create_expected_strengths() -> None:
    assert make_asserted().strength == QualificationStrength.ASSERTED
    assert make_tested().strength == QualificationStrength.TESTED
    assert make_checked().strength == QualificationStrength.CHECKED
    assert make_proved().strength == QualificationStrength.PROVED


def test_dictum_can_hold_qualification() -> None:
    qualification = Qualification(strength=QualificationStrength.TESTED)
    dictum = Dictum(subject="3", meaning="Number", qualification=qualification)

    assert dictum.qualification.strength == QualificationStrength.TESTED


def test_dictum_can_carry_visible_display_text() -> None:
    dictum = Dictum(subject="3 + 4", meaning="7", display="3 + 4 is 7")

    assert dictum.display == "3 + 4 is 7"
    assert dictum.visible_text() == "3 + 4 is 7"


def test_dictum_visible_text_falls_back_to_subject_and_meaning() -> None:
    dictum = Dictum(subject="3", meaning="Number")

    assert dictum.visible_text() == "3 is Number"


def test_concept_can_hold_dicta() -> None:
    dictum = Dictum(subject="3", meaning="Number")
    concept = Concept(
        name="numbers",
        purpose=Purpose(statement="Represent numeric meaning.", mode="test"),
        dicta=[dictum],
    )

    assert concept.dicta == [dictum]


def test_program_can_hold_concept() -> None:
    concept = Concept(name="numbers", purpose=Purpose(statement="Represent numbers."))
    program = Program(name="test-program", concept=concept)

    assert program.concept == concept
    assert program.history == []


def test_dictum_can_carry_kind_and_tags() -> None:
    dictum = Dictum(
        subject="write",
        meaning="changes Disk",
        kind="effect",
        tags=("disk", "write"),
    )

    assert dictum.kind == "effect"
    assert dictum.tags == ("disk", "write")


def test_disparity_can_carry_kind_and_tags() -> None:
    inference = _make_inference_with_disparity(
        disparity_kind="permission_denied",
        disparity_tags=("write", "protected/report.txt"),
    )
    disparity = inference.from_disparity

    assert disparity.kind == "permission_denied"
    assert disparity.tags == ("write", "protected/report.txt")


def test_disparity_snapshots_concept() -> None:
    purpose = Purpose(statement="observe before state")
    concept = Concept(
        name="snapshot-demo",
        purpose=purpose,
        dicta=[Dictum(subject="counter", meaning="0")],
    )
    disparity = Disparity(
        datum=Datum(value="counter = counter + 1"),
        concept=concept,
        purpose=purpose,
        description="counter is 0 before revision",
    )

    concept.dicta.append(Dictum(subject="counter", meaning="1"))

    assert [dictum.meaning for dictum in disparity.concept.dicta] == ["0"]


def test_outcome_can_carry_kind_and_tags() -> None:
    outcome = Outcome(
        inference=_make_inference_with_disparity(),
        result="write refused",
        kind="effect_refused",
        tags=("disk", "write"),
    )

    assert outcome.kind == "effect_refused"
    assert outcome.tags == ("disk", "write")


def test_revision_can_carry_kind_and_tags() -> None:
    outcome = Outcome(inference=_make_inference_with_disparity(), result="accepted")
    revision = Revision(
        outcome=outcome,
        changes=["Concept records accepted agent edit"],
        kind="accept_agent_edit",
        tags=("agent", "add_one"),
    )

    assert revision.kind == "accept_agent_edit"
    assert revision.tags == ("agent", "add_one")
