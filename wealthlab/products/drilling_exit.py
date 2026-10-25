"""A conditional full cash exit retains debt and separates ordinary recapture from capital gain.

Recapture capacity and character are supplied assumptions, not a section 1254
eligibility calculation. All modeled creditors must be paid before a completed
exit; a blocked attempt cannot silently cancel a household recourse obligation.
Positive recognition survives a loss in the other jurisdiction.
"""

from wealthlab.products import drilling_cash as cash
from wealthlab.products.drilling_tax import ordinary_field
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_business import BusinessIncome
from wealthlab.tax.nj_facts import NJIncome


def execute(ledger, observation, wallet, row):
    if not ledger.property_sold:
        ledger.cash += observation.exit_gross_proceeds
        ledger.property_value = cash.ZERO
        ledger.property_sold = True
        ledger.owed["manager_fee"] += observation.exit_fee
        cash.pay_creditors(ledger)
    if sum(ledger.owed.values(), cash.ZERO) or ledger.call_owed:
        row["blocked_exit"] = True
        return []
    proceeds = ledger.cash
    federal_gain = proceeds - ledger.bases["federal"]
    nj_gain = proceeds - ledger.bases["nj"]
    events = recognition(ledger.plan, observation.date, federal_gain, nj_gain, ledger.bases)
    row.update(
        exit_cash=proceeds,
        federal_exit_gain=federal_gain,
        nj_exit_gain=nj_gain,
        federal_ordinary_recapture=min(
            max(cash.ZERO, federal_gain), ledger.plan.federal_recapture_limit
        ),
    )
    wallet.deposit(proceeds)
    ledger.cash = cash.ZERO
    ledger.bases = dict.fromkeys(ledger.bases, cash.ZERO)
    ledger.tangible_basis = dict.fromkeys(ledger.tangible_basis, cash.ZERO)
    ledger.closed = True
    return events


def recognition(plan, when, federal_gain, nj_gain, bases):
    from wealthlab.products.conditional_allocations import events
    from wealthlab.products.household_inputs import SleeveAllocation

    recapture = min(max(cash.ZERO, federal_gain), plan.federal_recapture_limit)
    residual = federal_gain - recapture
    if residual > 0 and not plan.residual_capital_niit_inclusion_assumed_confirmed:
        raise ValueError("Confirm residual capital NIIT treatment or supply another exit adapter.")
    fcap = min(
        *plan.federal_exit_loss_limits.model_dump().values(), bases["federal"], bases["at_risk"]
    )
    ncap = min(*plan.nj_exit_loss_limits.model_dump().values(), bases["nj"])
    if residual and plan.residual_federal_capital_character == "unconfirmed":
        raise ValueError("Supply the residual federal capital holding character before exit.")
    character = "long_term" if not residual else plan.residual_federal_capital_character
    federal = FederalIncome(**{ordinary_field(plan): recapture, character: max(residual, -fcap)})
    nj = new_jersey(plan, max(nj_gain, -ncap))
    item = SleeveAllocation(
        id="drilling_exit",
        provenance="assumption",
        date=when,
        federal=federal,
        new_jersey=nj,
        federal_loss=plan.federal_exit_loss_timing,
        new_jersey_loss=plan.nj_exit_loss_timing,
    )
    return events(item)


def new_jersey(plan, gain):
    if plan.nj_exit_category == "partnership":
        return NJIncome(business=BusinessIncome(partnership=gain))
    recapture = min(max(cash.ZERO, gain), plan.nj_recapture_limit)
    return NJIncome(business=BusinessIncome(partnership=recapture), dispositions=gain - recapture)
