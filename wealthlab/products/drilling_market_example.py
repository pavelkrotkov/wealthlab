"""Original hypothetical commodity/share proxies; supplied well values stay independent."""

from wealthlab.markets.example import asset, invented_history
from wealthlab.markets.inputs import MarketCase
from wealthlab.products.drilling_example import synthetic as household
from wealthlab.products.drilling_market import DrillingMarketCase


def synthetic(mode="deterministic", profile="base"):
    scenario = household(profile)
    return DrillingMarketCase.model_validate(
        dict(
            household=scenario.model_dump(mode="json"),
            market=market(scenario, mode).model_dump(mode="json"),
            binding=dict(
                drilling=dict(
                    account_id=scenario.drilling_plan.account_id,
                    commodity_factor="commodity",
                    reference_factor="reference",
                    opening_commodity_price="100",
                    replace_price_observations_confirmed=True,
                    fixed_production_cost_tax_and_property_exit_quotes_valid_for_prices_confirmed=True,
                    validity_source=(
                        "Original synthetic assumption: supplied quantities, costs, tax facts, "
                        "residual-property and exit quotes remain valid on these price paths; "
                        "not sponsor terms, an appraisal or a recalculation of legal limits"
                    ),
                ),
                cash_yield_timing="opening_value_received_before_month_end_sales",
                ordinary_cash_character_confirmed=True,
                other_accounts_unmodeled_returns_confirmed=True,
            ),
        )
    )


def market(scenario, mode):
    data = dict(
        start=str(scenario.start),
        end=str(scenario.end),
        mode=mode,
        assets=[
            asset("commodity", "other", 0.12, 0.25, 0),
            asset("reference", "equity", 0.04, 0.15, 0),
        ],
        return_convention="price_plus_cash",
        expected_annual_inflation=0,
        annual_inflation_volatility=0,
        correlation=[[1, 0.2, 0], [0.2, 1, 0], [0, 0, 1]],
        seed=92,
        paths=4 if mode == "monte_carlo" else 1,
    )
    if mode == "historical":
        data["historical"] = history()
    if mode == "stress":
        data["shocks"] = [
            dict(name="Synthetic commodity crash", month=0, mark_shocks={"commodity": -0.5}),
            dict(name="Synthetic reference exit lock", month=23, lock_months={"reference": 1}),
        ]
    return MarketCase.model_validate(data)


def history():
    data = invented_history()
    data.update(
        source=(
            "Original invented commodity/share proxies; not actual market history; "
            "availability/retrieval dates are synthetic assumptions"
        ),
        retrieved_on="2010-01-01",
        months=[
            dict(
                row,
                mark_returns=dict(
                    commodity=row["mark_returns"]["employer"],
                    reference=row["mark_returns"]["equities"],
                ),
                cash_yields=dict(commodity=0, reference=0),
            )
            for row in data["months"][:24]
        ],
    )
    return data
