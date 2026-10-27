"""Create one actual liquid benchmark share book, preserving supplied opening tax bases."""

from decimal import ROUND_DOWN, Decimal

from wealthlab.household.calendar import money
from wealthlab.portfolio.book import Book
from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.models import Lot, Security, TradingAccount

SECURITY = "drilling_reference_security"


def opening(plan, scenario):
    value = plan.opening_cash + plan.opening_property_value
    quantity = (value / plan.opening_reference_price).quantize(
        Decimal(".000001"), rounding=ROUND_DOWN
    )
    invested = money(quantity * plan.opening_reference_price)
    residual = value - invested
    if residual > min(plan.opening_federal_basis, plan.opening_nj_basis):
        raise ValueError("Opening reference cash rounding exceeds supplied tax basis.")
    lots = (
        [
            Lot(
                id="drilling_reference_opening",
                provenance="illustration",
                account_id=plan.account_id,
                security_id=SECURITY,
                acquired=scenario.start,
                federal_holding_start=scenario.start,
                liquid_after=scenario.start,
                quantity=quantity,
                federal_basis=plan.opening_federal_basis - residual,
                nj_basis=plan.opening_nj_basis - residual,
            )
        ]
        if quantity
        else []
    )
    case = LotCase(
        as_of=scenario.start,
        end=scenario.end,
        accounts=[
            TradingAccount(
                id=plan.account_id,
                provenance="assumption",
                owner="primary",
                wrapper="taxable",
                cash=value - invested,
            )
        ],
        securities=[
            Security(
                id=SECURITY,
                provenance="illustration",
                wash_group=SECURITY,
                kind="etf",
                exposure_group=SECURITY,
            )
        ],
        lots=lots,
        trades=[],
        closing_prices={SECURITY: plan.opening_reference_price},
        federal_wash_tracking=True,
        opening_wash_context_complete=True,
        nj_wash_treatment=plan.reference_nj_wash_treatment,
    )
    return case, Book(case)
