"""Build ordinary 529 cases from actual household accounts and separate tuition bills.

Every institution request describes a net qualified bill after other benefits.
The request reserves that expense once; only actual distributions use it.
Cash fallback pays any remaining bill without another wrapper withdrawal.
"""

from wealthlab.retirement.education_inputs import EducationCase


def annual_case(scenario, year, balances=None, basis=None):
    plan = scenario.education_plan
    terms = {a.account_id: a for a in plan.accounts}
    accounts = opening_accounts(scenario, balances, basis)
    tuition = [r for r in plan.tuition if r.date.year == year]
    return EducationCase.model_validate(
        dict(
            year=year,
            rule_mode=plan.rule_mode,
            opening_cash=0,
            complete_context=True,
            nj_gross_income=None,
            people=plan.people,
            plans=plan.plans,
            accounts=accounts,
            contributions=[r for r in plan.contributions if r.date.year == year],
            returns=[r for r in plan.returns if r.date.year == year],
            **tuition_inputs(tuition, terms),
        )
    )


def tuition_inputs(tuition, terms):
    return dict(
        withdrawals=[dict(**r.model_dump(), payee="institution") for r in tuition],
        expenses=[expense(r, terms[r.source].beneficiary) for r in tuition],
        allocations=[
            dict(
                id=f"allocation_{identity}",
                provenance="assumption",
                account=identity,
                recipient="beneficiary",
                expenses=uses(tuition, identity),
            )
            for identity in dict.fromkeys(r.source for r in tuition)
        ],
    )


def expense(row, beneficiary):
    return dict(
        id=f"expense_{row.id}",
        provenance=row.provenance,
        beneficiary=beneficiary,
        paid=row.date,
        amount=row.amount,
        tax_free_aid=0,
        credit_expenses=0,
        other_vehicle_expenses=0,
        eligibility="confirmed_higher_education",
    )


def uses(tuition, identity):
    return [
        dict(expense=f"expense_{r.id}", amount=r.amount) for r in tuition if r.source == identity
    ]


def opening_accounts(scenario, balances, basis):
    terms = {a.account_id: a for a in scenario.education_plan.accounts}
    accounts = []
    for account in scenario.accounts:
        if account.wrapper == "education":
            term = terms[account.id]
            accounts.append(
                dict(
                    **account.model_dump(exclude={"balance"}),
                    balance=balances[account.id] if balances is not None else account.balance,
                    zero_value_basis_history_confirmed=basis is not None,
                    beneficiary=term.beneficiary,
                    plan=term.plan,
                    contribution_basis=(
                        basis[account.id] if basis is not None else term.contribution_basis
                    ),
                )
            )
    return accounts
