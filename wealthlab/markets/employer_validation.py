"""Require explicit employer terms; a return factor cannot supply tax allocations."""

from wealthlab.employment.compensation_validation import validate as validate_compensation
from wealthlab.markets.employer_links import unique_links
from wealthlab.markets.employer_links import validate as validate_link


def validate(scenario, batch, binding):
    if not binding.employers:
        return
    if scenario.compensation_plan is None:
        raise ValueError("Employer market bindings need an existing compensation plan.")
    validate_compensation(scenario)
    identities = [b.account_id for b in binding.employers]
    if len(identities) != len(set(identities)):
        raise ValueError("Bind each employer account once.")
    unique_links(binding.employers)
    accounts = {a.id: a for a in scenario.accounts}
    for item in binding.employers:
        validate_account(scenario, batch, item)
        if item.employment:
            validate_link(scenario, item, accounts[item.account_id])


def validate_account(scenario, batch, item):
    plan = scenario.compensation_plan
    if item.account_id not in {t.account for t in plan.tranches}:
        raise ValueError("Employer market bindings need an existing compensation account.")
    validate_factor(batch, item.factor)
    if not item.replace_entered_net_returns_confirmed:
        raise ValueError("Confirm replacement of entered employer net returns.")


def validate_factor(batch, identity):
    if identity not in batch.assets:
        raise ValueError("Unknown employer market factor.")
    factor = batch.assets.index(identity)
    if batch.metadata["input"]["assets"][factor]["role"] != "employer":
        raise ValueError("Employer bindings require an explicitly designated employer factor.")
    if (batch.cash_yields[:, :, factor] != 0).any():
        raise ValueError("Employer net-return factors need zero separate cash yield.")
