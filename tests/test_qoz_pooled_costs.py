"""A pooled corporation incurs one manager fee and one loan-interest charge.

The first 20% return and $1,000 costs leave $69k. Adding $50k produces $119k
NAV and a $119k loan at 2x. The next 10% asset mark adds $23,800; $1,190 each
of interest/management fee leaves $140,420 NAV and $121,380 financing debt.
"""

from decimal import Decimal

from qoz_pooled_cases import rising

from wealthlab.household.projection import project


def test_manager_fee_and_financing_belong_to_the_single_company_not_its_stock_lots():
    rows = project(rising(".12", ".12"))
    march = rows[-1]["qoz_audit"]["economic_log"][1]
    assert (march["manager_fee"], march["financing_cost"]) == (Decimal(1190), Decimal(1190))
    assert rows[2]["qoz_nav"] == Decimal(140420)
    assert rows[2]["qoz_internal_debt"] == Decimal(121380)
