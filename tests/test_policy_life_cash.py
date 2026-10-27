"""An actual1000premium and supplied900value increase cost100, never create free cash.

All paths share310000opening wealth,48000living expenses and1broker commission.
Independent final cash is261999,261899or261799, including returned policy basis.
Policy inputs carry matching values; the optimizer never scales an illustration.
"""

import pytest
from optimization_cases import changed
from optimization_life_cases import case

from wealthlab.markets.paths import generate
from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.search import evaluate, search


@pytest.fixture(scope="module")
def result():
    return search(case())


def test_supplied_funding_paths_conserve_capital_and_rank_actual_after_tax_cash(result):
    candidates = result["candidates"]
    assert [r["median_real_after_tax_exit_wealth"] for r in candidates] == [261999, 261899, 261799]
    assert all(r["eligible"] for r in candidates)
    assert result["selection"] == "candidate_0"
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 261999
    assert all(
        r["opening_allocation_audit"]["allocated_opening_wealth"] == 310000 for r in candidates
    )


def test_selected_premiums_use_native_basis_cash_and_final_surrender_once():
    profile = changed(case(), lambda d: d["dimensions"][1].update(locked_choice="two_premiums"))
    report = search(profile)
    rows = report["selected_training"]["details"][0]["rows"]
    assert sum(r["life_premiums_paid"] for r in rows) == 2000
    assert sum(r["life_cash_received"] for r in rows) == 11800
    exit_row = rows[-1]["life_policy_audit"]["executed"][-1]
    assert exit_row["federal_basis_before"] == 12000
    assert exit_row["federal_ordinary_income"] == 0
    assert exit_row["closed"] and rows[-1]["closing_cash"] == 261799


def test_choice_replaces_one_complete_path_and_preserves_shared_accounts_and_insurance_need():
    profile = case()
    before = profile.model_dump_json()
    choices = [d.choices[0] for d in profile.dimensions]
    household, _ = compile_candidate(profile, choices)
    assert household.accounts == profile.household.accounts
    assert household.tax_plan == profile.household.tax_plan
    assert household.life_plan is not None and profile.household.life_plan is not None
    assert (
        household.life_plan.insurance_need_by_owner
        == profile.household.life_plan.insurance_need_by_owner
    )
    assert household.life_plan.holdings[0] == profile.life_opportunities[0].holding
    assert before == profile.model_dump_json()


def test_unpaid_premium_cannot_rank_as_safe_even_when_failure_surrender_pays_the_bills():
    def edit(data):
        data["household"]["accounts"][0]["balance"] = "600"
        data["targets"]["reserve_years"] = 0

    profile = changed(case(), edit)
    choices = [profile.dimensions[0].choices[0], profile.dimensions[1].choices[2]]
    candidate, report = evaluate(profile, choices, 0, generate(profile.training))
    assert report is not None
    outcome = report["outcomes"][0]
    assert outcome["life_payment_failure_months"] == 1
    assert not candidate["constraints"]["spending_and_product_safety"]
    rows = report["details"][0]["rows"]
    assert rows[0]["life_payment_unfunded"] == 1000
    assert sum(r["life_cash_received"] for r in rows) == 10000
