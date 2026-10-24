"""Compile observed HSA marks, entitled cash income and dated sale restrictions.

Opening shares earn supplied monthly cash yield at the previous closing price.
Entitlement/payment/recognition occur on the first day, before that day's HSA
recipient orders. Closing prices are observable only on the final day. This is
an explicit scenario convention, not an issuer distribution calendar.
"""

from datetime import timedelta
from decimal import Decimal
from hashlib import sha256

from wealthlab.household.calendar import months

UNIT = Decimal(".00000001")


def compile_plan(payload, scenario, batch, binding, index):
    if not binding.hsa_securities:
        return
    linked = payload["hsa_plan"]["investments"]
    prices = dict(scenario.hsa_plan.investments.opening_prices)
    securities = {b.security_id: b for b in binding.hsa_securities}
    marks, distributions, locks = [], [], []
    for month, (start, end) in enumerate(months(scenario.start, scenario.end)):
        for security, item in securities.items():
            factor = batch.assets.index(item.factor)
            payment = cash_yield(item, prices[security], batch, index, month, factor, start)
            if payment is not None:
                distributions.append(payment)
            if batch.locked[month, factor]:
                locks.append(lock(security, month, start, end))
            rate = Decimal(str(1 + batch.mark_returns[index, month, factor]))
            prices[security] = (prices[security] * rate).quantize(UNIT)
        validate_prices(prices)
        marks.append(dict(date=end - timedelta(days=1), prices=dict(prices)))
    linked.update(marks=marks, liquidity_locks=locks)
    linked["case"].update(closing_prices=prices, distributions=distributions)
    validate_fee_marks(linked)


def cash_yield(item, price, batch, index, month, factor, when):
    rate = Decimal(str(batch.cash_yields[index, month, factor]))
    amount = (price * rate).quantize(UNIT)
    if amount == 0:
        return None
    return dict(
        id=generated_id("yield", month, item.security_id),
        provenance="assumption",
        security_id=item.security_id,
        ex_date=when,
        payment_date=when,
        recognition_date=when,
        per_share=amount,
        federal_character="interest" if item.nj_cash_character == "interest" else "dividends",
        nj_character=item.nj_cash_character,
    )


def lock(security, month, start, end):
    return dict(
        id=generated_id("lock", month, security),
        provenance="assumption",
        security_id=security,
        start=start,
        end=end,
    )


def validate_fee_marks(linked):
    # Fixed-dollar custody charges do not need market valuation. Variable fees
    # use supplied assessment-date marks, which must follow the same path.
    quotes = [(linked["case"]["as_of"], linked["opening_prices"])]
    quotes += [(str(m["date"]), m["prices"]) for m in linked["marks"]]
    for fee in linked["case"]["fee_schedules"]:
        for period in fee["periods"]:
            when = str(period["date"])
            current = next(prices for date, prices in reversed(quotes) if str(date) <= when)
            period["prices"] = dict(current)


def validate_prices(prices):
    if any(p <= 0 for p in prices.values()):
        raise ValueError("Zero-price HSA securities need a terminal write-off adapter.")


def generated_id(kind, month, security):
    return sha256(f"hsa_market_{kind}_{month}_{security}".encode()).hexdigest()
