"""Execute the 529 input form and inspect actual funding and separate annual tax recipients."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_education_workbench_executes_the_synthetic_case():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("Education").run()
    app.button(key="FormSubmitter:education_case-Project education accounts").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$15,000.00"
    assert app.dataframe[0].value["unfunded"].iloc[0] == 3000
    assert list(app.dataframe[1].value["recipient"]) == ["parent", "student"]
