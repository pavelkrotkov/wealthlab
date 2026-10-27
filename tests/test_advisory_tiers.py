"""Progressive bands and simultaneous cash-inclusive schedules use an immutable shared snapshot."""

from decimal import Decimal

from tests.advisory_cases import change, plain, with_fee
from wealthlab.household.projection import project


def test_marginal_bands_and_fixed_charge_reconcile_without_applying_top_rate_to_all_aum():
    case = with_fee(plain(asset="150000"), fixed="7")

    def tiers(data):
        data["schedules"][0]["tiers"] = [
            dict(upper_limit="100000", annual_rate=".01"),
            dict(upper_limit=None, annual_rate=".005"),
        ]

    row = project(change(case, tiers))[0]
    bill = row["advisory_fee_assessments"][0]
    # ($100k*1%+$50k*.5%)*30/360 +$7 = $111.17.
    assert bill["assessed"] == Decimal("111.17")
    assert [t["base"] for t in bill["marginal_tiers"]] == [100000, 50000]
    assert row["closing_cash"] == Decimal("4888.83")


def test_two_cash_inclusive_schedules_assess_before_either_charge_is_paid():
    case = with_fee(plain(cash="1000", asset="0"), account="cash", rate=".12")

    def twice(data):
        data["schedules"].append(dict(data["schedules"][0], id="second"))

    row = project(change(case, twice))[0]
    assert [a["valuation_base"] for a in row["advisory_fee_assessments"]] == [1000, 1000]
    assert [a["assessed"] for a in row["advisory_fee_assessments"]] == [10, 10]
    assert row["advisory_fees_paid"] == 20
    assert row["closing_cash"] == row["net_wealth"] == 980
