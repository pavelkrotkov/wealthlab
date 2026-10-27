"""Candidate taxes consume actual mapped wages, not a fixed favorable country bill.

From$50,000 opening cash, two/four$10,000 wages add$20,000/$40,000.
PR ordinary tax is(8430+(gross-3500-61500)*.33)*(.92/.95):
$18,381.60/$25,251.00. All-source US tax is fully credited locally.
Remaining payroll is$1,530/$3,060; NJ's actual table/formula is$4,182/$5,454.05.
"""

from decimal import Decimal as D

import pytest
from country_optimizer_cases import ready, spanish

from wealthlab.optimization.search import search


@pytest.mark.parametrize(
    ("wage", "expected"),
    [
        ("10000", [(D("45906.40"), D("24093.60")), (D("56234.95"), D("33765.05"))]),
        ("20000", [(D("56234.95"), D("33765.05")), (D("78086.95"), D("51913.05"))]),
    ],
)
def test_retirement_recomputes_both_country_bills_and_preserves_original_capital_and_sources(
    wage, expected
):
    case = ready(wage)
    original = case.model_dump_json()
    result = search(case)
    assert [
        (r["median_real_after_tax_exit_wealth"], r["median_net_cash_tax"])
        for r in result["candidates"]
    ] == expected
    assert result["selection"] == "candidate_1" and result["configured_validation_passed"]
    detail = result["held_out"]["results"]["details"][0]
    assert sum(r["income"] for r in detail["rows"]) == 4 * D(wage)
    assert sum(a.balance for a in case.household.accounts) == 50000
    assert detail["country_assessments"]["es_income_2025"]["assessment"]["income_tax"] > 0
    assert case.model_dump_json() == original


def test_spain_reconciles_candidate_wages_through_existing_native_income_and_cash_assessments():
    result = search(spanish())
    assert all(c["eligible"] for c in result["candidates"])
    assert result["selection"] == "candidate_1"
    detail = result["selected_training"]["details"][0]
    annual = detail["country_inputs"]["spain"]["assessments"]["annuals"][0]["case"]
    wage = next(i for i in annual["incomes"] if i["id"] == "future_wage")
    assert (
        wage["amount"]["amount"],
        D(annual["assets"][0]["fiscal_value"]["amount"]),
        detail["country_assessments"]["person_a_2025"]["liabilities_eur"]["wealth"] > 0,
    ) == ("10000.00", detail["rows"][-1]["closing_cash"], True)
    assert wage["amount"]["eur_per_unit"] == "0.909090909091"
    assert (
        result["candidates"][1]["median_foreign_net_cash_tax"]
        > result["candidates"][0]["median_foreign_net_cash_tax"]
    )
