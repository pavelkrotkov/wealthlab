"""Common fees cover native sleeve and exchange menus without changing capital."""

import pytest

from tests.optimization_allocation_cases import case as sleeves
from tests.optimization_exchange_cases import case as exchange
from wealthlab.optimization.advisory_example import extend
from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.validation import validate


@pytest.mark.parametrize("build", [sleeves, exchange])
def test_common_source_coverage_validates_the_complete_native_strategy_menu(build):
    model = extend(build())
    assert validate(model) > 0
    selected = [d.choices[0] for d in model.dimensions]
    household, _ = compile_candidate(model, selected)
    assert household.advisory_fee_plan == model.household.advisory_fee_plan
    assert sum(a.balance for a in household.accounts) == sum(
        a.balance for a in model.household.accounts
    )
