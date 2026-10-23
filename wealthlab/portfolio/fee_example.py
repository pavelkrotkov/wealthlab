"""Synthetic manager fees apply only to the replacement sleeve actually owned."""

from wealthlab.portfolio.fee_inputs import FeeSchedule
from wealthlab.portfolio.harvest_example import synthetic as harvest_example


def synthetic():
    fee = FeeSchedule.model_validate(
        dict(
            id="manager_fee",
            provenance="assumption",
            kind="manager",
            account_ids=["brokerage"],
            security_ids=["ETF"],
            annual_rate="0.01",
            payment_account="brokerage",
            periods=[
                dict(
                    start="2026-06-01",
                    date="2026-12-01",
                    prices={"STOCK": "10", "ETF": "10"},
                )
            ],
        )
    )
    return harvest_example().model_copy(update={"fee_schedules": [fee]})
