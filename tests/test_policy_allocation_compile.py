"""Opening purchases conserve original wealth and never spend future wages or tax credits.

A two-unit sleeve costs20000of current cash. An inactive offer has no capital,
contractual obligation or tax allocation in the actual candidate; the validated
unit template remains available for a later unlocked choice.
"""

from decimal import Decimal

import pytest
from optimization_allocation_cases import case
from optimization_cases import changed

from wealthlab.household.funding import opening_wealth
from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.validation import validate


def selected(profile, index):
    return [profile.dimensions[0].choices[0], profile.dimensions[1].choices[index]]


@pytest.mark.parametrize("index,amount", [(0, 0), (1, 20000), (2, 20000), (3, 20000)])
def test_actual_opening_cash_and_new_account_capital_reconcile(index, amount):
    profile = case()
    before = profile.model_dump_json()
    household, binding = compile_candidate(profile, selected(profile, index))
    accounts = {a.id: a for a in household.accounts}
    assert accounts["cash"].balance == 200000 - amount
    assert accounts["brokerage"] == profile.household.accounts[1]
    assert sum(a.balance for a in household.accounts if a.id.startswith("new_")) == amount
    assert opening_wealth(household) == opening_wealth(profile.household) == 300000
    assert len(binding.sleeves) == (2 if index == 3 else int(bool(amount)))
    assert profile.model_dump_json() == before


def test_over_budget_mix_fails_instead_of_using_forecast_payroll_or_a_negative_cash_balance():
    profile = changed(case(), lambda d: d["household"]["accounts"][0].update(balance="19999"))
    with pytest.raises(ValueError, match="available source cash"):
        compile_candidate(profile, selected(profile, 3))


def test_unit_scaling_changes_only_supplied_money_not_rates_dates_or_tax_eligibility():
    profile = case()
    household, _ = compile_candidate(profile, selected(profile, 2))
    source = profile.sleeve_opportunities[1].unit
    actual = household.sleeve_plan.sleeves[0]
    assert actual.case.opening_equity == Decimal(2) * source.case.opening_equity
    assert actual.case.annual_manager_fee == source.case.annual_manager_fee
    assert actual.observations == source.observations
    contract = actual.private_fund_contract
    assert contract.federal_opening_basis == contract.new_jersey_opening_basis == 20000
    assert contract.requests == source.private_fund_contract.requests
    assert contract.federal_exit_loss == source.private_fund_contract.federal_exit_loss


def test_distinct_opportunity_dimensions_can_be_locked_independently():
    data = case().model_dump(mode="json")
    data["dimensions"] = [
        data["dimensions"][0],
        *[
            dict(
                id=identity,
                choices=[
                    dict(id="none", sleeve_units={identity: 0}),
                    dict(id="one", sleeve_units={identity: 1}),
                ],
                locked_choice="one",
            )
            for identity in ("new_margin", "new_private")
        ],
    ]
    from wealthlab.optimization.inputs import PolicySearch

    assert validate(PolicySearch.model_validate(data)) == 1
