"""Outer fees observe current native equity without rewriting product books.

The native account value already reflects embedded financing or manager costs.
An outer adviser bill is paid from actual household cash and cannot acquire new
stock basis, erase an unvested entitlement or change investor return character.
"""

from decimal import Decimal

from tests.advisory_cases import with_fee
from wealthlab.employment.compensation_example import synthetic as employer
from wealthlab.household.projection import project
from wealthlab.products.exchange_fund_example import synthetic as exchange
from wealthlab.products.option_household_example import synthetic as options


def test_option_advisory_bill_uses_actual_net_book_equity_and_preserves_delivery_basis():
    case = options()
    baseline = project(case)
    rows = project(with_fee(case, account=case.option_plan.account_id))
    bill = rows[0]["advisory_fee_assessments"][0]
    base = baseline[0]["account_balances"][case.option_plan.account_id]
    assert bill["valuation_base"] == base
    assert bill["assessed"] == (base * Decimal(".01") * 30 / 360).quantize(Decimal(".01"))
    assert rows[-1]["option_lots"] == baseline[-1]["option_lots"]
    assert rows[-1]["option_tax_audit"] == baseline[-1]["option_tax_audit"]


def test_employer_fee_base_excludes_actual_contingent_unvested_rights():
    case = employer()
    row = project(with_fee(case, account="employer_fund"))[0]
    bill = row["advisory_fee_assessments"][0]
    assert bill["valuation_base"] == row["employer_vested"] == 20000
    assert row["employer_unvested_contingent"] == 90000
    assert row["advisory_fees_paid"] == Decimal("16.67")


def test_exchange_outer_charge_is_separate_from_actual_manager_fee_and_investor_basis():
    case = exchange()
    baseline = project(case)
    rows = project(with_fee(case, account="exchange"))
    base = baseline[0]["account_balances"]["exchange"]
    assert rows[0]["advisory_fee_assessments"][0]["valuation_base"] == base
    assert rows[0]["account_balances"]["exchange"] == base
    assert rows[-1]["exchange_fund_audit"] == baseline[-1]["exchange_fund_audit"]
    assert rows[-1]["net_wealth"] == baseline[-1]["net_wealth"] - rows[0]["advisory_fees_paid"]
