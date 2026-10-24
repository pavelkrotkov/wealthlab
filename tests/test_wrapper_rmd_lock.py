"""A liquidity restriction cannot erase the existing required-withdrawal target."""

from wealthlab.retirement.distribution_example import synthetic
from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run


def test_an_illiquid_ira_retains_its_real_rmd_shortfall():
    data = synthetic().model_dump(mode="json")
    data["owners"][0]["birth_date"] = "1950-06-01"
    data["annual_tax_case"] = None
    baseline = run(DistributionCase.model_validate(data))
    data["liquidity_locks"] = [
        dict(
            id="lock",
            provenance="assumption",
            account_id="ira",
            start="2026-01-01",
            end="2027-01-01",
        )
    ]
    locked = run(DistributionCase.model_validate(data))
    assert baseline["rmd"]["person"]["shortfall"] == 0
    assert locked["rmd"]["person"]["required"] > 0
    assert locked["rmd"]["person"]["shortfall"] == locked["rmd"]["person"]["required"]
    assert locked["orders"][0]["blocked_by_liquidity"]
