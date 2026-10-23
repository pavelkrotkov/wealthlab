"""Tax outcomes must not depend on whether one purchase is stored as one or two lots."""

from decimal import Decimal

import pytest
from test_nj_wash import nj_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def retained_case(split_purchase):
    payload = nj_case()
    payload["as_of"] = "2026-06-01"
    payload["trades"] = payload["trades"][:1]
    payload["trades"][0].update(quantity="50", selection="specific", lot_ids=["original"])
    payload["lots"][0].update(
        acquired="2026-05-15", federal_holding_start="2026-05-15", liquid_after="2026-05-15"
    )
    if split_purchase:
        payload["lots"][0].update(
            quantity="50", federal_basis="500", nj_basis="500", economic_basis="500"
        )
        payload["lots"].append(dict(payload["lots"][0], id="retained"))
    return payload


@pytest.mark.parametrize("split_purchase", [False, True])
def test_unsold_recent_shares_replace_loss_shares_even_with_same_lot_id(split_purchase):
    # May 15's purchase leaves 50 unsold shares after June 1's loss sale.
    # The remaining shares qualify as replacements under the same 30-day rule
    # whether an import gives the entire purchase one ID or splits it into two.
    result = run(LotCase.model_validate(retained_case(split_purchase)))
    sold = result["disposals"][0]
    assert sold["federal_wash_deferred"] == 125
    assert sold["nj_wash_deferred"] == 125
    assert sold["federal_recognized_gain"] == 0
    assert sum(Decimal(lot["federal_basis"]) for lot in result["lots"]) == 625
    assert sum(Decimal(lot["economic_basis"]) for lot in result["lots"]) == 500


def test_full_exit_releases_retained_share_deferral_once():
    # The final sale consumes the remaining shares; it cannot replace itself.
    # Two $125 economic losses become one $250 recognized loss at full exit.
    payload = retained_case(False)
    payload["trades"].append(dict(payload["trades"][0], id="exit", date="2026-06-02"))
    result = run(LotCase.model_validate(payload))
    first, last = result["disposals"]
    assert first["federal_recognized_gain"] == 0
    assert last["federal_recognized_gain"] == -250
    assert not result["lots"]
