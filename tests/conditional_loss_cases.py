"""Supplied allocations with income and separate capital/NJ partnership loss assumptions."""

from wealthlab.products.household_inputs import SleeveAllocation


def allocation(federal="allowed", state="allowed", release="2027-04-01"):
    def timing(treatment):
        return dict(
            treatment=treatment,
            release_on=release if treatment == "deferred" else None,
            eligibility_after_limits_assumed=True,
        )

    return SleeveAllocation.model_validate(
        dict(
            id="conditional",
            provenance="assumption",
            date="2026-04-01",
            federal=dict(short_term=50000, long_term=-12000),
            new_jersey=dict(dispositions=50000, business=dict(partnership=-12000)),
            federal_loss=timing(federal),
            new_jersey_loss=timing(state),
        )
    )
