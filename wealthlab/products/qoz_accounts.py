"""A zero-opening QOZ account owns only its own calls, interests and receivables."""


def validate_account(scenario, plan):
    account = next((a for a in scenario.accounts if a.id == plan.account_id), None)
    if account is None or account.wrapper != "taxable" or account.currency != "USD":
        raise ValueError("QOZ needs a separately identified USD taxable account.")
    if account.balance or account.monthly_fee:
        raise ValueError("QOZ opens at zero; its fees and capital calls are modeled once.")
    validate_ownership(scenario, plan)
    validate_transfers(scenario, plan)


def validate_ownership(scenario, plan):
    linked = {a.id for a in scenario.lot_plan.case.accounts}
    if scenario.sleeve_plan:
        linked.update(s.account_id for s in scenario.sleeve_plan.sleeves)
    if scenario.exchange_fund_plan:
        linked.add(scenario.exchange_fund_plan.account_id)
    if scenario.option_plan:
        linked.add(scenario.option_plan.account_id)
    if scenario.drilling_plan:
        linked.add(scenario.drilling_plan.account_id)
    if plan.account_id in linked:
        raise ValueError("QOZ cannot share ownership with another product or linked-lot account.")


def validate_transfers(scenario, plan):
    if any(c.destination == plan.account_id for c in scenario.contributions):
        raise ValueError("Use QOZ calls instead of duplicating account contributions.")
    if any(s.account_id == plan.account_id for s in scenario.tax_plan.funding_sources):
        raise ValueError("A locked QOZ account cannot be an automatic tax-funding source.")
