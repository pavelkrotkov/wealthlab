"""The combined IRA workbench exposes funded deposits, deduction and eligibility context."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_combined_ira_workbench_shows_cash_and_contribution_tax_inputs():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("IRA withdrawals").run()
    app.selectbox[0].set_value("Contributions with withdrawals").run()
    app.button(key="FormSubmitter:ira_withdrawals-Project IRA withdrawals").click().run()
    assert not app.exception
    assert not app.error
    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Cash remaining before tax payments"] == "$39,000.00"
    assert (metrics["IRA contributions funded"], metrics["Federal IRA deduction"]) == (
        "$6,000.00",
        "$3,000.00",
    )
    assert "Decimal(" not in str(app.json[0].value)
