"""Selected report paths are atomic and never silently ignored, overwritten or echoed."""

from pathlib import Path

from wealthlab import cli, local_files

SOURCE = Path(__file__).resolve().parents[1] / "examples/synthetic.json"


def test_cli_selected_private_output_is_created_once(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(local_files, "REPOSITORY_ROOT", tmp_path / "public")
    args = ["project", str(SOURCE), "--output-directory", str(tmp_path)]
    assert cli.main(args) == 0
    target = tmp_path / "projection.json"
    before = target.read_bytes()
    assert cli.main(args) == 2
    assert target.read_bytes() == before
    assert "never overwritten" in capsys.readouterr().err


def test_filename_without_selected_directory_does_not_dump_private_results(capsys):
    assert cli.main(["project", str(SOURCE), "--filename", "result.json"]) == 2
    assert capsys.readouterr().out == ""
