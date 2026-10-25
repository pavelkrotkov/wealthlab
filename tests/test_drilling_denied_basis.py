"""Current deductibility and supplied outside-basis/at-risk effects are separate facts."""

import pytest
from drilling_cases import change, short

from wealthlab.household.calendar import months
from wealthlab.household.funding import Wallet
from wealthlab.products.drilling_example_terms import deduction, timing
from wealthlab.products.drilling_household import Ledger


def case(reduction):
    def configure(data):
        row = data["drilling_plan"]["observations"][0]
        item = deduction("nondeductible", "operating_loss", 100, "denied")
        item.update(
            federal_basis_reduction=str(reduction),
            nj_basis_reduction="0",
            at_risk_reduction="0",
            nj_timing=timing("denied"),
            basis_effect_source="Supplied conditional noncapital basis effect; NJ/at-risk zero",
        )
        row.update(
            idc_cost="0",
            tangible_cost="0",
            manager_fee="0",
            operating_cost="100",
            deductions=[item],
            residual_property_value="0",
            exit_requested=False,
        )

    return change(short(), configure)


@pytest.mark.parametrize("reduction,applied", [(0, 0), (100, 100), (500, 100)])
def test_denied_current_deduction_retains_its_supplied_actual_basis_effect(reduction, applied):
    scenario = case(reduction)
    ledger, wallet = Ledger(scenario), Wallet(scenario)
    events = ledger.after_receipts(wallet, *next(months(scenario.start, scenario.end)))
    assert sum(e.federal.allowed_nonpassive_partnership_income for e in events) == 0
    assert ledger.bases == dict(federal=100000 - applied, nj=100000, at_risk=100000)
    assert wallet.cash + ledger.cash == 199900
    effects = ledger.log[0]["deduction_audit"][0]["basis_effects"]
    assert effects["applied"] == dict(federal=applied, nj=0, at_risk=0)
    assert effects["requested"]["federal"] == reduction
    assert "Supplied conditional" in effects["source"]


def test_missing_independent_basis_effect_source_blocks_the_scenario():
    data = case(100).model_dump(mode="json")
    data["drilling_plan"]["observations"][0]["deductions"][0].pop("basis_effect_source")
    from wealthlab.household.scenario import Scenario

    with pytest.raises(ValueError, match="basis_effect_source"):
        Scenario.model_validate(data)
