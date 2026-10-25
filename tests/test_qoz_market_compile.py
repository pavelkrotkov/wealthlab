"""Exact path compilation changes observations without rewriting source or contract economics."""

from decimal import Decimal

import pytest

from tests.qoz_market_cases import flat
from wealthlab.markets.household_compile import compile_marks
from wealthlab.markets.household_execution import Execution


def test_exact_path_replaces_returns_but_preserves_native_contract_and_dividends():
    case, batch, binding = flat(
        shocks=[dict(name="growth", month=1, mark_shocks=dict(qof_assets=0.1))]
    )
    plan = case.qoz_plan
    supplied = plan.observations[2].model_copy(update=dict(dividend_fraction_of_nav=Decimal(".1")))
    changed = plan.model_copy(
        update=dict(observations=[*plan.observations[:2], supplied, *plan.observations[3:]])
    )
    case = case.model_copy(update=dict(qoz_plan=changed))
    compiled = compile_marks(case, batch, binding, 0)
    original, actual = changed.model_dump(), compiled.qoz_plan.model_dump()
    original.pop("observations")
    actual.pop("observations")
    assert actual == original
    assert compiled.lot_plan.case.sale_policies == case.lot_plan.case.sale_policies
    assert compiled.qoz_plan.observations[1].asset_return == Decimal(
        str(batch.mark_returns[0, 1, 1])
    )
    assert compiled.qoz_plan.observations[2].dividend_fraction_of_nav == Decimal(".1")
    assert Execution(compiled, batch, binding, 0).scenario is compiled


def test_stale_return_or_missing_generated_lock_cannot_enter_direct_execution():
    case, batch, binding = flat(
        shocks=[dict(name="growth", month=1, mark_shocks=dict(qof_assets=0.1))]
    )
    with pytest.raises(ValueError, match="stale returns"):
        Execution(case, batch, binding, 0)
    case, batch, binding = flat(
        shocks=[dict(name="lock", month=11, lock_months=dict(qof_assets=1))]
    )
    with pytest.raises(ValueError, match="stale returns"):
        Execution(case, batch, binding, 0)
