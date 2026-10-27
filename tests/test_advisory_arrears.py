"""A later actual receipt cures an unpaid bill without rewriting the earlier cash or fee history."""

from decimal import Decimal

from tests.advisory_cases import plain, with_fee
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_later_household_receipt_pays_prior_fee_once_without_counting_the_old_gap_again():
    data = plain(cash="0").model_dump(mode="json")
    data["end"] = "2026-03-01"
    data["incomes"] = [
        dict(
            id="later_receipt",
            provenance="illustration",
            owner="person_a",
            start="2026-02-01",
            end="2026-03-01",
            monthly_amount="1000",
            currency="USD",
            annual_growth=0,
            stop_at_retirement=False,
        )
    ]
    rows = project(with_fee(Scenario.model_validate(data)))
    assert rows[0]["closing_cash"] == rows[0]["advisory_fees_paid"] == 0
    assert rows[0]["advisory_fees_owed"] == Decimal("83.33")
    assert rows[1]["advisory_fees_assessed"] == 0
    assert rows[1]["advisory_fees_paid"] == Decimal("83.33")
    assert rows[1]["advisory_fees_owed"] == rows[1]["fees_unfunded"] == 0
    assert rows[1]["closing_cash"] == Decimal("916.67")
    assert rows[-1]["net_wealth"] == Decimal("100916.67")
