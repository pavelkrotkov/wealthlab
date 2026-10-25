"""Compare submitted household inputs against an automatic personal HSA control.

Edited wages must propagate into that control. Simultaneous automatic and
supplied policies cannot silently override one another or use a stale example.
"""

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from wealthlab.household.scenario import Scenario
from wealthlab.markets.hsa_payroll_example import synthetic
from wealthlab.ui.market_hsa_payroll import policy_text


def test_actual_markets_editor_runs_automatic_matched_hsa_funding_control():
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=90
    ).run()
    app.radio[0].set_value("Markets").run()
    app.radio(key="market_workbench").set_value("Household funding").run()
    app.selectbox(key="market_account_scope").set_value("HSA payroll and employment").run()
    next(b for b in app.button if b.label == "Project actual household paths").click().run()
    assert not app.exception
    assert not app.error
    bundle = app.session_state["market_household_result"]
    assert bundle["comparison"]["result"]["outcomes"][0]["hsa_personal_deposits"] == 12000
    assert bundle["baseline"]["batch_id"] == bundle["comparison"]["result"]["batch_id"]
    assert any(m.label == "Funded HSA salary reductions" for m in app.metric)


def test_automatic_control_uses_edited_inputs_instead_of_a_stale_example():
    household, _, _ = synthetic()
    data = household.model_dump(mode="json")
    data["incomes"][0]["monthly_amount"] = "9000"
    household = Scenario.model_validate(data)
    control = Scenario.model_validate_json(policy_text(household, "", True))
    assert control.incomes == household.incomes
    assert control.compensation_plan == household.compensation_plan
    assert control.hsa_plan is not None
    assert control.hsa_plan.payroll is None
    assert len(control.hsa_plan.contributions) == 24


def test_supplied_policy_and_automatic_policy_cannot_silently_override_each_other():
    household, _, _ = synthetic()
    with pytest.raises(ValueError, match="not both"):
        policy_text(household, json.dumps(dict(household="supplied")), True)
    assert policy_text(household, "supplied", False) == "supplied"
