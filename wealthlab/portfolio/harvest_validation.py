"""A distinct ticker is not proof that a replacement is legally nonidentical."""

from wealthlab.portfolio.policy_validation import validate_decision, validate_snapshot


def validate_harvest(case):
    identities = {item.id for item in [*case.trades, *case.sale_policies]}
    for policy in case.harvest_policies:
        if policy.id in identities:
            raise ValueError("Harvest, sale-policy and trade IDs must be distinct.")
        identities.add(policy.id)
        validate_decision(case, policy)
        validate_snapshot(case, policy)
        validate_pair(case, policy)
    if case.harvest_policies and not case.federal_wash_tracking:
        raise ValueError("Harvesting requires household federal wash tracking.")


def validate_pair(case, policy):
    securities = {item.id: item for item in case.securities}
    accounts = {item.id: item for item in case.accounts}
    if policy.replacement_id not in securities:
        raise ValueError("Harvest replacement must reference a configured security.")
    source, replacement = securities[policy.security_id], securities[policy.replacement_id]
    if not policy.replacement_eligible or source.wash_group == replacement.wash_group:
        raise ValueError(
            "Confirm replacement eligibility and distinct substantially-identical groups."
        )
    validate_types(accounts[policy.account_id], source, replacement)


def validate_types(account, source, replacement):
    if account.wrapper != "taxable":
        raise ValueError(
            "Harvest policies require a taxable account, not a retirement distribution."
        )
    if source.kind == "collectible" or replacement.kind == "collectible":
        raise ValueError(
            "This stock/securities harvesting policy does not model collectible replacements."
        )
