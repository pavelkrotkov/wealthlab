"""Share the existing sale solver with required product payments in the active month.

A product can request cash only after the return has recognized preceding events.
Quotes retain actual withholding and the existing spending requirement. All sales
accumulate in one report even when several product payments precede ordinary bills.
"""

from decimal import Decimal

ZERO = Decimal(0)


def begin(ledger, amounts, required, start, end):
    ledger.funding_context = dict(
        amounts=amounts, required=required, period=(start, end), proceeds=ZERO, active=True
    )


def fund(ledger, wallet, additional, start, end):
    context = getattr(ledger, "funding_context", {})
    if not context.get("active") or context.get("period") != (start, end):
        raise ValueError("Required product funding needs the active household tax month.")
    if additional < 0:
        raise ValueError("Additional required cash cannot be negative.")
    required = context["required"]
    spending = required() if callable(required) else required
    sold = ledger.funding.fund(
        ledger, wallet, spending + additional, context["amounts"], start, end
    )
    context["proceeds"] += sold
    return sold


def finish(ledger):
    ledger.funding_context["active"] = False
    return ledger.funding_context["proceeds"]
