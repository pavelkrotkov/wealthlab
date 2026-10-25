"""Fund-only cash/tax facts require explicit exclusion from directly owned securities.

The policies share prices, not partnership tax identity. Reporting the difference
is necessary for a reviewer to distinguish a deliberate contract change from a
lost distribution, omitted tax event or ignored redemption request.
"""

import pytest
from exchange_fund_cases import change, flat

from wealthlab.products.exchange_fund_compare import compare


def fund_facts(data):
    mark = data["exchange_fund_plan"]["observations"][0]
    mark.update(distribution="1000", federal_basis_adjustment="500", nj_basis_adjustment="200")
    mark["allocation"]["federal"] = dict(interest="500")
    mark["allocation"]["new_jersey"] = dict(interest="200")


def test_nonzero_fund_facts_cannot_be_silently_ignored_in_paired_direct_ownership():
    case = change(flat(), fund_facts)
    with pytest.raises(ValueError, match="Confirm fund-specific"):
        compare(case)
    case = change(
        case,
        lambda d: d["exchange_fund_plan"].update(
            fund_specific_flows_excluded_from_direct_sale_confirmed=True
        ),
    )
    result = compare(case)
    direct = result["rows"]["direct_sale"][0]
    fund = result["rows"]["exchange"][0]
    assert direct["exchange_excluded_fund_distribution"] == 1000
    assert direct["exchange_excluded_fund_federal_basis_adjustment"] == 500
    assert direct["exchange_excluded_fund_nj_basis_adjustment"] == 200
    assert direct["exchange_excluded_fund_tax_allocation"] == 1
    assert direct["closing_cash"] == 30000
    assert fund["closing_cash"] == 31000
    assert result["fund_specific_exclusions_confirmed"]


def test_direct_redeem_acknowledges_existing_basket_and_never_invents_a_second_cash_receipt():
    result = compare(flat())
    direct = result["rows"]["direct_sale"][-1]
    fund = result["rows"]["exchange"][-1]
    assert direct["exchange_direct_basket_already_owned_requests"] == 1
    assert fund["exchange_direct_basket_already_owned_requests"] == 0
    assert direct["exchange_sale_cash"] == 100000
    assert fund["exchange_sale_cash"] == 100000
    assert direct["net_wealth"] == fund["net_wealth"]
