"""Source property marks and actual escrow close share native assets, debt and tax books.

Only execution state and audit are local. Wallet.balances and the original
mutable household debt dictionary remain the sole financial balances.
"""

from decimal import Decimal

from wealthlab.household.property_close import execute
from wealthlab.household.property_validation import validate

ZERO = Decimal(0)
FIELDS = ("gross_proceeds", "closing_costs", "owner_cash_paid", "cash_received")


class Ledger:
    def __init__(self, scenario, debt_balances):
        validate(scenario)
        if debt_balances is None:
            raise ValueError("Property requires the actual mutable household debt balances.")
        self.scenario, self.debt_balances = scenario, debt_balances
        self.plan = scenario.property_plan
        self.states = {
            h.id: dict(
                closed=False,
                blocked=False,
                federal_basis=h.opening_federal_basis,
                nj_basis=h.opening_nj_basis,
            )
            for h in self.plan.holdings
        }
        self.month, self.log, self.summary = 0, [], {}

    def after_receipts(self, wallet, start, end):
        monthly, events = [], []
        for holding in self.plan.holdings:
            state = self.states[holding.id]
            observation = holding.observations[self.month]
            if state["closed"]:
                continue
            wallet.balances[holding.account_id] = observation.value
            if holding.sale is not None and holding.sale.date == observation.date:
                record, taxes = execute(
                    holding,
                    state,
                    self.scenario,
                    self.debt_balances,
                    wallet,
                    observation,
                    start,
                    end,
                )
                monthly.append(record)
                events.extend(taxes)
        self.log.extend(monthly)
        self.summary = summarize(monthly, self.states)
        self.month += 1
        return events

    def observe(self, row):
        positions = []
        for holding in self.plan.holdings:
            value = row["account_balances"][holding.account_id]
            debt = sum((row["debt_balances"][key] for key in holding.linked_debt_ids), ZERO)
            positions.append(
                dict(
                    account_id=holding.account_id,
                    terminal_action=holding.terminal_action,
                    gross_value=value,
                    linked_debt_balance=debt,
                    net_equity=value - debt,
                    **self.states[holding.id],
                )
            )
        return dict(property_positions=positions)

    def finish(self, rows):
        rows[-1]["property_audit"] = dict(
            inputs=self.plan.model_dump(mode="json"),
            closing_events=self.log,
            economic_state=rows[-1]["property_positions"],
            automatic_exclusion_calculation=False,
            automatic_mortgage_interest_deduction=False,
            cash_scope="Existing household cash only; no new borrowing or hypothetical payoff",
            blocked_close_costs_posted=False,
        )


def summarize(records, states):
    executed = [r for r in records if r["executed"]]
    liens = [d for r in executed for d in r["liens"]]
    return dict(
        property_product_failure=any(s["blocked"] for s in states.values()),
        property_closing_events=records,
        **{"property_" + key: total(executed, key) for key in FIELDS},
        property_debt_principal_paid=total(liens, "principal"),
        property_debt_interest_paid=total(liens, "interest"),
        property_closing_cash_shortfall=total(records, "closing_cash_shortfall"),
    )


def attach(books, scenario, debt_balances):
    if scenario.property_plan is None:
        return None
    ledger = Ledger(scenario, debt_balances)
    books.append(ledger)
    return ledger


def observe(products, row):
    ledger = getattr(products, "property_book", None)
    return ledger.observe(row) if ledger else {}


def total(records, key):
    return sum((r.get(key, ZERO) for r in records), ZERO)
