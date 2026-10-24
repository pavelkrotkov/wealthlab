"""A complete synthetic benefit household loads, calculates and remains editable in the UI."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_generated_claims_project_in_the_household_and_show_taxable_benefits():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.button[0].click().run()
    assert any(
        c.label == "Include generated Social Security payments" and c.value for c in app.checkbox
    )
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$244,250.00"
    tax = next(frame.value for frame in app.dataframe if "taxable_social_security" in frame.value)
    assert tax.iloc[-1]["taxable_social_security"] == 3050
