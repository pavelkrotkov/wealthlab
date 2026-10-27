"""Cash-only paths may retain dormant zero taxable accounts, never unbound investments.

Cash earns no invented factor return. Confirmed cash character and other-return
scope remain mandatory; inflation and guardrails still use their actual paths.
An unfunded dormant account cannot accept scheduled contributions or hide an
active native investment book merely because its opening balance is zero.
"""

CASH_PLANS = {
    "tax_plan",
    "foreign_tax_plan",
    "employment_plan",
    "social_work_plan",
    "medicare_plan",
    "advisory_fee_plan",
}


def cash_only(scenario):
    dormant = {a.id for a in scenario.accounts if a.wrapper != "cash"}
    accounts_safe = all(safe_account(a) for a in scenario.accounts)
    active = any(active_book(scenario, name) for name in type(scenario).model_fields)
    scheduled = any(c.destination in dormant for c in scenario.contributions)
    return accounts_safe and not active and not scheduled


def safe_account(account):
    return account.wrapper == "cash" or (account.wrapper == "taxable" and account.balance == 0)


def active_book(scenario, name):
    return name.endswith("_plan") and name not in CASH_PLANS and getattr(scenario, name) is not None
