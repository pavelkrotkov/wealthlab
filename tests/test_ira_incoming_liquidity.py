"""Outgoing withdrawal locks do not imply a custodian rejects incoming plan cash."""

from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run
from wealthlab.retirement.ira_rollover_example import synthetic


def test_an_outgoing_ira_lock_does_not_block_an_incoming_direct_transfer():
    """The existing lock restricts withdrawals; it is not an inbound custodian restriction."""
    data = synthetic().model_dump(mode="json")
    data["liquidity_locks"] = [
        dict(
            id="ira_lock",
            provenance="illustration",
            account_id="ira",
            start="2026-03-01",
            end="2027-01-01",
        )
    ]
    result = run(DistributionCase.model_validate(data))
    assert result["account_balances"]["ira"] == 30000
    assert result["cash"] == 0
    assert result["orders"][0]["blocked_by_liquidity"]
