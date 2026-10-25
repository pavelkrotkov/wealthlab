"""One HSA position book owns cash and assets; outside state/wash scope stays explicit.

Opening household values include the same positions exactly once. Recipient
withdrawals do not retax already recognized NJ investment income in this
conditional profile. Unknown historical basis remains a blocking input.
"""

from datetime import timedelta

from wealthlab.portfolio.household_values import account_value
from wealthlab.retirement.hsa_investment_validation import validate as validate_book


def validate(scenario):
    plan = scenario.hsa_plan
    if plan.investments is None:
        return
    investments = plan.investments
    validate_book(investments)
    if not (
        plan.cash_accounts_outside_investment_book_confirmed
        and plan.investment_income_excluded_from_other_inputs_confirmed
    ):
        raise ValueError("Confirm remaining cash HSAs and no duplicate HSA investment tax inputs.")
    if plan.cash_only_accounts_and_complete_context_confirmed:
        raise ValueError("An invested HSA cannot also be confirmed as a cash-only household.")
    if (investments.case.as_of, investments.case.end) != (
        scenario.start,
        scenario.end - timedelta(days=1),
    ):
        raise ValueError("Invested HSA dates must match the complete household horizon.")
    validate_accounts(scenario, investments)
    validate_withdrawals(plan, {a.id for a in investments.case.accounts})
    validate_outside_lots(scenario, investments)


def validate_accounts(scenario, plan):
    actual = {a.id: a for a in scenario.accounts}
    owners = dict(zip(("primary", "spouse"), [p.id for p in scenario.members], strict=False))
    for account in plan.case.accounts:
        household = actual.get(account.id)
        if household is None:
            raise ValueError("Each invested HSA must share its household account ID.")
        if (household.wrapper, household.currency, household.owner, household.monthly_fee) != (
            "hsa",
            "USD",
            owners.get(account.owner),
            0,
        ):
            raise ValueError(
                "Invested HSA owner, USD wrapper and separate custodian fees must match."
            )
        value = account_value(plan.case.lots, account.id, account.cash, plan.opening_prices)
        if household.balance != value:
            raise ValueError(
                "Household HSA opening value must equal its cash and marked positions."
            )


def validate_withdrawals(plan, accounts):
    rows = [(w.id, w.source) for w in plan.withdrawals]
    rows += [(b.id, b.hsa_source) for b in plan.medical_bills]
    if any(
        account in accounts and plan.nj_withdrawal_taxable_fractions.get(key, 0) != 0
        for key, account in rows
    ):
        raise ValueError("This NJ invested-HSA profile requires zero recipient taxable fractions.")


def validate_outside_lots(scenario, plan):
    if scenario.lot_plan is None:
        return
    groups = {s.wash_group for s in plan.case.securities}
    if any(s.wash_group in groups for s in scenario.lot_plan.case.securities):
        raise ValueError(
            "Identical outside securities need a separately validated HSA wash adapter."
        )
