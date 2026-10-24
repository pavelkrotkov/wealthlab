"""Conditional NJ investment recognition and recipient tax enter different channels."""

from decimal import Decimal

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.hsa_invested_example import synthetic
from wealthlab.tax.annual import AnnualCase, evaluate


def test_actual_nj_ingredients_change_the_completed_return_without_cash_tax_savings():
    data = synthetic().model_dump(mode="json")
    case = data["tax_plan"]["cases"][0]
    case["nj_income"]["wages"] = "100000"
    case["federal_income"]["wages_primary"] = "100000"
    rows = project(Scenario.model_validate(data))
    expected = dict(case)
    expected["nj_income"] = dict(case["nj_income"], dispositions="2399", dividends="100")
    annual = evaluate(AnnualCase.model_validate(expected))
    actual = rows[-1]["annual_tax"]
    assert actual["new_jersey"]["income_tax"] == annual["new_jersey"]["income_tax"]
    assert actual["federal"]["agi"] == 100000
    assert sum(r["tax_event_cash"] for r in rows) == 0


def test_nonqualified_distribution_uses_actual_sale_and_no_second_nj_principal_tax():
    data = synthetic().model_dump(mode="json")
    plan = data["hsa_plan"]
    plan["medical_bills"] = []
    plan["nonqualified_treatment"] = "ordinary_noninvestment_assumption"
    plan["nj_withdrawal_taxable_fractions"] = dict(nonqualified="0")
    plan["generated_distribution_tax_excluded_from_other_inputs_confirmed"] = True
    plan["withdrawals"] = [
        dict(
            id="nonqualified",
            provenance="assumption",
            date="2026-01-15",
            source="hsa",
            amount="5000",
            mode="allow_nonqualified",
            receipt_ids=[],
        )
    ]
    rows = project(Scenario.model_validate(data))
    assert sum(r["hsa_withdrawal_cash"] for r in rows) == 5000
    assert sum(r["hsa_nonqualified_taxable"] for r in rows) == 5000
    assert sum(r["hsa_additional_tax"] for r in rows) == 1000
    assert sum(r["hsa_nj_withdrawal_income"] for r in rows) == 0
    assert rows[-1]["annual_tax"]["federal"]["agi"] == Decimal(5000)
    assert rows[-1]["annual_tax"]["new_jersey"]["gross_income"] == 2499
