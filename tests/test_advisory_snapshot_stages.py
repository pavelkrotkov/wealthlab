"""A prior pre-spending product observation differs from the completed state on the same date."""

from datetime import date

import pytest

from tests.advisory_cases import plain
from tests.advisory_snapshot_cases import snapshot_fee
from wealthlab.household.advisory_advance_example import advance_plan
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


@pytest.mark.parametrize(
    "cutoff, base, fee, ending",
    [
        ("product_marks_before_optional_saving", 1000, 10, 890),
        ("completed_month_end", 900, 9, 891),
    ],
)
def test_exact_same_calendar_date_resolves_its_declared_observed_cutoff(cutoff, base, fee, ending):
    data = plain(cash="1000", asset="0").model_dump(mode="json")
    data["end"] = "2026-03-01"
    data["expenses"] = [
        dict(
            id="january_bill",
            provenance="illustration",
            start="2026-01-01",
            end="2026-02-01",
            monthly_amount="100",
            currency="USD",
            annual_growth=0,
            category="essential",
        )
    ]
    case = snapshot_fee(
        Scenario.model_validate(data),
        account="cash",
        cutoff=cutoff,
        valued="2026-01-31",
        billed="2026-02-28",
        rate=".12",
    )
    rows = project(case)
    assert rows[0]["closing_cash"] == 900
    assert rows[1]["advisory_fee_assessments"][0]["valuation_base"] == base
    assert rows[1]["advisory_fees_paid"] == fee
    assert rows[-1]["net_wealth"] == ending


def test_advance_starter_does_not_invent_a_post_horizon_service_period():
    with pytest.raises(ValueError, match="at least two modeled months"):
        advance_plan(plain().model_copy(update=dict(end=date(2026, 2, 1))))
