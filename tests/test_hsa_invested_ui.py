"""The actual household form renders invested assets, cash, fees and provider payments."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_invested_hsa_household_editor_runs_with_distinct_cash_and_asset_metrics():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    click(app, "Load synthetic invested HSA household")
    click(app, "Validate and project")
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Invested HSA net assets"] == "$6,548.17"
    assert metrics["Inside-HSA available cash"] == "$0.00"
    assert metrics["HSA custodian fees owed"] == "$50.00"
    check_bill(metrics)


def check_bill(metrics):
    assert metrics["Direct HSA medical payments"] == "$5,000.00"
    assert metrics["Cash medical bill payments"] == "$1,000.00"
    assert metrics["Unpaid medical bill liability"] == "$0.00"


def click(app, label):
    next(b for b in app.button if b.label == label).click().run()
