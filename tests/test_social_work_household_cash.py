"""Real earnings and net SSA cash enter the household once; claims never fund spending early."""

from social_work_household_cases import case, payload

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.social_household import prepare


def test_cashless_government_claim_increases_wealth_but_does_not_pay_january_spending():
    data = payload()
    data["accounts"][0]["balance"] = 0
    data["expenses"][0]["monthly_amount"] = 800
    data["incomes"] = []
    data["tax_plan"]["income_rules"] = []
    rows = project(Scenario.model_validate(data))
    assert rows[11]["social_security_government_receivable"] == 3372
    assert rows[11]["closing_cash"] == 0
    assert rows[11]["net_wealth"] == 3372
    assert rows[12]["essential_unfunded"] == 238
    assert rows[16]["social_security_refund_cash"] == 3372


def test_prepared_generated_cash_cannot_be_prepared_a_second_time():
    scenario = prepare(case())
    assert scenario.social_work_plan is None
    assert scenario.social_security is None
    assert prepare(scenario) == scenario
    assert sum(i.monthly_amount for i in scenario.incomes if i.id.startswith("ss_")) == 10045
