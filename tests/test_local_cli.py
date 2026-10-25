"""Native CLI execution starts outside the project and agrees with the real UI.

Only the public synthetic source is read. Captured stdout stays in memory;
no private output directory or real household records are used by these checks.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def invoke(args, cwd):
    return subprocess.run(
        [sys.executable, "-m", "wealthlab", *args],
        cwd=cwd,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


def test_native_cli_projection_and_real_ui_have_identical_cash_outcomes(tmp_path):
    result = invoke(["project", str(ROOT / "examples/synthetic.json")], tmp_path)
    assert result.returncode == 0
    report = json.loads(result.stdout)
    view = AppTest.from_file(ROOT / "app.py").run(timeout=90)
    view.button(key="FormSubmitter:household-Validate and project").click().run(timeout=90)
    assert not view.exception
    assert report["months"][-1]["net_wealth"] == "224000.00"
    assert view.metric[0].value == "$224,000.00"
    assert report["input_sha256"]
    assert report["taxes_modeled"] is False


def test_native_cli_compare_uses_the_same_selected_input_twice_without_creating_files(tmp_path):
    source = str(ROOT / "examples/synthetic.json")
    result = invoke(["compare", source, source], tmp_path)
    report = json.loads(result.stdout)
    assert result.returncode == 0
    assert report["ending_wealth_change_usd"] == "0.00"
    assert report["baseline"]["months"] == report["candidate"]["months"]
    assert not list(tmp_path.iterdir())


def test_invalid_selected_input_does_not_echo_private_values_or_paths(tmp_path):
    source = tmp_path / "private_path_marker.json"
    source.write_text('{"private_value_marker":"never_echo"}', encoding="utf-8")
    result = invoke(["project", str(source)], tmp_path)
    assert result.returncode == 2
    assert result.stdout == ""
    assert "private_value_marker" not in result.stderr
    assert "private_path_marker" not in result.stderr
