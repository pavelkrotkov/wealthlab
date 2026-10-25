"""Preflight all closing obligations before mutating the one wallet or actual debt balances.

Gross escrow proceeds cannot fund unrelated spending. A failed close posts no
cost or tax, while ordinary debt service remains responsible for its live debt.
"""

from decimal import Decimal

from wealthlab.household.debts import payment
from wealthlab.tax.facts import FederalIncome
from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.projection_inputs import TaxEvent

ZERO = Decimal(0)


def quote(holding, scenario, debt_balances, start, end):
    debts = {d.id: d for d in scenario.debts}
    liens = [
        dict(
            debt_id=key,
            principal=debt_balances[key],
            interest=payment(debts[key], debt_balances[key], scenario, start, end)[0],
        )
        for key in holding.linked_debt_ids
    ]
    payoff = sum((d["principal"] + d["interest"] for d in liens), ZERO)
    obligations = holding.sale.closing_costs + payoff
    return dict(
        liens=liens,
        payoff=payoff,
        owner_required=max(ZERO, obligations - holding.sale.gross_proceeds),
        net_proceeds=max(ZERO, holding.sale.gross_proceeds - obligations),
    )


def execute(holding, state, scenario, debt_balances, wallet, observation, start, end):
    sale = holding.sale
    closing = quote(holding, scenario, debt_balances, start, end)
    required = closing["owner_required"]
    available = min(wallet.cash, sale.maximum_owner_cash_to_close)
    blocked = observation.locked or required > available
    record = dict(
        account_id=holding.account_id,
        date=sale.date.isoformat(),
        requested=True,
        executed=not blocked,
        locked=observation.locked,
        owner_cash_required=required,
        closing_cash_shortfall=max(ZERO, required - available),
        **closing,
    )
    if blocked:
        state["blocked"] = True
        return record, ()
    # No callback/yield can change available cash between preflight and commit.
    if wallet.pay(required) != required:
        raise ValueError("Property close cannot consume unavailable owner cash.")
    for debt in closing["liens"]:
        debt_balances[debt["debt_id"]] = ZERO
    wallet.balances[holding.account_id] = ZERO
    wallet.deposit(closing["net_proceeds"])
    state.update(closed=True, federal_basis=ZERO, nj_basis=ZERO)
    record.update(
        gross_proceeds=sale.gross_proceeds,
        closing_costs=sale.closing_costs,
        owner_cash_paid=required,
        cash_received=closing["net_proceeds"],
        federal_taxable_gain=sale.federal_taxable_gain,
        nj_taxable_gain=sale.nj_taxable_gain,
    )
    event = TaxEvent(
        date=sale.date,
        description="Executed supplied property sale " + holding.id,
        cash_received=0,
        federal=FederalIncome(**{sale.federal_character: sale.federal_taxable_gain}),
        new_jersey=NJIncome(dispositions=sale.nj_taxable_gain),
    )
    return record, (event,)
