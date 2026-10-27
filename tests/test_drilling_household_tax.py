"""A real household pays accrued/settled tax; deductions never become invented receipts."""

from decimal import Decimal as D

from wealthlab.products.drilling_compare import compare
from wealthlab.products.drilling_example import synthetic
from wealthlab.products.drilling_reporting import annual_returns


def test_two_year_economics_include_actual_tax_not_headline_deduction_times_rate():
    result = compare(synthetic())
    drilling, liquid = (result["outcomes"][m] for m in ("drilling", "liquid_reference"))
    assert (drilling["call_funded"], drilling["distributions"]) == (100000, 58400)
    assert (drilling["actual_annual_tax_liability"], liquid["actual_annual_tax_liability"]) == (
        D("45413.93"),
        D("46135.00"),
    )
    assert drilling["conditional_after_tax_net_wealth"] < liquid["conditional_after_tax_net_wealth"]
    rows = result["rows"]["drilling"]
    assert (len(annual_returns(rows)), sum(r["tax_event_cash"] for r in rows)) == (2, 0)
    assert (drilling["unpaid_tax_position"], drilling["joint_funding_feasible"]) == (
        D("-9620.57"),
        True,
    )
    final = annual_returns(rows)["2027"]["federal"]["partnership"]
    assert (final["supplied_se_earnings_primary"], final["self_employment_tax"]) == (
        D("9600"),
        D("1356.44"),
    )


def test_allowed_deduction_does_not_make_failed_well_profitable_or_create_cash():
    result = compare(synthetic("poor_production"))
    drill, liquid = (result["outcomes"][m] for m in ("drilling", "liquid_reference"))
    assert (drill["distributions"], drill["product_value"]) == (0, 0)
    assert drill["conditional_after_tax_net_wealth"] < liquid["conditional_after_tax_net_wealth"]
    assert sum(r["tax_event_cash"] for r in result["rows"]["drilling"]) == 0
    assert not result["full_tax_optimization_supported"]
