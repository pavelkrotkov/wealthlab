"""Submit the actual household editor and inspect current-bill/HSA/cash outcomes."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_current_medical_bill_household_runs_with_visible_arrears():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    click(app, "Load synthetic current medical bills")
    click(app, "Validate and project")
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Direct HSA medical payments"] == "$3,000.00"
    assert metrics["Cash medical bill payments"] == "$3,000.00"
    assert metrics["Unpaid medical bill liability"] == "$0.00"
    assert metrics["Ending net wealth · nominal USD"] == "$6,000.00"


def click(app, label):
    next(b for b in app.button if b.label == label).click().run()
