"""Original hypothetical marginal rates demonstrate mechanics, not any adviser's quoted schedule."""

from datetime import timedelta

from wealthlab.household.advisory_inputs import AdvisoryPlan
from wealthlab.household.calendar import months


def plan(scenario):
    covered = [
        dict(
            account_id=a.id,
            value_basis=(
                "life_net_surrender_value"
                if a.wrapper == "insurance"
                else "modeled_net_account_equity"
            ),
        )
        for a in scenario.accounts
        if a.wrapper not in {"property", "hsa", "education"}
    ]
    return AdvisoryPlan.model_validate(
        dict(
            valuation_timing="observed_product_marks_before_optional_saving_and_deposits",
            payment_scope="household_cash_pool",
            payment_account_ids=[a.id for a in scenario.accounts if a.wrapper == "cash"],
            schedules=[
                dict(
                    id="synthetic_outer_advisory",
                    provenance="illustration",
                    source_ref="Original hypothetical marginal AUM schedule; no adviser quote",
                    source_date=scenario.start,
                    available_on=scenario.start,
                    contract_terms_and_valuation_basis_confirmed=True,
                    outer_cash_fee_not_already_in_embedded_costs_confirmed=True,
                    covered=covered,
                    tiers=[
                        dict(upper_limit="100000", annual_rate=".01"),
                        dict(upper_limit=None, annual_rate=".005"),
                    ],
                    day_count=365,
                    periods=[
                        dict(
                            accrual_start=start,
                            accrual_end=end,
                            valuation_date=end - timedelta(days=1),
                            assessment_date=end - timedelta(days=1),
                            payment_due_date=end - timedelta(days=1),
                        )
                        for start, end in months(scenario.start, scenario.end)
                    ],
                )
            ],
        )
    )
