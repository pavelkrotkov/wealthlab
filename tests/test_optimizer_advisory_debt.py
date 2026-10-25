"""A genuinely unfunded modeled bill remains debt and cannot become completed-exit wealth."""

from copy import deepcopy
from decimal import Decimal

import pytest

from tests.optimizer_advisory_cases import case, selection
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.optimization.advisory_metrics import actual
from wealthlab.optimization.assessment import assess
from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicySearch


def test_actual_unfunded_common_bill_blocks_exit_and_retains_liability_once():
    data = case().model_dump(mode="json")
    schedule = data["household"]["advisory_fee_plan"]["schedules"][0]
    schedule.update(tiers=[dict(upper_limit=None, annual_rate="0")], fixed_per_period="350000")
    model = PolicySearch.model_validate(data)
    household, binding = compile_candidate(model, selection(model, 0, False))
    result = run(household, generate(model.training), binding)
    final = result["details"][0]["rows"][-1]
    metric = assess(model, household, result)
    # $253,999 before December spending pays the bill; no remaining assets or loan funds its gap.
    assert final["advisory_fees_paid"] == 253999
    assert final["fees_owed"] == final["advisory_fees_owed"] == 96001
    assert final["closing_cash"] == 0
    assert final["net_wealth"] == Decimal(-96001)
    assert metric["median_real_after_tax_exit_wealth"] is None
    assert metric["maximum_ending_advisory_fees_owed"] == 96001


def test_missing_actual_cost_observations_do_not_become_zero_fee_metrics():
    model = case()
    household, binding = compile_candidate(model, selection(model, 0, False))
    result = run(household, generate(model.training), binding)
    corrupted = deepcopy(result)
    corrupted["details"][0]["rows"][0].pop("advisory_fees_assessed")
    with pytest.raises(ValueError, match="unknown costs are not zero"):
        actual(corrupted)
