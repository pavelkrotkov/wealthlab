"""Allocation bounds cannot override shared costs, cash permissions or target coverage."""

import pytest
from optimization_cases import flat
from optimization_diversification_cases import case

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicyChoice, PolicySearch
from wealthlab.optimization.search import search


@pytest.mark.parametrize("field", ["rebalances", "savings"])
def test_allocation_schedule_requires_an_actual_shared_lot_book(field):
    data = flat().model_dump(mode="json")
    data["household"]["lot_plan"] = None
    choice = PolicyChoice.model_validate(dict(id="choice", **{field: []}))
    with pytest.raises(ValueError, match="actual linked lots"):
        compile_candidate(PolicySearch.model_validate(data), [choice])


def test_saving_costs_are_shared_even_when_targets_differ():
    data = case().model_dump(mode="json")
    data["dimensions"][-1]["choices"][1]["savings"][0]["commission_per_trade"] = "0"
    with pytest.raises(ValueError, match="shared savings commission"):
        search(PolicySearch.model_validate(data))


def test_bad_allocation_sum_is_reported_as_unsupported_without_normalizing_weights():
    data = case().model_dump(mode="json")
    data["dimensions"][-1]["locked_choice"] = "balanced"
    data["dimensions"][-1]["choices"][1]["rebalances"][0]["target_weights"]["bond"] = ".6"
    result = search(PolicySearch.model_validate(data))
    assert result["selection"] is None
    assert "sum exactly to one" in result["candidates"][0]["unsupported_reason"]
