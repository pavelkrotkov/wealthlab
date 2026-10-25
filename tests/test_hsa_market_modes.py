"""All four path generators feed the actual HSA book with causal monthly prices."""

from datetime import timedelta
from decimal import Decimal

import pytest

from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_run import run
from wealthlab.markets.hsa_example import synthetic
from wealthlab.markets.paths import generate


@pytest.mark.parametrize("mode", ["deterministic", "historical", "monte_carlo", "stress"])
def test_hsa_path_compiles_original_prices_and_runs_one_realized_path(mode):
    household, market, binding = synthetic(mode)
    original = household.model_dump(mode="json")
    batch = generate(market)
    case = compile_marks(household, batch, binding, 0)
    result = run(household, batch, binding, [0])
    rows = result["details"][0]["rows"]
    audit = rows[-1]["hsa_audit"]["investments"]
    check_price(case, audit)
    assert household.model_dump(mode="json") == original
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 0
    assert len(result["outcomes"]) == 1
    assert batch.metadata["batch_id"] == result["batch_id"]


def check_price(case, audit):
    # The Dec 15 provider cannot see the Dec 31 quote.
    prior = next(m for m in case.hsa_plan.investments.marks if m.date.month == 11)
    assert Decimal(audit["executed_trades"][0]["price"]) == prior.prices["fund"]
    assert case.hsa_plan.investments.marks[-1].date == case.end - timedelta(days=1)
