"""Original synthetic home/liens example; supplied recognition is not an exclusion calculation."""

from datetime import timedelta

from wealthlab.household.calendar import months
from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.tax.projection_example import template


def synthetic():
    data = household().model_dump(mode="json")
    data.update(
        name="Synthetic sourced personal home and actual lien close",
        end="2027-01-01",
        incomes=[],
        expenses=[],
        contributions=[],
    )
    data["accounts"] = [
        dict(
            id="cash",
            provenance="illustration",
            owner="joint",
            currency="USD",
            wrapper="cash",
            balance="20000",
            monthly_fee="0",
        ),
        dict(
            id="home",
            provenance="illustration",
            owner="joint",
            currency="USD",
            wrapper="property",
            balance="300000",
            monthly_fee="0",
        ),
    ]
    data["debts"] = [
        dict(
            id="home_lien",
            provenance="illustration",
            currency="USD",
            balance="60000",
            annual_rate=".12",
            monthly_payment="600",
        )
    ]
    scenario = Scenario.model_validate(data)
    data["tax_plan"] = template(scenario).model_dump(mode="json")
    data["property_plan"] = plan(scenario)
    return Scenario.model_validate(data)


def plan(scenario):
    return dict(
        timing="month_end_after_required_products_before_advisory_and_optional_saving",
        other_tax_inputs_exclude_property_recognition_confirmed=True,
        debt_payoff_full_month_native_interest_confirmed=True,
        holdings=[holding(scenario)],
    )


def holding(scenario):
    return dict(
        id="original_home",
        provenance="illustration",
        account_id="home",
        source_ref="Original synthetic complete home/basis/closing assumptions; no contract claim",
        source_date=scenario.start,
        available_on=scenario.start,
        use="personal_use_home",
        ownership_legal_use_and_tax_facts_supplied_confirmed=True,
        unchanged_basis_and_no_other_asset_cashflows_confirmed=True,
        opening_federal_basis="250000",
        opening_nj_basis="240000",
        linked_debt_ids=["home_lien"],
        observations=[
            dict(
                id=f"home_mark_{i}",
                provenance="illustration",
                date=str(end - timedelta(days=1)),
                available_on=str(end - timedelta(days=1)),
                value="300000",
                locked=False,
            )
            for i, (_, end) in enumerate(months(scenario.start, scenario.end))
        ],
        terminal_action="sell",
        sale=dict(
            id="home_close",
            provenance="illustration",
            date="2026-06-30",
            gross_proceeds="300000",
            closing_costs="10000",
            maximum_owner_cash_to_close="0",
            federal_taxable_gain="10000",
            federal_character="long_term",
            nj_taxable_gain="15000",
            costs_due_only_on_executed_close_confirmed=True,
            no_closing_withholding_or_other_escrow_terms_confirmed=True,
            prelimited_tax_recognition_and_no_deduction_claims_confirmed=True,
        ),
    )
