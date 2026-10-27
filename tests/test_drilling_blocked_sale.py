"""An infeasible full liquidation retains the unsold property and actual creditor exposure."""

from drilling_cases import change, short

from wealthlab.household.projection import project


def test_blocked_mid_horizon_exit_carries_unsold_property_production_and_claims():
    def edit(data):
        data["drilling_plan"]["observations"][0].update(
            exit_requested=True, exit_gross_proceeds="40000", liability_cost="500000"
        )

    first, last = project(change(short(2), edit))
    assert (first["drilling_creditor_payables"], last["drilling_creditor_payables"]) == (
        400000,
        399200,
    )
    assert (
        last["drilling_property_value"],
        last["drilling_production_receipts"],
        last["drilling_exit_cash"],
        last["closing_cash"],
    ) == (20000, 1000, 0, 0)
    assert (last["net_wealth"], last["drilling_blocked_exit"]) == (-379200, True)
    assert last["drilling_audit"]["months"][0]["exit_cash"] == 0
