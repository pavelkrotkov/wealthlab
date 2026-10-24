"""Keep workplace accounts distinct from IRA pools and generic cash transfers.

Wrapper names describe tax character, not the product. Explicit IDs prevent
401(k) balances from entering ordinary-IRA pro-rata calculations or taxable
sales. No employer match or employer-funded vesting is inferred here.
"""


def validate_products(scenario):
    plan = scenario.workplace_plan
    accounts = {a.id: a for a in scenario.accounts}
    if not plan.products or set(plan.products) - set(accounts):
        raise ValueError("Classify known employee 401(k) accounts.")
    for aid, product in plan.products.items():
        validate_account(accounts[aid], product, {m.id for m in scenario.members})
    validate_exclusions(scenario, plan)


def validate_account(account, product, members):
    wrapper = "traditional" if product == "pretax_401k" else "roth"
    if account.owner not in members:
        raise ValueError("Employee 401(k) accounts need an individual household owner.")
    if account.wrapper != wrapper or account.currency != "USD" or account.monthly_fee:
        raise ValueError("Employee 401(k) accounts need matching USD wrappers without fees.")


def validate_exclusions(scenario, plan):
    if scenario.ira_plan and set(plan.products) & set(scenario.ira_plan.products):
        raise ValueError("An account cannot be both an ordinary IRA and a workplace plan.")
    if any(c.destination in plan.products for c in scenario.contributions):
        raise ValueError("Remove generic transfers into employee-deferral accounts.")
    if any(s.account_id in plan.products for s in scenario.tax_plan.funding_sources):
        raise ValueError("Employee plan accounts cannot be taxable funding sources.")
