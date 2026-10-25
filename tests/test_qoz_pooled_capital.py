"""All stock lots share one corporation, including creditors and later subscriptions.

A $50k equity call at 2x owns $100k assets and owes $50k. Losing all assets
leaves the company owing $50k, with no shareholder recourse. Another $50k
cash call cures that debt to zero; it cannot create a fresh $50k NAV book.
"""

from decimal import Decimal

import pytest
from qoz_pooled_cases import distressed

from wealthlab.household.projection import project


def test_new_cash_cures_existing_entity_creditors_without_creating_another_nav_book():
    rows = project(distressed())
    february = rows[1]
    assert february["qoz_call_paid"] == Decimal(50000)
    assert february["qoz_internal_debt"] == 0
    assert february["qoz_nav"] == 0
    assert february["closing_cash"] == february["net_wealth"] == Decimal(5000)
    ending = rows[-1]["qoz_audit"]["ending_entity"]
    assert ending["loan"] == 0


def test_no_new_call_leaves_creditor_debt_inside_the_company_without_investor_recourse():
    rows = project(distressed(second_call=False))
    assert rows[1]["qoz_internal_debt"] == Decimal(50000)
    assert rows[1]["qoz_nav"] == 0
    assert rows[1]["closing_cash"] == rows[1]["net_wealth"] == Decimal(55000)


def test_distressed_stock_issuance_requires_explicit_terms():
    with pytest.raises(ValueError, match="explicit stock issuance terms"):
        project(distressed(confirmed=False))
