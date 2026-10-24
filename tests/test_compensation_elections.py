"""Cash elections change liquidity/exposure, not the independently supplied income allocation."""

from decimal import Decimal

from wealthlab.employment.compensation_example import synthetic
from wealthlab.employment.compensation_stress import linked_shock
from wealthlab.household.projection import project


def test_retaining_distribution_preserves_value_but_changes_cash_and_employer_exposure():
    cash, retained = project(synthetic()), project(synthetic("retain"))
    assert cash[-1]["net_wealth"] == retained[-1]["net_wealth"] == 295980
    assert cash[-1]["closing_cash"] - retained[-1]["closing_cash"] == 20000
    assert retained[-1]["employer_vested"] - cash[-1]["employer_vested"] == 20000
    assert cash[11]["annual_tax"] == retained[11]["annual_tax"]


def test_joint_job_market_and_forfeiture_stress_is_dated_and_reproducible():
    case = linked_shock()
    rows = project(case)
    assert sum(r["income"] for r in rows) == 75000
    assert rows[9]["employer_vested"] == 21000
    assert rows[9]["employer_unvested_contingent"] == 0
    assert rows[11]["annual_tax"]["federal"]["agi"] == 95000
    assert rows[-1]["net_wealth"] == Decimal("204754.50")
    assert project(case) == rows


def test_elected_cash_can_avoid_assumed_unvested_forfeiture_without_tax_savings():
    cash = project(linked_shock())
    retained = project(linked_shock(synthetic("retain")))
    assert cash[11]["annual_tax"] == retained[11]["annual_tax"]
    assert cash[-1]["net_wealth"] - retained[-1]["net_wealth"] == 20000
