from dicta.core.models import Program
from dicta.core.program import build_arithmetic_demo_program


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
