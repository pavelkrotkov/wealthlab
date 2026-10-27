"""A wealth-tax refund is actual cash but cannot revise an original US income-tax credit."""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.tax.foreign_redetermination_example import synthetic_refund


def test_wealth_refund_does_not_generate_income_ftc_or_original_return_amendments():
    data = synthetic_refund().model_dump(mode="json")
    foreign = data["foreign_tax_plan"]
    foreign["assessments"][0]["tax_type"] = "wealth"
    foreign["refunds"][0]["record"]["tax_type"] = "wealth"
    rows = project(Scenario.model_validate(data))
    june = {row["date"]: row for row in rows}["2027-06-01"]
    assert june["foreign_tax_refund_received"] == 7000
    assert june["prior_tax_paid"] == 0
    assert not june["foreign_return_revisions"]
    assert not june["foreign_tax_unresolved"]
    assert not rows[-1]["foreign_final_source_returns"]
