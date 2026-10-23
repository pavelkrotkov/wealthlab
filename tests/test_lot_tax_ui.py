"""The local UI distinguishes conditional annual tax changes from gross portfolio wealth."""

from test_lot_tax_reporting import reporting_case
from test_lot_ui import workbench
from test_tax_budget_policy import budget_case


def test_nj_override_and_annual_comparison_are_visible():
    payload = reporting_case()
    payload["trades"] = payload["trades"][:1]
    payload["nj_wash_treatment"] = "unconfirmed"
    app = workbench()
    import json

    app.text_area[0].set_value(json.dumps(payload))
    app.selectbox[0].select("federal_rules")
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run(timeout=30)
    assert not app.exception
    assert not app.error
    assert any(item.value == "NJ conditional wash-sale adjustments" for item in app.subheader)
    assert app.dataframe[2].value["Change"][0] == -55


def test_budget_diagnostics_report_the_actual_limit():
    import json

    app = workbench()
    app.text_area[0].set_value(json.dumps(budget_case()))
    app.button(key="FormSubmitter:lot_case-Calculate lot accounting").click().run(timeout=30)
    assert not app.exception
    assert not app.error
    assert any("$500.00 budget (within budget)" in item.value for item in app.caption)
