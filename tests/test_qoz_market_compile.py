"""Exact path compilation changes observations without rewriting source or contract economics."""

import pytest

from tests.qoz_market_cases import flat
from wealthlab.markets.household_execution import Execution


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
