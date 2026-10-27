"""Original common-region comparison with ample income and no quota-cap reduction."""

from wealthlab.tax.spain_example import asset, income, synthetic


def case(region, wealth="4000000"):
    data = synthetic(region).model_dump(mode="json")
    data.update(
        assets=[asset("portfolio", wealth, False)],
        incomes=[income("earnings", "1000000", "general")],
        long_held_gain_cap_exclusion_eur="0",
    )
    return data
