"""Separate protection has priced premiums and no investment or terminal cash value.

A pre-existing investment policy instead needs a supplied opening surrender;
its actual loan satisfaction and income recognition use the same contract book.
"""

from wealthlab.products.life_contract_tax import TERMINAL


def validate_reference(case, scenario):
    term = set(case.term_account_ids)
    holdings = {h.account_id: h for h in scenario.life_plan.holdings}
    if len(term) != len(case.term_account_ids) or not term <= set(holdings):
        raise ValueError("Term account IDs must name unique reference policy holdings.")
    for identity, holding in holdings.items():
        if identity in term:
            validate_term(holding)
        else:
            validate_exit(holding, scenario.start)


def validate_term(holding):
    contract = holding.contract
    amounts = [contract.opening_loan, contract.opening_federal_basis]
    for value in [holding.opening_values, *contract.values]:
        amounts.extend((value.gross_cash_value, value.gross_surrender_value))
    if any(amount != 0 for amount in amounts):
        raise ValueError(
            "Separately priced term protection must have zero cash/loan/opening basis."
        )
    validate_term_events(contract.events)
    if any(f.event.amount != 0 for f in holding.failure_exits.values()):
        raise ValueError("A term failure cannot produce a cash settlement.")


def validate_term_events(events):
    if any(e.kind not in {"premium", "external_fee", *TERMINAL} for e in events):
        raise ValueError("The term reference cannot include investment receipts or policy loans.")
    if any(e.amount != 0 for e in events if e.kind in TERMINAL):
        raise ValueError("A term reference cannot create a terminal cash value.")


def validate_exit(holding, start):
    events = holding.contract.events
    if len(events) != 1 or events[0].kind not in TERMINAL or events[0].date != start:
        raise ValueError(
            "Existing investment policies need an actual opening exit in the reference."
        )
    if events[0].amount != holding.opening_values.gross_surrender_value:
        raise ValueError("Reference exit must use the supplied opening surrender settlement.")
