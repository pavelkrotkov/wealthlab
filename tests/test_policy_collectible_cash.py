"""An independent frozen-law cash identity includes collectible gains and separate NJ basis.

The expected amount comes from published worksheet arithmetic, never a native
return result. Actual sale proceeds, disposed bases, recognition dates and paid
cash must agree: an attractive marked value alone cannot establish an exit.
"""

from decimal import Decimal as D

import pytest
from optimization_collectible_cases import expected_cash, flat

from wealthlab.optimization.compile import compile_candidate
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search


@pytest.fixture(scope="module")
def result():
    return search(flat())


def test_actual_cash_reconciles_both_sale_dates_with_no_free_capital(result):
    assert expected_cash() == D("1039645.61")
    assert [c["median_real_after_tax_exit_wealth"] for c in result["candidates"]] == [
        expected_cash(),
        expected_cash(),
    ]
    assert all(c["eligible"] for c in result["candidates"])
    assert result["configured_validation_passed"]
    assert result["held_out"]["assessment"]["median_real_after_tax_exit_wealth"] == expected_cash()


def test_native_audit_preserves_independent_bases_and_collectible_character(result):
    rows = result["selected_training"]["details"][0]["rows"]
    audit = rows[-1]["lot_audit"]
    disposals = audit["disposals"]
    assert sum(r["proceeds"] for r in disposals) == 99999
    assert sum(r["federal_basis"] for r in disposals) == 58000
    assert sum(r["nj_basis"] for r in disposals) == 54000
    federal, state = audit["recognized_by_year"][2026]
    assert federal["long_term"] == federal["collectibles_component"] == 41999
    assert state == 45999 and not audit["lots"]
    assert all(row["market_cash_yield"] == row["tax_owed"] == 0 for row in rows)


def test_sale_choices_only_change_policy_and_do_not_retitle_or_rebase_assets():
    case = flat()
    for choice in case.dimensions[0].choices:
        household, binding = compile_candidate(case, [choice])
        assert household.accounts == case.household.accounts
        assert household.lot_plan.case.lots == case.household.lot_plan.case.lots
        assert household.tax_plan == case.household.tax_plan
        assert household.incomes == case.household.incomes
        assert binding == case.binding


def test_later_sale_cannot_be_recognized_in_an_earlier_return():
    data = flat().model_dump(mode="json")
    data["dimensions"][0]["locked_choice"] = "later"
    result = search(PolicySearch.model_validate(data))
    audit = result["selected_training"]["details"][0]["rows"][-1]["lot_audit"]
    assert audit["recognized_by_year"][2026][0]["collectibles_component"] == 0
    assert audit["recognized_by_year"][2027][0]["collectibles_component"] == 41999
