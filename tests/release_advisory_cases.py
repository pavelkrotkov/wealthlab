"""Original supplied drilling facts explicitly confirm this complete synthetic fee scope.

This fixture does not authorize a starter or an imported scenario to reconfirm a
changed envelope. All figures are original examples, not adviser or household data.
"""

import json
from pathlib import Path

import pytest
from optimization_drilling_search_cases import case as drilling
from streamlit.testing.v1 import AppTest
from test_local_cli import invoke

from wealthlab.optimization.advisory_example import extend
from wealthlab.optimization.drilling_example import confirm_synthetic

ROOT = Path(__file__).resolve().parents[1]


def well():
    data = extend(drilling()).model_dump(mode="json")
    data["dimensions"][0]["locked_choice"] = "well"
    return confirm_synthetic(data)


@pytest.fixture(scope="module")
def matched(tmp_path_factory):
    runtime = tmp_path_factory.mktemp("advisory-cli-ui")
    source = runtime / "original-synthetic-search.json"
    profile = well()
    source.write_text(profile.model_dump_json(), encoding="utf-8")
    process = invoke(["optimize", str(source)], runtime)
    assert process.returncode == 0, process.stderr
    app = AppTest.from_file(ROOT / "app.py", default_timeout=180).run()
    app.radio[0].set_value("Optimize").run()
    app.text_area("policy_search_editor").set_value(source.read_text())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception and not app.error
    return profile, json.loads(process.stdout), app, sorted(p.name for p in runtime.iterdir())
