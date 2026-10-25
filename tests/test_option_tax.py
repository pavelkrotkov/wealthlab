"""Conditional recognition is independently federal/NJ and never a cash receipt."""

from tests.option_cases import one_leg, parse
from wealthlab.products.option_engine import run


def test_unresolved_tax_status_does_not_become_zero_tax_or_an_allowed_loss():
    data = one_leg()
    data["tax"] = {}
    result = run(parse(data))
    assert all(r["recognized"] is None and r["unresolved"] for r in result["tax"])
    assert result["ending"]["cash"] == 11500


def test_supplied_federal_loss_deferral_does_not_force_nj_conformity_or_change_cash():
    data = one_leg()
    data["marks"][-1]["stock"] = "80"
    data["tax"].update(
        straddle="supplied_deferrals", federal_deferrals={"contract:2026-01-01": "300"}
    )
    result = run(parse(data))
    fed, nj = result["tax"]
    assert fed["recognized"] == -200 and fed["deferred"] == 300
    assert nj["recognized"] == -500 and nj["deferred"] == 0
    assert result["ending"]["cash"] == 9500
