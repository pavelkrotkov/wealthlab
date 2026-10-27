"""Actual native option/life gains and common fees reconcile to original household capital."""

from decimal import Decimal

import pytest

from tests.optimizer_advisory_cases import case, selection
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.optimization.compile import compile_candidate


@pytest.mark.parametrize(
    "units, policy, fee, ending",
    [
        (0, False, "2539.99", "249459.01"),
        (1, False, "2544.95", "249950.05"),
        (2, False, "2549.91", "250441.09"),
        (0, True, "2540.99", "249558.01"),
        (1, True, "2545.95", "250049.05"),
        (2, True, "2550.91", "250540.09"),
    ],
)
def test_actual_cash_and_basis_preserve_capital_with_common_source_fees(units, policy, fee, ending):
    model = case()
    household, binding = compile_candidate(model, selection(model, units, policy))
    result = run(household, generate(model.training), binding)
    final = result["details"][0]["rows"][-1]
    # $300k -$48k spending -$1 stock commission +$496/unit +$100 supplied life gain -fee.
    assert final["closing_cash"] == final["net_wealth"] == Decimal(ending)
    assert final["advisory_fees_paid"] == final["advisory_fees_assessed"] == Decimal(fee)
    assert final["fees_owed"] == final["advisory_fees_owed"] == 0
    assert final["annual_tax"]["total_liability"] == 0
    assert household.advisory_fee_plan == model.household.advisory_fee_plan
    assert sum(a.balance for a in household.accounts) == 300000
