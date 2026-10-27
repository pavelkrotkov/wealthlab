"""Foreign liability year cannot redirect the actual original US paid-year revision."""

from copy import deepcopy

from foreign_redetermination_cases import synthetic_refund

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_2024_foreign_liability_paid_2025_and_refunded_2027_revises_us_2025_not_2024():
    data = synthetic_refund().model_dump(mode="json")
    foreign = data["foreign_tax_plan"]
    foreign["assessments"][0]["liability_year"] = 2024
    foreign["schedules"][0]["source_income_year"] = 2024
    refund = foreign["refunds"][0]
    refund.update(source_income_year=2024)
    refund["record"]["liability_year"] = 2024
    historical = deepcopy(foreign["credit_profiles"][0]["income"][1])
    historical["value"]["date"] = "2024-09-30"
    foreign["credit_profiles"][0]["income"].append(historical)
    rows = project(Scenario.model_validate(data))
    june = {row["date"]: row for row in rows}["2027-06-01"]
    assert [r["year"] for r in june["foreign_return_revisions"]] == [2025, 2026]
    assert june["prior_tax_paid"] == 5500
    assert not june["foreign_tax_unresolved"]
    assert set(rows[-1]["foreign_final_source_returns"]) == {2025, 2026}
