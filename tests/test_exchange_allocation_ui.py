"""The real form edits contribution choices and reports actual source sales."""

from streamlit.testing.v1 import AppTest


def test_retained_only_preset_exits_actual_source_without_creating_a_fund():
    view = AppTest.from_string(
        "from wealthlab.ui.exchange_fund import show\nshow()", default_timeout=90
    ).run()
    view.selectbox[1].select("Retained source only").run()
    edited = view.text_area[0].value
    assert isinstance(edited, str)
    assert '"contribution_quantity": "0"' in edited
    view.button[0].click().run()
    assert not view.exception
    result = view.session_state["exchange_fund_result"]
    assert result["outcomes"]["exchange"]["positions_closed"] is True
    assert result["rows"]["exchange"][-1]["exchange_source_sale_cash"] == 100000
    assert (
        result["rows"]["exchange"][-1]["exchange_fund_audit"]["exit_status"]["fund_entered"]
        is False
    )
