"""Reject missing mappings and silent reinvestment assumptions before path execution."""

import pytest

from tests.market_household_cases import flat
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate


@pytest.mark.parametrize(
    "updates, message",
    [
        (dict(securities=[]), "every linked security"),
        (dict(ordinary_cash_character_confirmed=False), "Confirm ordinary yield"),
        (dict(inflation_expenses=["missing"]), "expense IDs"),
    ],
)
def test_explicit_binding_guards(updates, message):
    case, market, binding = flat()
    with pytest.raises(ValueError, match=message):
        run(case, generate(market), binding.model_copy(update=updates))


def test_total_return_cannot_hide_taxable_reinvested_distributions():
    case, market, binding = flat(cash_yield=0)
    market = market.model_copy(update=dict(return_convention="total_return_reinvested"))
    with pytest.raises(ValueError, match="separate price returns"):
        run(case, generate(market), binding)


@pytest.mark.parametrize("indices", [[], [0, 0], [-1], [1]])
def test_requested_path_indices_must_exist_and_be_unique(indices):
    case, market, binding = flat()
    with pytest.raises(ValueError, match=r"path indices|Path index"):
        run(case, generate(market), binding, indices=indices)


def test_duplicate_mapping_cannot_duplicate_economic_returns():
    case, market, binding = flat()
    duplicate = binding.model_copy(update=dict(securities=binding.securities * 2))
    with pytest.raises(ValueError, match="every linked security"):
        run(case, generate(market), duplicate)


def test_market_inflation_cannot_double_count_entered_expense_growth():
    from tests.test_market_household_inflation import spending_case

    case, market, binding = spending_case()
    expense = case.expenses[0].model_copy(update=dict(annual_growth=0.025))
    with pytest.raises(ValueError, match="zero separate annual growth"):
        run(case.model_copy(update=dict(expenses=[expense])), generate(market), binding)
