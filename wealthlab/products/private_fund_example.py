"""Independently synthetic contracts, supplied tax/basis schedules and a liquid unlevered proxy."""

from wealthlab.household.scenario import Scenario
from wealthlab.markets.sleeve_example import synthetic as market_example


def synthetic(mode="deterministic", stress="early_crash"):
    household, market, binding = market_example(mode, stress)
    fund = household.model_dump(mode="json")
    fund["name"] = "Synthetic conditional private-fund household"
    sleeve = fund["sleeve_plan"]["sleeves"][0]
    sleeve["case"].update(margin_policy="liquidate_on_breach", exit_at_horizon=False)
    sleeve["private_fund_contract"] = contract()
    for allocation in sleeve["allocations"]:
        allocation["date"] = allocation["date"][:4] + "-09-01"
    reference = Scenario.model_validate(fund).model_dump(mode="json")
    reference["name"] = "Synthetic liquid unlevered cash-distribution tax proxy"
    reference_sleeve = reference["sleeve_plan"]["sleeves"][0]
    reference_sleeve["case"].update(
        long_multiple="1",
        short_multiple="0",
        annual_manager_fee=".0005",
        annual_borrow_rate="0",
        annual_financing_rate="0",
        turnover_cost=".0001",
        exit_cost=".0001",
        maintenance_fraction_of_gross="1",
    )
    reference_sleeve["private_fund_contract"].update(
        lock_until="2026-01-01",
        dealing="monthly",
        notice_days=0,
        settlement_days=0,
    )
    market = market.model_copy(update=dict(paths=25 if mode == "monte_carlo" else 1))
    return dict(
        market=market.model_dump(mode="json"),
        binding=binding.model_dump(mode="json"),
        fund=fund,
        reference=reference,
    )


def contract():
    return dict(
        id="synthetic_private_contract",
        provenance="illustration",
        source_description="Invented cash-only fund contract, not any sponsor's terms or forecast",
        eligibility_assumed_confirmed=True,
        limited_liability_no_calls_assumed_confirmed=True,
        cash_only_no_hot_assets_no_liability_changes_assumed_confirmed=True,
        tax_basis_schedule_complete_assumed_confirmed=True,
        lock_until="2026-07-01",
        dealing="quarterly",
        notice_days=60,
        gate_fraction="1",
        settlement_days=30,
        federal_opening_basis="100000",
        new_jersey_opening_basis="100000",
        federal_capital_character="long_term",
        federal_exit_loss=dict(treatment="allowed", eligibility_after_limits_assumed=True),
        new_jersey_exit_loss=dict(treatment="allowed", eligibility_after_limits_assumed=True),
        requests=[
            dict(
                id="fund_final_request",
                provenance="illustration",
                notice_date="2027-09-01",
                amount="0",
                complete_liquidation=True,
            )
        ],
        basis_adjustments=[
            dict(
                id=f"fund_basis_{year}",
                provenance="illustration",
                date=f"{year}-09-01",
                federal="3000",
                new_jersey="3000",
                explanation="Basis increase matching illustrated allocation",
            )
            for year in (2026, 2027)
        ],
    )
