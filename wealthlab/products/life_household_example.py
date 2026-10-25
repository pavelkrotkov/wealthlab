"""Synthetic policy premiums, loan receipts and independently supplied failure settlements."""

from wealthlab.household.example import synthetic as household
from wealthlab.household.scenario import Scenario
from wealthlab.products.life_contract_example import synthetic as contract_case
from wealthlab.tax.projection_example import template


def event(identity, when, kind, amount, **extra):
    return dict(
        id=identity,
        provenance="assumption",
        date=when,
        kind=kind,
        amount=str(amount),
        nj_ordinary_income="0",
        **extra,
    )


def policy():
    data = contract_case().contract.model_dump(mode="json")
    data.update(
        start="2026-01-01",
        owner_birth_date="1975-01-01",
        opening_federal_basis="10000",
        opening_loan="0",
        values=values(),
        events=[
            event("premium1", "2026-01-15", "premium", 1000),
            event("premium2", "2026-02-15", "premium", 1000),
            event("loan", "2026-03-15", "loan_advance", 500, cash_value_before="12000"),
            event("future1", "2027-01-15", "premium", 1000),
            event("future2", "2028-01-15", "premium", 1000),
        ],
    )
    return data


def values():
    return [
        dict(
            date=when,
            gross_cash_value=str(value),
            gross_surrender_value=str(value),
            gross_death_benefit="100000",
        )
        for when, value in (("2026-01-31", 10900), ("2026-02-28", 11800), ("2026-03-31", 12000))
    ]


def holding():
    exits = {
        key: dict(
            event=event(key + "_exit", when, "surrender", gross),
            source="Synthetic conditional full settlement after unpaid premium",
            applicable_to_unfunded_payment_confirmed=True,
        )
        for key, when, gross in (
            ("premium1", "2026-01-15", 10000),
            ("premium2", "2026-02-15", 10900),
        )
    }
    return dict(
        account_id="life_policy",
        contract=policy(),
        funding="cash_only",
        opening_values=dict(
            date="2026-01-01",
            gross_cash_value="10000",
            gross_surrender_value="10000",
            gross_death_benefit="100000",
        ),
        failure_exits=exits,
        payments_complete_through="2029-01-01",
        other_inputs_exclude_policy_confirmed=True,
    )


def synthetic():
    data = household().model_dump(mode="json")
    data.update(name="Synthetic actual whole-life household", end="2026-04-01", incomes=[])
    data["accounts"] = [data["accounts"][0]]
    data["accounts"][0]["balance"] = "50000"
    data["accounts"].append(
        dict(
            id="life_policy",
            provenance="assumption",
            owner="person_a",
            currency="USD",
            wrapper="insurance",
            balance="10000",
            monthly_fee="0",
        )
    )
    data["expenses"][0]["monthly_amount"] = "1000"
    data["members"][0]["retirement_date"] = "2026-02-01"
    data["life_plan"] = dict(holdings=[holding()], insurance_need_by_owner={"person_a": "150000"})
    case = Scenario.model_validate(data)
    return case.model_copy(update={"tax_plan": template(case)})
