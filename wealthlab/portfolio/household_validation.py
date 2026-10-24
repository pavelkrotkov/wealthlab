"""No second account value, duplicate seller or invented cash finances linked lots.

The initial profile links ordinary taxable trading accounts with manual trades.
It reuses both wash books, but year-end unresolved loss windows require a later
prior-return reconciliation adapter. Rejecting that profile avoids quietly
moving a December deduction into the next year's tax return.
"""

from datetime import timedelta
from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.portfolio.household_values import account_value
from wealthlab.portfolio.validation import validate as validate_lots


def validate(scenario):
    plan = scenario.lot_plan
    if scenario.tax_plan is None:
        raise ValueError("Linked household lots require explicit household taxes.")
    if not (
        plan.complete_ownership_and_outside_purchases_confirmed
        and plan.monthly_settlement_and_cash_sweep_confirmed
    ):
        raise ValueError("Confirm complete lot ownership/purchases and monthly cash sweep timing.")
    case = plan.case
    validate_lots(case)
    validate_scope(case)
    if (case.as_of, case.end) != (scenario.start, scenario.end - timedelta(days=1)):
        raise ValueError("Linked lot dates must match the household's inclusive/exclusive horizon.")
    validate_marks(plan, scenario)
    validate_accounts(plan, scenario)
    validate_sellers(plan, scenario)


def validate_scope(case):
    unsupported = (
        case.lot_tax_cases,
        case.sale_policies,
        case.harvest_policies,
        case.fee_schedules,
        case.distributions,
        case.compare_harvesting,
        case.terminal_exit,
    )
    if any(unsupported):
        raise ValueError(
            "This household lot profile supports manual trades and funding sales only."
        )
    if not case.federal_wash_tracking or case.nj_wash_treatment == "unconfirmed":
        raise ValueError("Linked lots require federal wash tracking and explicit NJ treatment.")
    if any(a.wrapper != "taxable" for a in case.accounts):
        raise ValueError(
            "This linked profile owns taxable lots; wrapper lots need another adapter."
        )


def validate_marks(plan, scenario):
    validate_price_keys(plan)
    expected = [end - timedelta(days=1) for _, end in months(scenario.start, scenario.end)]
    if [m.date for m in plan.monthly_marks] != expected:
        raise ValueError("Supply one ordered closing mark snapshot for every household month.")


def validate_price_keys(plan):
    securities = {s.id for s in plan.case.securities}
    if set(plan.opening_prices) != securities:
        raise ValueError("Supply opening marks for every linked security.")
    if any(set(m.prices) != securities for m in plan.monthly_marks):
        raise ValueError("Every closing snapshot needs all linked security marks.")
    if plan.monthly_marks[-1].prices != plan.case.closing_prices:
        raise ValueError("Final linked marks must match the lot case's closing marks.")


def validate_accounts(plan, scenario):
    accounts = {a.id: a for a in scenario.accounts}
    owners = dict(zip(("primary", "spouse"), [p.id for p in scenario.members], strict=False))
    owners["joint"] = "joint"
    for account in plan.case.accounts:
        if account.id not in accounts:
            raise ValueError("Every linked lot account must exist in the household.")
        actual = accounts[account.id]
        if (actual.wrapper, actual.currency, actual.owner, actual.monthly_fee) != (
            "taxable",
            "USD",
            owners.get(account.owner),
            Decimal(0),
        ):
            raise ValueError(
                "Linked lot owner, USD taxable wrapper and zero account fee must match."
            )
        value = account_value(plan.case.lots, account.id, account.cash, plan.opening_prices)
        if value != actual.balance:
            raise ValueError(
                "Household opening balance must equal linked lots plus brokerage cash."
            )


def validate_sellers(plan, scenario):
    accounts = {a.id for a in plan.case.accounts}
    validate_funding_permissions(plan, accounts)
    if any(s.account_id in accounts for s in scenario.tax_plan.funding_sources):
        raise ValueError("Remove the proportional-basis seller for linked lot accounts.")
    if any(c.destination in accounts for c in scenario.contributions):
        raise ValueError(
            "Use explicit share purchases instead of generic linked-account transfers."
        )


def validate_funding_permissions(plan, accounts):
    securities = {s.id for s in plan.case.securities}
    keys = [(s.account_id, s.security_id) for s in plan.funding_sources]
    if len(keys) != len(set(keys)):
        raise ValueError("Each linked account/security funding source must appear once.")
    if any(a not in accounts or s not in securities for a, s in keys):
        raise ValueError("Unknown linked account or security in funding permission.")
