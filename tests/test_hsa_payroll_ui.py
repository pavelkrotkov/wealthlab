"""The actual Household form exposes funded salary reductions and independent tax scope."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_payroll_hsa_household_form_runs_the_confirmed_salary_reduction_case():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    click(app, "Load synthetic payroll HSA household")
    click(app, "Validate and project")
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Funded HSA salary reductions"] == "$6,000.00"
    assert metrics["Unfilled HSA salary elections"] == "$0.00"
    assert metrics["External employer HSA funding"] == "$500.00"
    assert metrics["Personal HSA deposits"] == "$1,000.00"


def click(app, label):
    next(b for b in app.button if b.label == label).click().run()
