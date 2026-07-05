from dicta.core.models import Concept, Dictum, Program, Purpose, Qualification
from dicta.core.qualification import QualificationStrength


def test_qualification_can_be_created() -> None:
    qualification = Qualification(
        strength=QualificationStrength.ASSERTED,
        basis="given",
        conditions=["demo"],
        timing="now",
    )

    assert qualification.strength == QualificationStrength.ASSERTED
    assert qualification.basis == "given"


def test_dictum_can_hold_qualification() -> None:
    qualification = Qualification(strength=QualificationStrength.TESTED)
    dictum = Dictum(subject="3", meaning="Number", qualification=qualification)

    assert dictum.qualification.strength == QualificationStrength.TESTED


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
