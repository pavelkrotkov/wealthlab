"""A2 category arithmetic and ScheduleC source attribution remain independently visible."""

from decimal import Decimal

from pr_schedule_c_cases import mixed

from wealthlab.tax.pr_preferential import calculate


def test_mixed_wages_and_gain_allocate_exemption_before_a_binding_actual_credit_limit():
    annual, slices = mixed()
    result = calculate(annual, slices, Decimal(20000))
    allocation = result["regular_source_allocation"]
    assert result["regular_tax"] == 26481
    assert allocation["source_net"] == Decimal("48833.45")
    assert result["regular_credit"]["limitation_fraction"] == Decimal(".3333")
    assert result["regular_credit"]["allowed"] == Decimal("8826.12")
    assert result["income_tax"] == Decimal("17654.88")


def test_signed_a2_ordinary_column_is_preserved_in_the_summed_credit_denominator():
    # A2ColumnA line11:1000-3500=-2500; ColumnC100000; signed sum97500.
    # C allocates3500*99.01%=3465.35. Actual source net96534.65, separate
    # aggregate limit14851.48, keeps rounded-up country limit14851.50 honest.
    annual, slices = mixed(1000, 100000)
    result = calculate(annual, slices, Decimal(20000))
    assert result["a2_ordinary_net_before_tax_floor"] == -2500
    assert result["ordinary_net"] == 0
    assert result["regular_net_income"] == 97500
    assert result["regular_source_allocation"]["source_net"] == Decimal("96534.65")
    assert result["regular_credit"]["allowed"] == Decimal("14851.48")
