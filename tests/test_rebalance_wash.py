"""A later rebalance repurchase can actually undo an earlier tax loss."""

from decimal import Decimal

from rebalance_cases import payload

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_repurchase_defers_federal_loss_without_inventing_nj_adjustment():
    data = payload()
    linked = data["lot_plan"]
    linked["case"]["lots"][0].update(federal_basis="2000", nj_basis="2000")
    linked["rebalances"].append(
        dict(
            linked["rebalances"][0],
            id="repurchase",
            date="2026-02-28",
            target_weights=dict(stock="1", bond="0"),
        )
    )
    rows = project(Scenario.model_validate(data))
    audit = rows[-1]["lot_audit"]
    replacement = next(lot for lot in audit["lots"] if lot["id"] == "repurchase_buy_stock")
    assert Decimal(replacement["federal_basis"]) == 1000
    assert Decimal(replacement["nj_basis"]) == 500
    assert rows[-1]["net_wealth"] == 2000
    assert sum(row["tax_refund_received"] for row in rows) == 0
