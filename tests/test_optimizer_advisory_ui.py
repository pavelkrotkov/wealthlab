"""The real optimizer UI compares sourced after-fee native option and new-life outcomes."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from tests.optimizer_advisory_cases import case


def test_optimizer_common_fee_controls_and_actual_cash_comparison_run_together():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=120
    ).run()
    app.radio[0].set_value("Optimize").run()
    app.checkbox(key="new_option_allocation_starter").check().run()
    app.checkbox(key="new_life_starter").check().run()
    app.checkbox(key="optimizer_advisory_starter").check().run()
    text = str(app.text_area(key="policy_search_editor").value)
    assert '"presence": "if_present"' in text
    app.text_area(key="policy_search_editor").set_value(case().model_dump_json())
    app.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert not app.exception
    assert not app.error
    result = app.session_state["policy_search_result"]
    assert result["configured_validation_passed"] is True
    assert result["held_out"]["assessment"]["median_advisory_fees_paid"] > 0
    assert any(s.value == "Evaluated policy choices" for s in app.subheader)
