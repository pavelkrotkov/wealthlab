"""Targets cannot silently liquidate an omitted position or duplicate a decision."""

from wealthlab.portfolio.household_policies import month_end


def validate(plan):
    case = plan.case
    policies = plan.rebalances
    accounts = {a.id for a in case.accounts}
    securities = {s.id for s in case.securities}
    validate_ids(case, policies)
    keys = [(p.date, p.account_id) for p in policies]
    if len(set(keys)) != len(keys) or keys != sorted(keys):
        raise ValueError("Order rebalances by date/account, once per account per date.")
    for policy in policies:
        validate_policy(policy, case, accounts, securities)


def validate_ids(case, policies):
    identifiers = [p.id for p in policies]
    existing = {
        r.id
        for group in (case.lots, case.trades, case.sale_policies, case.harvest_policies)
        for r in group
    }
    if len(set(identifiers)) != len(identifiers) or existing.intersection(identifiers):
        raise ValueError("Rebalance IDs must be unique and distinct from lots and other orders.")


def validate_policy(policy, case, accounts, securities):
    if policy.provenance == "unresolved":
        raise ValueError("Resolve rebalance assumptions before projecting.")
    if not case.as_of <= policy.date <= case.end or policy.date != month_end(policy.date):
        raise ValueError("Rebalances require month-end dates inside the household horizon.")
    if policy.account_id not in accounts or not policy.target_weights.keys() <= securities:
        raise ValueError("Rebalance targets require known linked accounts and securities.")
    if sum(policy.target_weights.values()) != 1:
        raise ValueError("Rebalance target weights must sum exactly to one.")
    validate_holdings(policy, case)


def validate_holdings(policy, case):
    required = {
        r.security_id for r in (*case.lots, *case.trades) if r.account_id == policy.account_id
    }
    required.update(
        p.replacement_id for p in case.harvest_policies if p.account_id == policy.account_id
    )
    if not required <= policy.target_weights.keys():
        raise ValueError(
            "Give every account holding/purchase an explicit rebalance weight, even zero."
        )
