"""Observed prices change actual AUM fees; liquidity locks never erase the bill."""

from decimal import Decimal

from tests.advisory_cases import native, with_fee
from wealthlab.markets.household_run import run


def test_observed_price_shock_changes_the_fee_base_and_actual_household_cash():
    case, batch, binding = native(
        shocks=[dict(name="growth", month=0, mark_shocks=dict(source_stock=0.1))]
    )
    rows = run(with_fee(case), batch, binding)["details"][0]["rows"]
    assert rows[0]["advisory_fee_assessments"][0]["valuation_base"] == 110000
    assert rows[0]["advisory_fees_paid"] == Decimal("91.67")
    assert rows[-1]["net_wealth"] == Decimal("114908.33")


def test_allowed_native_sale_funds_the_assessed_fee_without_duplicate_cash_or_basis_changes():
    case, batch, binding = native(cash="0")
    rows = run(with_fee(case), batch, binding)["details"][0]["rows"]
    final = rows[-1]
    disposal = final["lot_audit"]["disposals"][0]
    # Microshare execution raises exactly $83.33. Actual gain uses original dual basis.
    assert disposal["proceeds"] == Decimal("83.33")
    assert (disposal["federal_gross_gain"], disposal["nj_gross_gain"]) == (
        Decimal("66.66"),
        Decimal("58.33"),
    )
    assert rows[0]["advisory_fees_paid"] == Decimal("83.33")
    assert final["net_wealth"] == Decimal("99916.67")
    assert final["annual_tax"]["total_liability"] == 0


def test_locked_source_leaves_real_assets_and_an_unpaid_fee_liability():
    case, batch, binding = native(
        cash="0", shocks=[dict(name="lock", month=0, lock_months=dict(source_stock=12))]
    )
    final = run(with_fee(case), batch, binding)["details"][0]["rows"][-1]
    assert final["advisory_fees_owed"] == final["fees_owed"] == Decimal("83.33")
    assert final["account_balances"]["brokerage"] == 100000
    assert final["lot_audit"]["disposals"] == []
    assert final["net_wealth"] == Decimal("99916.67")
