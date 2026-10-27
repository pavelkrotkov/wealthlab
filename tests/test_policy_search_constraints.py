"""The default horizon, blocked exits and missing issuer inventory cannot win on wealth."""

from decimal import Decimal

from optimization_cases import changed, flat

from wealthlab.optimization.assessment import concentration
from wealthlab.optimization.search import search


def test_default_age100_target_rejects_profitable_short_horizon():
    case = changed(flat(), lambda d: d["targets"].update(target_age=100))
    result = search(case)
    assert result["selection"] is None
    assert result["held_out"] is None
    assert all("target_age_horizon" in c["unmet_constraints"] for c in result["candidates"])


def test_retained_shares_are_marks_and_do_not_become_after_tax_exit_wealth():
    case = changed(flat(), lambda d: d["household"]["lot_plan"]["case"].update(sale_policies=[]))
    result = search(case)
    assert result["selection"] is None
    assert all(c["median_real_after_tax_exit_wealth"] is None for c in result["candidates"])


def test_unknown_issuer_inventory_cannot_satisfy_an_enabled_limit():
    rows = [dict(issuer_concentration_complete=False, max_security_weight=None)]
    assert not concentration(Decimal(1), rows)
    assert concentration(None, rows)


def test_unconfigured_conversion_choice_is_visible_without_favorable_fallback():
    from wealthlab.optimization.inputs import Dimension

    case = flat().model_copy(
        update=dict(
            dimensions=[
                Dimension.model_validate(
                    dict(id="invalid_ira", choices=[dict(id="missing", ira_orders=[])])
                )
            ]
        )
    )
    result = search(case)
    assert result["selection"] is None
    assert "existing configured IRA" in result["candidates"][0]["unsupported_reason"]
