"""Synthetic common-share distributions with independently configured cash and tax dates."""

from test_harvest_comparison import harvest_case


def distribution(**changes):
    event = dict(
        id="dividend",
        provenance="assumption",
        security_id="STOCK",
        ex_date="2026-06-01",
        payment_date="2026-06-15",
        recognition_date="2026-06-15",
        per_share="1",
        federal_character="dividends",
        nj_character="dividends",
        qualified_fraction="1",
        qualified_issuer_confirmed=True,
        undiminished_risk_confirmed=True,
    )
    return dict(event, **changes)


def distribution_case():
    payload = harvest_case()
    payload.update(
        harvest_policies=[],
        compare_harvesting=False,
        terminal_exit=None,
        price_only_marks_confirmed=True,
        distributions=[distribution()],
    )
    return payload


def trade(action, when, qty="100", price="10", **changes):
    result = dict(
        id=action,
        provenance="assumption",
        date=when,
        action=action,
        account_id="brokerage",
        security_id="STOCK",
        quantity=qty,
        price=price,
        commission="0",
    )
    return dict(result, **changes)
