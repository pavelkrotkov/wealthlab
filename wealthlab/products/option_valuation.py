"""QuantLib model marks are scenarios, never fabricated historical execution quotes."""

from decimal import Decimal

import QuantLib as ql

from wealthlab.checks.options import VALUATION_LOCK
from wealthlab.products.option_math import intrinsic


def value(leg, mark):
    spot = getattr(mark, leg.underlying.lower())
    if mark.date >= leg.expiry:
        return intrinsic(leg, spot)
    try:
        with VALUATION_LOCK, ql.SavedSettings():
            today = ql.Date(mark.date.day, mark.date.month, mark.date.year)
            end = ql.Date(leg.expiry.day, leg.expiry.month, leg.expiry.year)
            ql.Settings.instance().evaluationDate = today
            dc = ql.Actual365Fixed()
            rate = ql.YieldTermStructureHandle(ql.FlatForward(today, mark.rate, dc))
            div = ql.YieldTermStructureHandle(
                ql.FlatForward(today, getattr(mark, f"{leg.underlying.lower()}_yield"), dc)
            )
            vol = ql.BlackVolTermStructureHandle(
                ql.BlackConstantVol(
                    today, ql.NullCalendar(), getattr(mark, f"{leg.underlying.lower()}_vol"), dc
                )
            )
            process = ql.BlackScholesMertonProcess(
                ql.QuoteHandle(ql.SimpleQuote(float(spot))), div, rate, vol
            )
            exercise = (
                ql.EuropeanExercise(end)
                if leg.style == "european"
                else ql.AmericanExercise(today, end)
            )
            option = ql.VanillaOption(
                ql.PlainVanillaPayoff(
                    ql.Option.Call if leg.kind == "call" else ql.Option.Put, float(leg.strike)
                ),
                exercise,
            )
            engine = (
                ql.AnalyticEuropeanEngine(process)
                if leg.style == "european"
                else ql.BinomialVanillaEngine(process, "crr", 801)
            )
            option.setPricingEngine(engine)
            return Decimal(str(option.NPV()))
    except RuntimeError as error:
        raise ValueError(f"Unsupported QuantLib valuation assumptions: {error}") from error
