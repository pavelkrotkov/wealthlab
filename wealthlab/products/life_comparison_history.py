"""Preserve existing financial policy history while allowing genuinely new zero-cost cover.

Surrender equity alone is insufficient: an underwater or fully loaned policy can
still have taxable gain. Opening loans, cost and gross values therefore determine
whether a policy's existing history must be carried into every alternative.
"""

EXCLUDED = {
    "events",
    "values",
    "stop_funding_date",
    "name",
    "source",
    "source_date",
    "id",
    "provenance",
    "values_match_executed_events_confirmed",
}


def history(scenario):
    return {
        h.account_id: dict(
            opening=h.opening_values.model_dump(), contract=h.contract.model_dump(exclude=EXCLUDED)
        )
        for h in scenario.life_plan.holdings
        if existing(h)
    }


def existing(holding):
    return any(
        value != 0
        for value in (
            holding.contract.opening_loan,
            holding.contract.opening_federal_basis,
            holding.opening_values.gross_cash_value,
            holding.opening_values.gross_surrender_value,
        )
    )
