"""Original fixed PR context varies actual future wages, never residence or source eligibility.

All wages are independently assumed US-source here, so paid US income tax is
credited locally and the combined income-tax bill equals the ordinary PR tax.
Opening cash already reflects historical wages and paid employee payroll.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.example import asset
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.tax.pr_execution_salary_example import monthly


def synthetic():
    data = monthly().model_dump(mode="json")
    data["name"] = "Synthetic fixed PR context with actual retirement wages and country tax"
    data["members"][0]["retirement_date"] = "2026-01-01"
    data["incomes"][0]["stop_at_retirement"] = True
    annuals = [
        *data["tax_plan"]["cases"],
        *(p["annual"] for p in data["foreign_tax_plan"]["credit_profiles"]),
    ]
    for annual in annuals:
        for row in annual["pr_federal"]["sources"]:
            row["income"].update(federal_source="US", pr_source="US")
    for profile in data["foreign_tax_plan"]["credit_profiles"]:
        for row in profile["income"]:
            row["country"] = "US"
    market = market_case(data)
    return PolicySearch.model_validate(
        dict(
            household=Scenario.model_validate(data),
            training=market,
            validation=dict(market, seed=107),
            binding=dict(
                cash_yield_timing="opening_value_received_before_month_end_sales",
                ordinary_cash_character_confirmed=True,
                other_accounts_unmodeled_returns_confirmed=True,
            ),
            country_context=dict(
                source="Original synthetic fixed PR/US source facts across both retirement dates",
                source_date="2025-08-31",
                valid_through="2025-12-31",
                all_candidate_income_market_and_fiscal_facts_confirmed=True,
                replace_bound_future_wages_confirmed=True,
                wage_sources=[
                    dict(
                        income_id="salary",
                        source_id=f"wage_{m:02d}",
                        date=f"2025-{m:02d}-{'30' if m in (9, 11) else '31'}",
                    )
                    for m in range(9, 13)
                ],
            ),
            dimensions=[
                dict(
                    id="retirement",
                    choices=[
                        dict(id="early", retirement_dates={"person_a": "2025-11-01"}),
                        dict(id="later", retirement_dates={"person_a": "2026-01-01"}),
                    ],
                )
            ],
        )
    )


def market_case(data):
    market = dict(
        start=data["start"],
        end=data["end"],
        mode="monte_carlo",
        seed=71,
        paths=1,
        assets=[asset("cash_reference", "equity", 0, 0, 0)],
        return_convention="price_plus_cash",
        expected_annual_inflation=0,
        annual_inflation_volatility=0,
        correlation=[[1, 0], [0, 1]],
    )
    return market
