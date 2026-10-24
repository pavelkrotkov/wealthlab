"""Synthetic spouses: retirement lowers future MAGI, not the current two-year lookback."""

from wealthlab.retirement.medicare_inputs import MedicareCase


def synthetic():
    example = dict(provenance="illustration")
    base_coverage = dict(
        eligibility_confirmed=True,
        part_a=True,
        part_a_monthly_2026=0,
        part_b=True,
        standard_b_premium_applicable=True,
        part_d=True,
        part_d_plan_monthly_2026=40,
        other_monthly_health_cost_2026=200,
        end="2028-01-01",
        **example,
    )
    return MedicareCase.model_validate(
        dict(
            start_year=2026,
            end_year=2028,
            opening_cash=5000,
            complete_context=True,
            future_policy="freeze_2026",
            premium_growth=0,
            threshold_growth=0,
            payment_policy="first_of_coverage_month_fifo_arrears",
            members=[dict(id="person", **example), dict(id="spouse", **example)],
            coverage=[
                dict(id="person_cover", member="person", start="2026-01-01", **base_coverage),
                dict(id="spouse_cover", member="spouse", start="2026-07-01", **base_coverage),
            ],
            income_history=[
                dict(
                    id="joint_2024",
                    year=2024,
                    members=["person", "spouse"],
                    filing="joint",
                    agi=300000,
                    tax_exempt_interest=1000,
                    **example,
                ),
                dict(
                    id="joint_2025",
                    year=2025,
                    members=["person", "spouse"],
                    filing="joint",
                    agi=120000,
                    tax_exempt_interest=1000,
                    **example,
                ),
            ],
            receipts=[dict(id="later_funding", date="2027-01-01", amount=20000, **example)],
        )
    )
