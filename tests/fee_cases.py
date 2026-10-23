"""Independent synthetic fee contracts with explicit ten-day valuation periods."""

from test_harvest_comparison import harvest_case


def fee_schedule(**changes):
    result = dict(
        id="advice",
        provenance="assumption",
        kind="advisor",
        account_ids=["brokerage"],
        annual_rate="0.365",
        fixed_per_period="5",
        payment_account="brokerage",
        periods=[dict(start="2026-01-01", date="2026-01-11", prices={"STOCK": "10", "ETF": "10"})],
    )
    return dict(result, **changes)


def fee_case():
    payload = harvest_case()
    payload.update(harvest_policies=[], compare_harvesting=False, terminal_exit=None)
    payload["fee_schedules"] = [fee_schedule()]
    return payload
