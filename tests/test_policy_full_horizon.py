"""A full younger-spouse horizon reconciles independent cash without waiving safety targets.

The synthetic youngest member is born1977-01-01. Full age100 therefore ends at
2078-01-01:624monthly expenses. With2.1million capital, zero wages/returns/taxes,
and full stock basis, actual final cash must be2100000-1248000-1=851999.
"""

from datetime import date
from types import SimpleNamespace

import pytest

from wealthlab.markets.household_report import target_end
from wealthlab.optimization.horizon_example import complete_year, synthetic
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search
from wealthlab.optimization.validation import validate


def flat():
    data = synthetic(wages=0).model_dump(mode="json")
    data["dimensions"][0]["locked_choice"] = "early"
    for name in ("training", "validation"):
        market = data[name]
        market.update(paths=1, expected_annual_inflation=0, annual_inflation_volatility=0)
        market["assets"][0].update(
            expected_annual_mark_return=0, annual_volatility=0, annual_cash_yield=0
        )
    for lot in data["household"]["lot_plan"]["case"]["lots"]:
        lot["federal_basis"] = lot["nj_basis"] = str(int(lot["quantity"]) * 100)
    return PolicySearch.model_validate(data)


@pytest.fixture(scope="module")
def result():
    return search(flat())


def test_full_horizon_reaches_younger_age100_and_closes_all52_tax_years_in_actual_cash(result):
    candidate = result["candidates"][0]
    assert candidate["median_real_after_tax_exit_wealth"] == 851999
    rows = result["selected_training"]["details"][0]["rows"]
    assert len(rows) == 624
    assert rows[-1]["closing_cash"] == 851999
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == 851999


def test_completed_example_retains_all_safety_constraints_and_small_sample_uncertainty(result):
    assert result["status"] == "best_evaluated_candidate"
    assert result["held_out"]["assessment"]["eligible"]
    candidate = result["candidates"][0]
    assert all(candidate["constraints"].values())
    assert candidate["joint_success_95_wilson"][0] < 0.95


def test_synthetic_form_values_propagate_through_complete_income_expense_and_tax_schedules():
    case = synthetic(cash=123456, wages=7654, spending=2345)
    assert case.household.end == date(2078, 1, 1)
    assert case.household.accounts[0].balance == 123456
    assert case.household.incomes[0].monthly_amount == 7654
    assert case.household.expenses[0].monthly_amount == 2345
    assert case.household.incomes[0].end == case.household.expenses[0].end == case.household.end


def test_all_future_rule_years_and_default_targets_are_explicit():
    case = synthetic()
    assert case.household.tax_plan is not None
    assert len(case.household.tax_plan.cases) == 52
    assert all(c.policy.mode == "freeze_2025" for c in case.household.tax_plan.cases)
    assert case.targets.target_age == 100 and case.targets.success_fraction == 0.95
    assert case.targets.reserve_years == 2 and case.targets.maximum_issuer_weight == 1
    assert validate(case) == 2


@pytest.mark.parametrize(
    "born,required,end",
    [
        (date(1977, 1, 1), date(2078, 1, 1), date(2078, 1, 1)),
        (date(1980, 2, 29), date(2081, 2, 28), date(2082, 1, 1)),
        (date(1977, 7, 4), date(2078, 7, 4), date(2079, 1, 1)),
    ],
)
def test_youngest_whole_age_year_and_complete_tax_year_boundaries(born, required, end):
    scenario = SimpleNamespace(
        target_age=100,
        members=[SimpleNamespace(birth_date=date(1970, 1, 1)), SimpleNamespace(birth_date=born)],
    )
    assert target_end(scenario) == required
    assert complete_year(required) == end


def test_unsupported_native_ages_do_not_silently_drop_years_or_change_the_requested_target():
    with pytest.raises(ValueError, match="less than or equal to 120"):
        synthetic(target_age=120)
