"""Nondeductible basis and a zero-deposit policy agree with their tax and cash meaning."""

from decimal import Decimal

from tests.ira_deposit_household_cases import one_year
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.distribution_inputs import AccountReturn
from wealthlab.retirement.ira_deposit_household_example import synthetic


def test_funded_nondeductible_deposit_adds_federal_and_nj_basis():
    data = one_year().model_dump(mode="json")
    data["incomes"][0]["monthly_amount"] = "25000"
    context = data["ira_plan"]["contributions"]
    context["years"][0]["contributors"][0].update(
        covered_by_workplace_plan=True, traditional_ira_magi="300000", roth_ira_magi="300000"
    )
    context["orders"] = context["orders"][:1]
    row = project(Scenario.model_validate(data))[-1]
    owner = row["ira_annual_reconciliation"]["owners"][0]
    assert (owner["federal_ira_basis"], owner["nj_ira_basis"]) == (
        Decimal("2126.21"),
        Decimal("2126.21"),
    )
    assert row["ira_annual_reconciliation"]["contribution_owners"][0]["federal_ira_deduction"] == 0


def test_empty_deposit_policy_matches_fixed_ira_projection_including_returns():
    case = synthetic()
    deposits = case.ira_plan.contributions.model_copy(update=dict(orders=[]))
    event = AccountReturn(
        id="known_return",
        provenance="illustration",
        date="2026-02-01",
        account_id="retirement",
        rate=Decimal(".10"),
    )
    fixed = case.ira_plan.model_copy(update=dict(contributions=None, returns=[event]))
    dynamic = fixed.model_copy(update=dict(contributions=deposits))
    before = project(case.model_copy(update=dict(ira_plan=fixed)))
    after = project(case.model_copy(update=dict(ira_plan=dynamic)))
    assert after[-1]["account_balances"] == before[-1]["account_balances"]
    assert after[-1]["net_wealth"] == before[-1]["net_wealth"]
    assert [r["annual_tax"] for r in after] == [r["annual_tax"] for r in before]
