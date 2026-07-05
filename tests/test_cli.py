from typer.testing import CliRunner

from dicta.cli import app


def test_file_write_demo_cli_output_preserves_visible_text() -> None:
    runner = CliRunner()

    result = runner.invoke(app, ["file-write-demo"])

    assert result.exit_code == 0
    assert 'Datum: write report.txt "hello"' in result.output
    assert "* write changes Disk" in result.output
    assert "* write requires Permission" in result.output
    assert "* write accepted" in result.output
    assert '* Concept records report.txt contains "hello"' in result.output
