"""Export all economic, tax and contract evidence without reusing cash as a tax saving."""

from wealthlab.products.option_deferrals import validate as validate_deferrals
from wealthlab.products.option_exit_state import evidence
from wealthlab.products.option_recognition import recognition
from wealthlab.products.option_tax_rows import stock_recognition


def report(state, held, leg_rows):
    case = state.case
    tax = recognition(state) + stock_recognition(state)
    validate_deferrals(case.tax, tax)
    opening = case.holdings.accounts[0].cash + case.outside_cash
    opening += sum(lot.quantity for lot in case.holdings.lots) * case.marks[0].stock
    return dict(
        opening_wealth=opening,
        economic_gain=state.rows[-1]["wealth"] - opening,
        scope="Conditional synthetic accounting; model marks are not history or guaranteed floors.",
        rows=state.rows,
        legs=leg_rows,
        terminations=list(state.closed.values()),
        tax=tax,
        disposals=state.book.disposals,
        cash_movements=state.cash_movements,
        failures=state.failures,
        held=held,
        ending=state.rows[-1],
        lots=[lot.model_dump(mode="json") for lot in state.book.lots.values()],
        open_legs=list(state.active),
        assumptions=case.model_dump(mode="json"),
        exit_state=evidence(state, case.holdings.end),
    )
