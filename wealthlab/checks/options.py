"""Compare QuantLib with a separate standard-library Black-Scholes calculation."""

from math import erf, exp, sqrt
from threading import Lock

import QuantLib as ql

# ponytail: one process-wide valuation date; isolate workers if pricing becomes parallel.
VALUATION_LOCK = Lock()


def price() -> float:
    """One-year ATM European call: spot/strike 100, rate 4%, volatility 20%."""
    with VALUATION_LOCK, ql.SavedSettings():
        start, end = ql.Date(1, 1, 2025), ql.Date(1, 1, 2026)
        ql.Settings.instance().evaluationDate = start
        day_count = ql.Actual365Fixed()
        risk_free = ql.YieldTermStructureHandle(ql.FlatForward(start, 0.04, day_count))
        dividend = ql.YieldTermStructureHandle(ql.FlatForward(start, 0.0, day_count))
        vol = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(start, ql.NullCalendar(), 0.2, day_count)
        )
        process = ql.BlackScholesMertonProcess(
            ql.QuoteHandle(ql.SimpleQuote(100.0)), dividend, risk_free, vol
        )
        option = ql.VanillaOption(
            ql.PlainVanillaPayoff(ql.Option.Call, 100.0), ql.EuropeanExercise(end)
        )
        option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
        return float(option.NPV())


def cases() -> list[tuple[str, float, float]]:
    d1, d2 = 0.3, 0.1
    normal_d1 = 0.5 * (1 + erf(d1 / sqrt(2)))
    normal_d2 = 0.5 * (1 + erf(d2 / sqrt(2)))
    expected = 100 * normal_d1 - 100 * exp(-0.04) * normal_d2
    return [("European option independent valuation", price(), expected)]
