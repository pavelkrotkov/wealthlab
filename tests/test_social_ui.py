"""Execute the claim-date workbench and verify the corrected delayed-credit/spouse total."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_social_security_workbench_executes_ordinary_claims():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py").run()
    app.sidebar.radio[0].set_value("Retirement").run()
    app.radio(key="retirement_mode").set_value("Social Security").run()
    app.button(key="FormSubmitter:social_case-Project Social Security claims").click().run()
    assert not app.exception
    assert not app.error
    assert app.metric[0].value == "$152,250.00"
    assert (
        app.dataframe[0]
        .value.query("year == 2031 and member == 'spouse'")["issued_before_offsets"]
        .iloc[0]
        == 15000
    )
