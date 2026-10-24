"""A synthetic matched recovery demonstrates temporary deferral versus complete-exit tax."""

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.example import synthetic as lot_example
from wealthlab.tax.annual import synthetic as tax_example


def synthetic():
    payload = lot_example().model_dump(mode="json")
    annual = tax_example().model_dump(mode="json")
    annual["policy"].update(year=2026, mode="freeze_2025")
    annual["nj_regime"] = "freeze_2025"
    payload.update(
        federal_wash_tracking=True,
        opening_wash_context_complete=True,
        nj_wash_treatment="federal_rules",
        lot_tax_cases=[annual],
        trades=[],
        compare_harvesting=True,
    )
    payload["lots"][0].update(federal_basis="1000", nj_basis="1000", economic_basis="1000")
    payload["securities"].append(
        dict(payload["securities"][0], id="ETF", wash_group="ETF", kind="etf")
    )
    payload["closing_prices"] = {"STOCK": "10", "ETF": "10"}
    payload["harvest_policies"] = [
        dict(
            id="harvest",
            provenance="assumption",
            date="2026-06-01",
            account_id="brokerage",
            security_id="STOCK",
            replacement_id="ETF",
            replacement_eligible=True,
            prices={"STOCK": "7.5", "ETF": "7.5"},
        )
    ]
    payload["terminal_exit"] = dict(account_ids=["brokerage"], no_replacements_next30_days=True)
    return LotCase.model_validate(payload)
