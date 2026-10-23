"""Distinct valid long policy IDs must not become identical generated trades."""

import pytest
from test_harvest_comparison import harvest_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


@pytest.mark.parametrize("prefix_size", [60, 79])
def test_long_namespaced_policies_generate_unique_valid_order_ids(prefix_size):
    # Each policy sells half of the original position, using distinct IDs that
    # agree beyond the old 55-character truncation point. The longest case also
    # exercises digest IDs while retaining the input schema's 80-character cap.
    payload = harvest_case()
    policy = payload["harvest_policies"][0]
    policy.update(id="x" * prefix_size + "a", max_gross_sales="375")
    payload["harvest_policies"].append(dict(policy, id="x" * prefix_size + "b"))
    result = run(LotCase.model_validate(payload))
    ids = [trade["id"] for trade in result["executed_trades"]]
    assert len(set(ids)) == len(ids) == 4
    assert all(len(identity) <= 80 for identity in ids)
    assert [row["sold_units"] for row in result["harvest_decisions"]] == [50, 50]
