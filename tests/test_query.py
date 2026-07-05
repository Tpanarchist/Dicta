from dicta.core.program import (
    build_agent_edit_demo_program,
    build_arithmetic_demo_program,
    build_file_write_demo_program,
    build_refused_agent_edit_demo_program,
    build_refused_file_write_demo_program,
)
from dicta.core.query import (
    dicta_by_kind,
    dicta_with_tag,
    disparities_by_kind,
    has_dictum_meaning,
    outcomes_by_kind,
    revisions_by_kind,
)


def test_dicta_by_kind_finds_effect_dicta() -> None:
    program = build_file_write_demo_program()

    dicta = dicta_by_kind(program, "effect")

    assert any(dictum.subject == "write" and dictum.meaning == "changes Disk" for dictum in dicta)


def test_dicta_by_kind_finds_permission_dicta() -> None:
    program = build_refused_file_write_demo_program()

    dicta = dicta_by_kind(program, "permission")

    assert any(
        dictum.subject == "Permission"
        and dictum.meaning == "does not qualify for protected/report.txt"
        for dictum in dicta
    )


def test_dicta_with_tag_finds_tagged_dictum() -> None:
    program = build_file_write_demo_program()

    dicta = dicta_with_tag(program, "disk")

    assert any(dictum.kind == "effect" for dictum in dicta)


def test_has_dictum_meaning_finds_visible_meaning() -> None:
    program = build_arithmetic_demo_program()

    assert has_dictum_meaning(program, "3 + 4 is 7")


def test_disparities_by_kind_finds_permission_denied() -> None:
    program = build_refused_file_write_demo_program()

    disparities = disparities_by_kind(program, "permission_denied")

    assert len(disparities) == 1
    assert disparities[0].description == "write lacks Permission for protected/report.txt"


def test_outcomes_by_kind_finds_agent_refusal() -> None:
    program = build_refused_agent_edit_demo_program()

    outcomes = outcomes_by_kind(program, "agent_refusal")

    assert len(outcomes) == 1
    assert outcomes[0].result == "agent edit refused"


def test_revisions_by_kind_finds_agent_edit_acceptance() -> None:
    program = build_agent_edit_demo_program()

    revisions = revisions_by_kind(program, "accept_agent_edit")

    assert len(revisions) == 1
    assert revisions[0].changes == [
        "Concept records accepted agent edit",
        "Concept preserves add_one behavior",
    ]
