"""Independent synthetic allocation/cash-election scenarios, not terms of a named employer plan."""

from datetime import date

from wealthlab.employment.compensation_inputs import CompensationPlan, Tranche
from wealthlab.employment.example import synthetic as wages
from wealthlab.household.records import Account


def synthetic(election="cash"):
    case = wages()
    path = case.employment_plan.paths[0]
    employment = case.employment_plan.model_copy(
        update=dict(paths=[path.model_copy(update=dict(changes=[path.changes[0]]))])
    )
    account = Account(
        id="employer_fund",
        provenance="illustration",
        owner="person_a",
        wrapper="employer",
        currency="USD",
        balance=20000,
        monthly_fee=0,
    )
    tranche = Tranche(
        id="award",
        provenance="illustration",
        account=account.id,
        opening_vested=20000,
        opening_unvested=80000,
        liquid_from=date(2027, 1, 1),
        unvested_tax_cash_right_confirmed=True,
        vested_tax_cash_before_liquidity_confirmed=False,
    )
    plan = CompensationPlan(
        tranches=[tranche],
        events=events(election),
        tax_inputs_exclude_plan_events_confirmed=True,
        all_plan_tax_recognition_supplied_confirmed=True,
        tax_policy="supplied_allocations_independent_of_cash_elections",
        return_convention="net_embedded_fees_external_account_fees_separate",
    )
    return case.model_copy(
        update=dict(
            name="Synthetic employer allocation and cash election",
            accounts=[*case.accounts, account],
            employment_plan=employment,
            compensation_plan=plan,
        )
    )


def events(election):
    base = dict(tranche="award", provenance="illustration", sequence=0)
    return [
        dict(base, id="grant", kind="grant", date=date(2026, 1, 2), amount=10000),
        dict(base, id="growth", kind="net_return", date=date(2026, 3, 1), rate=".10"),
        dict(
            base,
            id="allocation",
            kind="allocation",
            date=date(2026, 4, 1),
            federal=dict(allowed_passive_income=20000),
            new_jersey=dict(business=dict(partnership=20000)),
        ),
        dict(
            base,
            id="tax_cash",
            kind="distribution",
            date=date(2026, 5, 1),
            amount=20000,
            bucket="unvested",
            purpose="tax_distribution",
            election=election,
        ),
        dict(base, id="partial_vest", kind="vest", date=date(2026, 6, 1), amount=20000),
        dict(base, id="remaining_vest", kind="vest", date=date(2026, 12, 1), amount=None),
        dict(
            base,
            id="locked_request",
            kind="distribution",
            date=date(2026, 12, 15),
            amount=20000,
            bucket="vested",
            purpose="ordinary",
            election="cash",
        ),
        dict(
            base,
            id="liquid_request",
            kind="distribution",
            date=date(2027, 2, 1),
            amount=10000,
            bucket="vested",
            purpose="ordinary",
            election="cash",
        ),
    ]


def template(scenario):
    return dict(
        tranches=[
            dict(
                id=f"tranche_{index}",
                provenance="unresolved",
                account=a.id,
                opening_vested=str(a.balance),
                opening_unvested="0",
                liquid_from=str(scenario.start),
                unvested_tax_cash_right_confirmed=False,
                vested_tax_cash_before_liquidity_confirmed=False,
            )
            for index, a in enumerate(scenario.accounts)
            if a.wrapper == "employer"
        ],
        events=[],
        tax_inputs_exclude_plan_events_confirmed=False,
        all_plan_tax_recognition_supplied_confirmed=False,
        tax_policy="supplied_allocations_independent_of_cash_elections",
        return_convention="net_embedded_fees_external_account_fees_separate",
    )
