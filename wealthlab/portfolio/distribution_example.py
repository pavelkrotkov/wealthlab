"""A synthetic partial sale demonstrates dividend holding-day qualification."""

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.harvest_example import synthetic as harvest_example


def synthetic():
    payload = harvest_example().model_dump(mode="json")
    payload.update(
        lots=[],
        harvest_policies=[],
        compare_harvesting=False,
        terminal_exit=None,
        price_only_marks_confirmed=True,
    )
    common = dict(
        provenance="assumption",
        account_id="brokerage",
        security_id="STOCK",
        price="10",
        commission="0",
    )
    payload["trades"] = [
        dict(common, id="purchase", action="buy", date="2026-05-15", quantity="100"),
        dict(common, id="partial_sale", action="sell", date="2026-06-10", quantity="40"),
    ]
    payload["distributions"] = [
        dict(
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
    ]
    return LotCase.model_validate(payload)
