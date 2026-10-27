"""Part-year deductions follow legal periods rather than a blanket tax fraction.

Filing uses full-year gross even where each period is below the normal filing
threshold. The official fifteen-day rule can count one calendar month in both
returns. Medical deductions instead use actual period expenses and gross.
"""

from decimal import Decimal

from nj_residence_helpers import edited, results

from wealthlab.tax.nj_residence_example import row


def test_full_year_gross_determines_threshold_even_when_resident_income_below_ten_thousand():
    def change(profile, data):
        profile["income"] = [
            row("before", "2025-06-30", 6000, "allowed"),
            row("outside", "2025-09-30", 6000, "denied"),
        ]
        data["nj_income"]["wages"] = "12000"

    resident, outside = results(edited(change))
    assert not resident["below_filing_threshold"]
    assert resident["income_tax"] == 77
    assert outside["income_tax"] == 0


def test_fifteen_day_rule_counts_each_return_independently_even_if_months_sum_thirteen():
    def change(profile, _):
        profile["people"][0]["periods"] = [dict(start="2025-01-01", end="2025-01-16")]

    resident, outside = results(edited(change))
    assert resident["months"] == 1
    assert outside["months"] == 12
    assert resident["prorated_exemptions"] == Decimal("83.33")
    assert outside["prorated_exemptions"] == 1000


def test_post_departure_line22_pension_has_no_nj_source_column_even_if_marked_nj():
    def change(profile, data):
        profile["income"].append(row("pension", "2025-10-31", 30000, "allowed", "pension"))
        data["nj_income"]["pension"] = "30000"

    outside = results(edited(change))[1]
    assert outside["column_a"] == 80000
    assert outside["column_b"] == 20000
    assert outside["income_percentage"] == Decimal(".2500")


def test_actual_medical_expenses_use_the_period_gross_floor_and_not_an_annual_fraction():
    def change(profile, _):
        profile["deductions"] = [
            dict(
                owners=["person_a"],
                period="resident",
                paid_on="2025-06-15",
                inputs=dict(medical="5000"),
                eligibility_and_period_allocation_assumed_confirmed=True,
                source="Synthetic medical expense incurred and paid during NJ residence",
            )
        ]

    resident, outside = results(edited(change))
    assert resident["deductions"] == 4500  # 5000 - 2% * 50000 + 500 exemption
    assert outside["deductions"] == 500
