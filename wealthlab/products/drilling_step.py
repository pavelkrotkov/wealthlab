"""Cash-basis operations recognize actual funded income and independently limited supplied losses.

Final noncash tax facts can arrive after an economic exit. Additional cash,
property or expense activity then requires a settlement adapter instead of
silently reopening the interest or inventing new contribution basis.
"""

from wealthlab.products import drilling_cash as cash
from wealthlab.products.conditional_allocations import event
from wealthlab.products.drilling_exit import execute as exit_interest
from wealthlab.products.drilling_exit import fund_sale
from wealthlab.products.drilling_reporting import snapshot
from wealthlab.products.drilling_tax import losses, ordinary
from wealthlab.tax.nj_facts import NJIncome


def step(ledger, observation, wallet):
    events = [
        event(
            observation.date,
            "Supplied drilling SE/QBI/AMT facts",
            observation.supplemental_federal,
            NJIncome(),
        )
    ]
    if ledger.closed:
        return closed(ledger, observation, wallet), events
    if ledger.property_sold and observation.residual_property_value:
        raise ValueError("A sold drilling property cannot reappear in later marks.")
    row = cash.operating(ledger, observation, wallet)
    fund_sale(ledger, observation, row)
    events.extend(operating_income(ledger, observation, row))
    events.extend(losses(ledger, observation, row))
    row["distribution"] = cash.distribute(ledger, observation.distribution_request, wallet)
    row["distribution_unfilled"] = observation.distribution_request - row["distribution"]
    if observation.exit_requested or ledger.property_sold:
        events.extend(exit_interest(ledger, observation, wallet, row))
    snapshot(ledger, wallet, row)
    return row, events


def closed(ledger, observation, wallet):
    values = [
        observation.capital_call,
        observation.production_units,
        observation.distribution_request,
        observation.residual_property_value,
        observation.exit_fee,
        observation.exit_gross_proceeds if observation.exit_requested else 0,
        *(getattr(observation, k) for k in cash.COSTS),
    ]
    if any(values) or observation.deductions:
        raise ValueError("Post-exit drilling cash/basis changes require a settlement adapter.")
    row = dict(
        date=observation.date.isoformat(),
        capital_call=0,
        call_funded=0,
        recourse_funded=0,
        call_owed=0,
        production_receipts=0,
        royalties=0,
        net_operating_income=0,
        distribution=0,
        distribution_unfilled=0,
        exit_cash=0,
        blocked_exit=False,
        paid_costs={},
    )
    snapshot(ledger, wallet, row)
    return row


def operating_income(ledger, observation, row):
    events = []
    for key in ledger.tangible_basis:
        ledger.tangible_basis[key] += row["paid_costs"]["tangible_cost"]
    if row["net_operating_income"] > 0:
        for key in ledger.bases:
            ledger.bases[key] += row["net_operating_income"]
        events.append(
            ordinary(
                ledger.plan,
                observation.date,
                row["net_operating_income"],
                "Actual cash-basis drilling operating income",
            )
        )
    return events
