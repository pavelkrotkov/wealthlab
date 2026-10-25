"""Real UI starters expose observed snapshot cutoffs and honest actual month-end payment dates."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_household_advance_starter_renders_editable_observed_sources_and_actual_cash_audit():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    next(
        b for b in app.button if b.label == "Load synthetic observed advance advisory fees"
    ).click().run()
    text = str(app.text_area(key="advisory_editor").value)
    assert '"valuation_cutoff": "opening"' in text
    assert '"advance_nonrefundable_no_proration_assumed_confirmed": true' in text
    app.button(key="FormSubmitter:household-Validate and project").click().run()
    assert not app.exception
    assert not app.error
    assert any(s.value == "Outer advisory assessments and actual fee cash" for s in app.subheader)


def test_market_advance_profile_keeps_realized_batches_and_stored_native_snapshots():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.checkbox(key="market_advisory_example").check().run()
    app.selectbox(key="market_advisory_profile").set_value("Advance on observed opening").run()
    app.button(key="FormSubmitter:market_household-Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["market_household_result"]["baseline"]
    audit = result["details"][0]["rows"][-1]["advisory_fee_audit"]
    assert audit["observed_snapshots"]
    assert (
        result["household"]["advisory_fee_plan"]["valuation_timing"]
        == "explicit_observed_snapshot_cutoffs"
    )
