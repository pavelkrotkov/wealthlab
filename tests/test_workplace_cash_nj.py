"""A supplied NJ withholding rate changes liquidity and payment credits, not gross income."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_withdrawal_example import synthetic


def test_state_source_tax_reduces_optional_deposit_and_is_credited_once():
    data = synthetic().model_dump(mode="json")
    data["workplace_plan"]["cash_withdrawals"]["orders"][0]["nj_withholding_rate"] = ".05"
    rows = project(Scenario.model_validate(data))
    assert rows[1]["hsa_personal_contributions"] == 7500
    assert rows[1]["tax_source_withholding"] == 2500
    assert rows[11]["annual_tax"]["new_jersey"]["gross_income"] == 10000
    assert rows[11]["annual_tax"]["state_income_tax_deduction_input"] == 500
    assert rows[15]["tax_refund_received"] == 2500
    assert rows[-1]["net_wealth"] == 100000
