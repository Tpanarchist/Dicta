from typer.testing import CliRunner

from dicta.cli import app


def test_current_cli_commands_run() -> None:
    runner = CliRunner()

    for command in [
        "version",
        "demo",
        "appraise-arithmetic-demo",
        "appraise-invalid-arithmetic-demo",
        "invalid-demo",
        "counter-demo",
        "appraise-counter-demo",
        "appraise-refused-counter-demo",
        "file-write-demo",
        "refused-file-write-demo",
        "supervised-worker-demo",
        "agent-edit-demo",
        "refused-agent-edit-demo",
    ]:
        result = runner.invoke(app, [command])

        assert result.exit_code == 0, command
        assert result.output


def test_demo_cli_renders_qualification_data() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["demo"])

    assert result.exit_code == 0
    assert "Qualification:" in result.output
    assert "* 3 + 4 is 7: checked" in result.output
    assert "basis=hard-coded arithmetic evaluation" in result.output


def test_file_write_demo_cli_output_preserves_visible_text() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["file-write-demo"])

    assert result.exit_code == 0
    assert 'Datum: write report.txt "hello"' in result.output
    assert "* write changes Disk" in result.output
    assert "* write requires Permission" in result.output
    assert "* write accepted" in result.output
    assert '* Concept records report.txt contains "hello"' in result.output
