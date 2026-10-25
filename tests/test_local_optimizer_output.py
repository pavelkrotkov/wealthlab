"""An optimizer report follows the existing atomic private-output and sanitized-error boundary."""

import json

from optimization_cases import flat

from wealthlab import cli, local_files


def test_optimizer_selected_output_preserves_full_audit_and_cannot_overwrite(
    tmp_path, monkeypatch, capsys
):
    source = tmp_path / "allowed.json"
    source.write_text(flat().model_dump_json())
    monkeypatch.setattr(local_files, "REPOSITORY_ROOT", tmp_path / "public")
    args = ["optimize", str(source), "--output-directory", str(tmp_path)]
    assert cli.main(args) == 0
    target = tmp_path / "policy-search.json"
    original = target.read_bytes()
    assert json.loads(original)["selected_training"]["details"][0]["rows"]
    assert cli.main(args) == 2
    assert target.read_bytes() == original
    assert "never overwritten" in capsys.readouterr().err


def test_optimizer_invalid_private_input_is_not_echoed_to_terminal_or_written(tmp_path, capsys):
    source = tmp_path / "private_path_marker.json"
    source.write_text('{"private_value_marker":"never_echo"}')
    assert cli.main(["optimize", str(source)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "private_value_marker" not in captured.err and "private_path_marker" not in captured.err
    assert not (tmp_path / "policy-search.json").exists()
