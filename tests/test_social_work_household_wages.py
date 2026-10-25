"""Earned payroll, retirement choices and current net benefits share annual tax recognition."""

from decimal import Decimal as D

from social_work_household_cases import case, completed, payload

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_actual_wage_streams_keep_claims_out_of_cash_and_receipt_year_tax():
    scenario = case()
    rows = project(scenario)
    assert rows[11]["social_security_government_receivable"] == 491
    assert rows[11]["social_security_net_cash"] == 562
    assert rows[16]["social_security_net_cash"] == 1053
    assert completed(rows, 2026)["federal"]["taxable_social_security"] == D("1405.00")
    assert scenario.social_work_plan.years[0].actual_monthly_wages is None


def test_household_retirement_change_reconciles_later_without_rewriting_prior_checks():
    scenario = case()
    original = project(scenario)
    data = payload()
    data["members"][0]["retirement_date"] = "2026-07-01"
    changed = project(Scenario.model_validate(data))
    assert changed[0]["social_security_net_cash"] == original[0]["social_security_net_cash"]
    assert changed[11]["social_security_government_receivable"] == 3372
    assert changed[16]["social_security_refund_cash"] == 3372
    assert completed(changed, 2026)["federal"]["taxable_social_security"] == 0


def test_unearned_interest_changes_tax_without_becoming_work_test_earnings():
    data = payload()
    data["incomes"].append(
        dict(
            data["incomes"][0],
            id="interest",
            monthly_amount=10000,
            start="2026-01-01",
            end="2027-01-01",
            stop_at_retirement=False,
        )
    )
    data["tax_plan"]["income_rules"].append(
        dict(income_id="interest", federal="interest", new_jersey="interest")
    )
    rows = project(Scenario.model_validate(data))
    assert rows[11]["social_security_government_receivable"] == 491
    assert completed(rows, 2026)["federal"]["taxable_social_security"] == D("2388.50")
