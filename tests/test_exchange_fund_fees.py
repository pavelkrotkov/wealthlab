"""Economic fees and independent allocations conserve capital without invented deductions.

Fees are real NAV reductions. K-1 income, cash distributions and basis changes
are independent supplied facts, so no fee automatically creates a deduction.
"""

from decimal import Decimal

from exchange_fund_cases import change, flat

from wealthlab.household.projection import project


def test_fee_drag_reduces_value_without_inventing_a_tax_deduction_or_new_basis():
    def configure(data):
        data["exchange_fund_plan"].update(annual_fee="0.12", requests=[])

    rows = project(change(flat(), configure))
    fees = sum(r["exchange_fees"] for r in rows)
    assert rows[-1]["exchange_locked_value"] == Decimal("88638.48")
    assert fees == Decimal("11361.52")
    assert rows[-1]["net_wealth"] == 130000 - fees
    assert rows[-1]["exchange_federal_interest_basis"] == 20000
    assert rows[-1]["exchange_nj_interest_basis"] == 30000
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 0


def test_cash_distribution_and_non_cash_income_change_basis_and_cash_separately():
    def configure(data):
        plan = data["exchange_fund_plan"]
        plan["requests"] = []
        mark = plan["observations"][0]
        mark.update(distribution="1000", federal_basis_adjustment="500", nj_basis_adjustment="200")
        mark["allocation"]["federal"] = dict(interest="500")
        mark["allocation"]["new_jersey"] = dict(interest="200")

    rows = project(change(flat(), configure))
    assert rows[0]["closing_cash"] == 31000
    assert rows[0]["exchange_locked_value"] == 99000
    assert rows[-1]["exchange_federal_interest_basis"] == 19500
    assert rows[-1]["exchange_nj_interest_basis"] == 29200
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 500
    assert sum(r["tax_event_cash"] for r in rows) == 0
