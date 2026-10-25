"""Real fee-enabled command output cannot enter the public checkout.

Only original synthetic input is written under the selected test runtime.
The native selected-output writer must refuse that actual repository path;
stdout reports remain explicit and no external private directory is selected.
"""

from test_local_cli import invoke

from tests.optimizer_advisory_cases import case


def test_fee_enabled_cli_refuses_selected_report_writes_inside_actual_code_checkout(tmp_path):
    source = tmp_path / "synthetic-input.json"
    source.write_text(case().model_dump_json(), encoding="utf-8")
    target = tmp_path / "must-not-exist.json"
    process = invoke(
        ["optimize", str(source), "--output-directory", str(tmp_path), "--filename", target.name],
        tmp_path,
    )
    assert process.returncode == 2 and process.stdout == ""
    assert not target.exists() and source.exists()
    assert str(tmp_path) not in process.stderr
    assert sorted(p.name for p in tmp_path.iterdir()) == [source.name]
