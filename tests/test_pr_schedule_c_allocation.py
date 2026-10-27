"""The percentage must round before exemption allocation, then net limits round separately.

US10000/30000=33.33%;3500*33.33%=1166.55 allocated exemption.
NetUS8833.45/26500 again rounds33.33%. PR tax1223.60 therefore permits
407.83 credit, versus the former continuous-ratio407.87. Native US income
is10000 minus prorated5250 standard deduction, so475 is actually payable.
"""

from decimal import Decimal

from pr_schedule_c_cases import ordinary

from wealthlab.tax.pr_annual import evaluate


def test_actual_annual_us_payment_is_limited_after_two_separate_rounded_source_percentages():
    result = evaluate(ordinary())["candidate"]
    local = result["puerto_rico"]
    audit = local["regular_source_allocation"]
    assert result["federal"]["income_tax"] == 475
    assert audit["attributable_percentage"] == Decimal(".3333")
    assert audit["allocated_deductions_and_exemptions"] == Decimal("1166.55")
    assert audit["source_net"] == Decimal("8833.45")
    assert local["regular_credit"]["allowed"] == Decimal("407.83")
    assert local["income_tax"] == Decimal("815.77")
