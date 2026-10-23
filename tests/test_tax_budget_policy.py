"""Sales obey cumulative filing-unit tax budgets rather than a flat capital-gain rate."""

from decimal import Decimal as D

import pytest
from test_lot_tax_reporting import forecast
from test_sale_policies import case_with, decision

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run


def budget_case(budget="500"):
    payload = case_with(decision("tax_budget", None, tax_budget=budget, budget_grid_points=8))
    payload.update(
        federal_wash_tracking=True,
        opening_wash_context_complete=True,
        nj_wash_treatment="federal_rules",
        lot_tax_cases=[forecast()],
    )
    payload["trades"] = []
    return payload


def test_sale_fits_actual_federal_and_nj_budget_without_paying_tax_twice():
    """Separate bases imply $50 federal and $40 NJ gain per share at a $100 price.

    A $500 combined budget permits roughly 49.76 shares, not $500 / one rate.
    The tax report is a liability comparison; it must not subtract tax from cash.
    """
    result = run(LotCase.model_validate(budget_case()))
    row = result["sale_decisions"][0]
    assert D("49.7") < row["sold_units"] < D("49.9")
    assert D("499.9") <= row["estimated_incremental_liability"] <= 500
    assert row["budget_met"]
    assert result["annual_tax_comparison"][0]["incremental_liability"] <= 500
    assert result["gross_wealth"] == 11000
    assert result["closing_cash"] == D(1000) + (row["sold_units"] * 100).quantize(D("0.01"))


def test_second_policy_cannot_spend_the_same_annual_budget_again():
    payload = budget_case()
    payload["sale_policies"].append(
        dict(payload["sale_policies"][0], id="second", date="2026-08-01")
    )
    result = run(LotCase.model_validate(payload))
    assert result["sale_decisions"][1]["sold_units"] < D("0.001")
    assert result["annual_tax_comparison"][0]["incremental_liability"] <= 500


@pytest.mark.parametrize("budget,expected", [("0", False), ("2000", True)])
def test_zero_or_nonbinding_budget_is_reported(budget, expected):
    result = run(LotCase.model_validate(budget_case(budget)))
    row = result["sale_decisions"][0]
    assert (row["sold_units"] == 100) is expected
    assert row["budget_met"]


def test_already_exceeded_budget_does_not_claim_no_sale_fixes_it():
    payload = budget_case("1")
    sale = dict(
        id="manual",
        provenance="assumption",
        date="2026-06-01",
        action="sell",
        account_id="brokerage",
        security_id="STOCK",
        quantity="25",
        price="100",
        commission="0",
    )
    payload["trades"] = [sale]
    row = run(LotCase.model_validate(payload))["sale_decisions"][0]
    assert row["sold_units"] == 0
    assert not row["budget_met"]
    assert row["estimated_incremental_liability"] > 1


def test_budget_requires_forecasts_and_cannot_be_attached_to_another_mode():
    payload = budget_case()
    payload["lot_tax_cases"] = []
    with pytest.raises(ValueError, match="require annual"):
        run(LotCase.model_validate(payload))
    payload["sale_policies"][0]["mode"] = "retain"
    with pytest.raises(ValueError, match="Supply tax_budget"):
        LotCase.model_validate(payload)


def test_future_manual_sale_cannot_influence_or_be_guaranteed_by_current_budget():
    payload = budget_case()
    before = run(LotCase.model_validate(payload))["sale_decisions"][0]
    payload["trades"] = [
        dict(
            id="future",
            provenance="assumption",
            date="2026-09-01",
            action="sell",
            account_id="brokerage",
            security_id="STOCK",
            quantity="25",
            price="200",
            commission="0",
        )
    ]
    result = run(LotCase.model_validate(payload))
    assert result["sale_decisions"][0] == before
    assert result["annual_tax_comparison"][0]["incremental_liability"] > 500
