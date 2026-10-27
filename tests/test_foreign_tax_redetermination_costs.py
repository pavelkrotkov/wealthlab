"""Other assessed costs use existing dated expenses, never an assumed interest exemption."""

from foreign_redetermination_cases import synthetic_refund

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_supplied_domestic_charge_debits_the_same_cash_before_optional_contribution():
    data = synthetic_refund().model_dump(mode="json")
    data["expenses"] = [
        dict(
            id="amendment_cost",
            provenance="illustration",
            category="essential",
            start="2027-06-01",
            end="2027-07-01",
            monthly_amount="250",
            currency="USD",
            annual_growth=0,
        )
    ]
    months = {r["date"]: r for r in project(Scenario.model_validate(data))}
    before, after = months["2027-05-01"], months["2027-06-01"]
    assert after["prior_tax_paid"] == 5500
    assert (
        after["account_balances"]["saved_cash"] - before["account_balances"]["saved_cash"] == 1250
    )
    assert not after["funding_failure"]


def test_unknown_interest_penalty_or_compliance_cost_blocks_a_savings_conclusion():
    scenario = synthetic_refund()
    plan = scenario.foreign_tax_plan.model_copy(
        update=dict(redetermination_other_costs_complete_confirmed=False)
    )
    months = {
        r["date"]: r for r in project(scenario.model_copy(update=dict(foreign_tax_plan=plan)))
    }
    row = months["2027-06-01"]
    assert row["foreign_tax_refund_received"] == 7000
    assert row["prior_tax_paid"] == 5500
    assert row["foreign_return_revisions"]
    assert row["foreign_redetermination_unresolved"]
    assert row["funding_failure"]
