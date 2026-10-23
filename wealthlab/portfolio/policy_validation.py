"""Validate decision inputs before replay can mutate any lots or account cash.

Each policy carries a complete snapshot. Reusing closing prices would give an
intermediate sale access to future valuations and invalidate matched comparisons.
"""


def validate_policies(case):
    ids = {item.id for item in case.trades}
    for policy in case.sale_policies:
        if policy.id in ids:
            raise ValueError("Policy and trade IDs must be distinct.")
        ids.add(policy.id)
        validate_decision(case, policy)
        validate_snapshot(case, policy)


def validate_decision(case, policy):
    if policy.provenance == "unresolved":
        raise ValueError("Resolve sale-policy assumptions before calculating.")
    if not case.as_of <= policy.date <= case.end:
        raise ValueError("Policy dates must lie inside the opening/closing dates.")


def validate_snapshot(case, policy):
    accounts = {item.id for item in case.accounts}
    securities = {item.id for item in case.securities}
    if policy.account_id not in accounts or policy.security_id not in securities:
        raise ValueError("Every policy must reference a configured account and security.")
    if set(policy.prices) != securities:
        raise ValueError("Each policy needs its own current price for every security.")
