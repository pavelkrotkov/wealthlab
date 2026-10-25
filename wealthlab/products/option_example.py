"""Original invented contracts/prices, independent of any adviser or actual account."""

from wealthlab.portfolio.example import synthetic as lot_example
from wealthlab.products.option_inputs import OptionCase


def synthetic(strategy="Four-leg synthetic exposure"):
    holdings = lot_example().model_dump(mode="json")
    holdings.update(as_of="2025-01-01", end="2026-01-01", trades=[])
    holdings["accounts"][0]["cash"] = "10000"
    specs = [("stock_call", "STOCK", "call", "short", "110", "6")]
    if strategy != "Covered call":
        specs.append(("stock_put", "STOCK", "put", "long", "90", "4"))
    if strategy == "Four-leg synthetic exposure":
        specs.extend(
            [
                ("index_call", "INDEX", "call", "long", "100", "10"),
                ("index_put", "INDEX", "put", "short", "100", "6"),
            ]
        )
    legs = make_legs(specs)
    marks = [
        dict(
            date=day,
            stock=stock,
            index=index,
            rate=0.04,
            stock_vol=0.2,
            index_vol=0.2,
            stock_yield=0,
            index_yield=0,
            source="Invented scenario spots; QuantLib model option values, no historical quotes",
        )
        for day, stock, index in [
            ("2025-01-01", "100", "100"),
            ("2025-06-01", "95", "105"),
            ("2025-12-31", "79", "119"),
            ("2026-01-01", "80", "120"),
        ]
    ]
    return OptionCase.model_validate(
        dict(
            holdings=holdings,
            legs=legs,
            marks=marks,
            outside_cash="5000",
            allow_settlement_loan=False,
            settlement_loan_annual_rate=0.06,
            short_collateral_fraction="0.2",
            cover_stock_calls=True,
            cash_secure_puts=True,
            stock_sale_fee="1",
            unwind=True,
            dividends=[dict(ex_date="2025-06-01", pay_date="2025-06-01", per_share="1")],
        )
    )


def make_legs(specs):
    return [
        dict(
            id=name,
            provenance="illustration",
            underlying=underlying,
            kind=kind,
            side=side,
            strike=strike,
            premium=premium,
            contracts=1,
            multiplier=100,
            opening_fee="1",
            closing_fee="1",
            opened="2025-01-01",
            expiry="2026-01-01",
            style="european",
            settlement="physical" if underlying == "STOCK" else "cash",
            expiry_rule="exercise_if_itm",
            federal_class="capital",
            federal_character="short_term",
        )
        for name, underlying, kind, side, strike, premium in specs
    ]
