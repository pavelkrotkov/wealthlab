"""CLI and UI run the same finite grid, retain uncertainty and reproduce actual cash."""

import json
from pathlib import Path

import pytest
from optimization_cases import flat
from streamlit.testing.v1 import AppTest
from test_local_cli import invoke

from wealthlab.household.report import encode

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def matched(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("optimizer-cli")
    path = tmp_path / "allowed-policies.json"
    path.write_text(flat().model_dump_json(), encoding="utf-8")
    process = invoke(["optimize", str(path)], tmp_path)
    assert process.returncode == 0, process.stderr
    result = json.loads(process.stdout)
    app = AppTest.from_file(ROOT / "app.py", default_timeout=180).run()
    app.radio[0].set_value("Optimize").run()
    app.text_area("policy_search_editor").set_value(path.read_text())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    view = json.loads(encode(app.session_state["policy_search_result"]))
    return result, view, sorted(p.name for p in tmp_path.iterdir()), path.name


def test_native_optimizer_cli_and_ui_match_actual_selected_tax_cash_and_frozen_validation(matched):
    result, view, files, name = matched
    assert result == view
    assert result["selection"] == "candidate_1"
    assert result["candidates"][0]["median_real_after_tax_exit_wealth"] == "251999.00"
    assert result["held_out"]["selected_candidate"] == result["selection"]
    assert files == [name]
    assert result["input_sha256"]
    assert result["dependencies"]["taxcalc"]
