"""Provided deduction facts are limited independently; no tax benefit becomes a cash receipt.

Actual funded costs and source-provided legal limits bound recognition. Basis
and at-risk reductions remain independently supplied and occur in their source
month; a deferred tax deduction can therefore retain a later recognition date.
"""

from decimal import Decimal

from wealthlab.products.conditional_allocations import event
from wealthlab.products.drilling_basis import funded_components
from wealthlab.products.drilling_basis_effects import apply as basis_effects
from wealthlab.products.drilling_limits import limited
from wealthlab.products.loss_timing import LossTiming
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_business import BusinessIncome
from wealthlab.tax.nj_facts import NJIncome

ZERO = Decimal(0)


def ordinary_field(plan):
    return (
        "allowed_nonpassive_partnership_income"
        if (plan.federal_ordinary == "nonpassive_assumption")
        else "allowed_passive_income"
    )


def ordinary(plan, when, amount, description):
    return event(
        when,
        description,
        FederalIncome(**{ordinary_field(plan): amount}),
        NJIncome(business=BusinessIncome(partnership=amount)),
    )


def losses(ledger, observation, row):
    plan = ledger.plan
    result, audit = [], []
    for item in observation.deductions:
        available = funded_components(ledger, item, observation, row)
        eligible = {
            key: min(getattr(item, key + "_requested"), amount) for key, amount in available.items()
        }
        records = []
        for jurisdiction in ("federal", "nj"):
            amount, choice, record = limited(ledger, item, jurisdiction, eligible[jurisdiction])
            result.extend(loss_event(plan, observation.date, item.id, jurisdiction, amount, choice))
            records.append(record)
        effects = basis_effects(ledger, item, available)
        for record in records:
            record["basis_effects"] = effects
        audit.extend(records)
    row["deduction_audit"] = audit
    return result


def loss_event(plan, when, identity, jurisdiction, amount, choice: LossTiming):
    if not amount or choice.treatment == "denied":
        return []
    if not choice.eligibility_after_limits_assumed:
        raise ValueError("Confirm drilling loss eligibility after independently supplied limits.")
    if choice.release_on is not None and choice.release_on <= when:
        raise ValueError("Deferred drilling loss release must follow its funded source date.")
    federal, nj = FederalIncome(), NJIncome()
    if jurisdiction == "federal":
        federal = FederalIncome(**{ordinary_field(plan): -amount})
    else:
        nj = NJIncome(business=BusinessIncome(partnership=-amount))
    return [event(choice.release_on or when, f"{identity}:{jurisdiction}", federal, nj)]
