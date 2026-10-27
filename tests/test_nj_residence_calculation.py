"""Official move mechanics use period facts, full-year thresholds and unbounded B/A."""

from decimal import Decimal

from nj_residence_helpers import edited, results, state

from wealthlab.tax.annual import evaluate
from wealthlab.tax.nj_residence_example import row, synthetic


def test_resident_and_nonresident_returns_use_distinct_income_and_prorated_exemptions():
    resident, outside = results(synthetic())
    assert (resident["months"], outside["months"]) == (6, 6)
    assert (resident["prorated_exemptions"], outside["prorated_exemptions"]) == (500, 500)
    assert resident["column_a"] == outside["column_a"] == 50000
    assert outside["column_b"] == 20000
    assert outside["income_percentage"] == Decimal(".4000")
    # The official table's single $49,500-49,550 cell is $1,244.
    assert (resident["income_tax"], outside["income_tax"]) == (1244, Decimal("497.60"))
    assert state(synthetic())["income_tax"] == Decimal("1741.60")


def test_departure_does_not_remove_worldwide_us_wages_or_payroll():
    case = synthetic()
    moved = evaluate(case)
    resident = evaluate(case.model_copy(update=dict(nj_residence=None)))
    assert moved["federal"] == resident["federal"]
    assert moved["new_jersey"]["income_tax"] == Decimal("1741.60")
    assert resident["new_jersey"]["income_tax"] == 4182
    assert moved["federal"]["employee_payroll"] == 7650


def test_official_nj_real_property_example_allows_125_percent_without_capping():
    def change(profile, data):
        profile["people"][0].update(status="nonresident", periods=[])
        profile["income"] = [
            row("nj_property", "2025-06-30", 50000, "allowed", "dispositions"),
            row("fl_property_loss", "2025-06-30", -10000, "denied", "dispositions"),
        ]
        data["nj_income"].update(wages="0", dispositions="40000")

    only = results(edited(change))[0]
    assert only["column_a"] == 40000
    assert only["column_b"] == 50000
    assert only["income_percentage"] == Decimal("1.2500")
    assert only["tax_before_source_percentage"] == 683
    assert only["income_tax"] == Decimal("853.75")


def test_nonresident_percentage_rounds_to_four_decimals_before_multiplying_tax():
    def change(profile, data):
        profile["people"][0].update(status="nonresident", periods=[])
        profile["income"] = [
            row("nj", "2025-06-30", 20000, "allowed"),
            row("elsewhere", "2025-06-30", 10000, "denied"),
        ]
        data["nj_income"]["wages"] = "30000"

    only = results(edited(change))[0]
    assert only["income_percentage"] == Decimal(".6667")
    assert only["tax_before_source_percentage"] == 438
    assert only["income_tax"] == Decimal("292.01")


def test_unsupported_retirement_and_business_outputs_keep_the_existing_numeric_contract():
    result = state(synthetic())
    assert (
        result["pension_exclusion"],
        result["other_exclusion"],
        result["business_adjustment"],
        result["business_expired"],
    ) == (0, 0, 0, 0)
    assert result["business_carry"] == []
