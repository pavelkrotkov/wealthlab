"""Source-matched retirement forfeits or vests real contingent value through one wallet.

Early:320000opening wealth-48000spending=272000. Later adds60000 actual
wages and80000 vested contingency, less8535+10384 actual taxes:393081.
The former is not allowed to receive the latter's source-supplied vesting.
"""

import pytest
from optimization_employment_cases import flat

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(flat())


def test_native_early_and_later_policies_preserve_capital_and_settle_actual_tax(result):
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        272000,
        393081,
    ]
    assert [c["median_net_cash_tax"] for c in result["candidates"]] == [0, 18919]
    assert all(c["eligible"] for c in result["candidates"])
    assert result["selection"] == "candidate_1"
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 393081
    assert result["configured_validation_passed"]


def test_later_vesting_is_not_opening_capital_or_a_second_distribution(result):
    rows = result["selected_training"]["details"][0]["rows"]
    assert sum(row["income"] for row in rows) == 60000
    assert sum(row["employer_distribution_cash"] for row in rows) == 100000
    assert rows[-1]["account_balances"]["employer_fund"] == 0
    assert rows[-1]["tax_refund_receivable"] == rows[-1]["tax_owed"] == 0
    evidence = rows[-1]["employer_tranches"][0]["exit_evidence"]
    assert evidence["forfeited_value"] == 0 and evidence["contractual_exit_proven"]
    assert rows[11]["annual_tax"]["total_liability"] == 8535
    assert rows[-1]["annual_tax"]["total_liability"] == 10384


def test_early_retirement_uses_forfeiture_and_has_no_later_vesting_cash():
    data = flat().model_dump(mode="json")
    data["dimensions"][0]["locked_choice"] = "early"
    result = search(PolicySearch.model_validate(data))
    rows = result["selected_training"]["details"][0]["rows"]
    assert sum(row["income"] for row in rows) == 0
    assert sum(row["employer_distribution_cash"] for row in rows) == 20000
    evidence = rows[-1]["employer_tranches"][0]["exit_evidence"]
    assert evidence["forfeited_value"] == 80000 and evidence["contractual_exit_proven"]
    assert not any(event["kind"] == "vest" for event in rows[-1]["employer_event_log"])


def test_native_plan_preparation_preserves_original_wealth_and_compiled_tax_facts():
    case = flat()
    for choice in case.dimensions[0].choices:
        household, _ = compile_candidate(case, [choice])
        assert household.accounts == case.household.accounts
        assert household.incomes == case.household.incomes
        assert household.tax_plan == case.household.tax_plan
        assert household.lot_plan == case.household.lot_plan
        assert household.compensation_plan.tranches == case.household.compensation_plan.tranches


def test_retirement_cutoffs_also_support_source_profiles_without_explicit_wage_paths():
    data = flat().model_dump(mode="json")
    data["household"]["employment_plan"] = None
    for offer in data["employment_offers"]:
        offer["employment_plan"] = None
    result = search(PolicySearch.model_validate(data))
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        272000,
        393081,
    ]


def test_blocked_later_employer_redemption_cannot_outrank_completed_early_cash():
    data = flat().model_dump(mode="json")
    data["training"].update(
        mode="stress",
        stress_base="deterministic",
        shocks=[
            dict(
                name="Actual retirement-date employer liquidity lock",
                month=12,
                lock_months=dict(employer=1),
            )
        ],
    )
    result = search(PolicySearch.model_validate(data))
    later = result["candidates"][1]
    assert later["median_real_after_tax_exit_wealth"] is None
    assert not later["constraints"]["completed_after_tax_exit"]
    assert result["selection"] == "candidate_0"
