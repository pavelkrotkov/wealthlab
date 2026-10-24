"""One opening cash/account book and confirmed eligibility prevent duplicate financing."""

import pytest

from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_contribution_example import synthetic


@pytest.mark.parametrize(
    "path,value,message",
    [
        (("contribution_context_confirmed",), False, "Confirm annual IRA contribution"),
        (("contributions", "opening_cash"), "10001", "share the year and opening cash"),
        (
            ("contributions", "accounts", 0, "balance"),
            "100001",
            "match the ordinary IRA opening book",
        ),
        (("contributions", "orders", 0, "kind"), "pretax_401k", "Only ordinary IRA contributions"),
        (("contributions", "orders", 0, "id"), "draw_0", "unique IDs"),
        (("contributions", "filing"), "head", "filing status must match"),
        (
            ("annual_tax_case", "federal_income", "deductible_ira_contributions"),
            "100",
            "Remove manual IRA deductions",
        ),
        (("annual_tax_case", "federal_income", "social_security"), "100", "deduction worksheets"),
        (
            ("annual_tax_case", "federal_income", "allowed_passive_income"),
            "-100",
            "AGI-dependent passive losses",
        ),
    ],
)
def test_invalid_combined_context_blocks(path, value, message):
    data = synthetic().model_dump(mode="json")
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValueError, match=message):
        run(DistributionCase.model_validate(data))


def test_negative_magi_forecast_is_not_mistaken_for_negative_compensation():
    data = synthetic().model_dump(mode="json")
    data["annual_tax_case"] = None
    data["contributions"]["contributors"][0].update(
        traditional_ira_magi="-100", roth_ira_magi="-100"
    )
    result = run(DistributionCase.model_validate(data))
    assert sum(r["funded"] for r in result["contribution_orders"]) == 6000
    assert result["contribution_owners"][0]["federal_ira_deduction"] == 3000
