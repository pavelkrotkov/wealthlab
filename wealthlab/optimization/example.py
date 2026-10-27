"""Short synthetic search deliberately fails the default age-100 horizon constraint."""

from wealthlab.markets.household_example import synthetic as market_household
from wealthlab.optimization.inputs import PolicySearch


def synthetic():
    household, market, binding = market_household("monte_carlo")
    data = household.model_dump(mode="json")
    data["name"] = "Synthetic bounded retirement search; short horizon is insufficient"
    data["accounts"][0]["balance"] = "200000"
    data["expenses"][0]["monthly_amount"] = "2000"
    data["lot_plan"]["case"]["sale_policies"] = [
        dict(
            id="complete_exit",
            provenance="illustration",
            date="2027-12-31",
            account_id="brokerage",
            security_id="stock",
            mode="sell_all",
            prices=dict(stock="100"),
            commission="1",
            selection="hifo",
        )
    ]
    training = market.model_dump(mode="json")
    training.update(paths=4, seed=71)
    owner = data["members"][0]["id"]
    return PolicySearch.model_validate(
        dict(
            household=data,
            binding=binding,
            training=training,
            validation=dict(training, seed=107, paths=8),
            dimensions=[
                dict(
                    id="retirement",
                    choices=[
                        dict(id="early", retirement_dates={owner: "2026-01-01"}),
                        dict(id="later", retirement_dates={owner: "2027-01-01"}),
                    ],
                )
            ],
        )
    )
