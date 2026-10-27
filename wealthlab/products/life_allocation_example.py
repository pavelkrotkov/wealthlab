"""Original hypothetical new issue versus remaining uninsured, with identical capital.

Values and failure settlements are supplied synthetic assumptions, not an insurer
quote. Nothing scales the policy or converts opening household cash to free cover.
"""

from copy import deepcopy

from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.saving_example import synthetic as saving_household
from wealthlab.products.life_comparison_example import account
from wealthlab.products.life_comparison_inputs import LifeComparison
from wealthlab.products.life_household_example import event


def contract():
    return dict(
        id="new_policy",
        provenance="assumption",
        name="Hypothetical zero-opening new issue with supplied exit",
        source="Original synthetic path; conditional terms, no insurer illustration or quote",
        source_date="2026-01-01",
        start="2026-01-01",
        issue_date="2026-01-01",
        owner_birth_date="1975-01-01",
        opening_federal_basis="0",
        opening_loan="0",
        federal_status="non_mec",
        ordinary_personal_contract_confirmed=True,
        no_aggregation_or_special_basis_adjustments_confirmed=True,
        withdrawals_without_early_benefit_recapture_confirmed=True,
        capitalized_interest_is_new_loan_confirmed=True,
        additional_tax_exception="none",
        values_match_executed_events_confirmed=True,
        stop_funding_date="2026-02-15",
        events=[
            event("new_premium1", "2026-01-15", "premium", 1000),
            event("new_premium2", "2026-02-15", "premium", 1000),
            dict(event("new_surrender", "2026-03-15", "surrender", 2100), nj_ordinary_income="100"),
        ],
        values=[
            dict(
                date=when,
                gross_cash_value=str(amount),
                gross_surrender_value=str(amount),
                gross_death_benefit="100000",
            )
            for when, amount in (("2026-01-31", 900), ("2026-02-28", 1800))
        ],
    )


def holding():
    return dict(
        account_id="new_policy",
        contract=contract(),
        opening_values=dict(
            date="2026-01-01",
            gross_cash_value="0",
            gross_surrender_value="0",
            gross_death_benefit="0",
        ),
        funding="cash_only",
        failure_exits={
            f"new_premium{i}": dict(
                event=event(f"unfunded_{i}", when, "surrender", amount),
                source="Synthetic conditional full settlement after the unfunded payment",
                applicable_to_unfunded_payment_confirmed=True,
            )
            for i, when, amount in ((1, "2026-01-15", 0), (2, "2026-02-15", 900))
        },
        payments_complete_through="2029-01-01",
        other_inputs_exclude_policy_confirmed=True,
    )


def synthetic():
    data = saving_household().model_dump(mode="json")
    data.update(name="No policy; independently retained protection need")
    data["accounts"][0]["balance"] = "10000"
    data["lot_plan"]["savings"] = []
    data["life_plan"] = dict(holdings=[], insurance_need_by_owner={"person_a": "150000"})
    new = deepcopy(data)
    new["name"] = "Hypothetical new policy paid from the same household cash"
    new["accounts"].append(account("new_policy"))
    new["life_plan"]["holdings"] = [holding()]
    return LifeComparison(
        alternatives={
            "no_policy": Scenario.model_validate(data),
            "new_issue": Scenario.model_validate(new),
        },
        liquid_reference="no_policy",
        term_account_ids=[],
        independently_priced_protection_confirmed=False,
    )
