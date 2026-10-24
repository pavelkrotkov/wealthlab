"""Independent household example with explicit placeholder marks and supplied tax allocations."""

from datetime import timedelta

from wealthlab.household.calendar import months
from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.products.household_inputs import SleevePlan
from wealthlab.products.long_short_example import terms
from wealthlab.tax.projection_example import template as tax_template


def synthetic():
    data = household().model_dump(mode="json")
    data.update(name="Synthetic household long-short cash and recourse debt")
    data["accounts"] = [
        dict(
            id="cash",
            provenance="illustration",
            owner="joint",
            currency="USD",
            wrapper="cash",
            balance="10000",
            monthly_fee="0",
        ),
        dict(
            id="sleeve",
            provenance="illustration",
            owner="person_a",
            currency="USD",
            wrapper="taxable",
            balance="100000",
            monthly_fee="0",
        ),
    ]
    data["incomes"][0]["monthly_amount"] = "5000"
    data["expenses"][0]["monthly_amount"] = "2000"
    scenario = Scenario.model_validate(data)
    case = dict(terms().model_dump(mode="json"), outside_cash="0", exit_at_horizon=False)
    plan = dict(
        sleeves=[
            dict(
                id="risk_book",
                provenance="illustration",
                account_id="sleeve",
                case=case,
                observations=observations(scenario),
                allocations=allocations(scenario),
                all_tax_recognition_and_exit_assumptions_supplied_confirmed=True,
            )
        ],
        other_tax_inputs_exclude_supplied_allocations_confirmed=True,
        actual_household_cash_confirmed=True,
        priority="after_prior_tax_arrears_before_wrapper_deposits_and_current_tax",
    )
    return scenario.model_copy(
        update=dict(tax_plan=tax_template(scenario), sleeve_plan=SleevePlan.model_validate(plan))
    )


def observations(scenario):
    return [
        dict(
            id=f"sleeve_observation_{i}",
            provenance="illustration",
            date=end - timedelta(days=1),
            long_return=0,
            short_return=0,
            long_yield=0,
            short_yield=0,
            locked=False,
        )
        for i, (_, end) in enumerate(months(scenario.start, scenario.end))
    ]


def allocations(scenario):
    return [
        dict(
            id=f"illustrated_allocation_{year}",
            provenance="illustration",
            date=f"{year}-12-01",
            federal=dict(short_term="3000"),
            new_jersey=dict(dispositions="3000"),
        )
        for year in range(scenario.start.year, scenario.end.year)
    ]
