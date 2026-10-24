"""Outflow restrictions have explicit half-open boundaries and retain their real horizon."""

from datetime import date

from wealthlab.retirement.account_liquidity import AccountLock, annual
from wealthlab.retirement.distribution_example import synthetic
from wealthlab.retirement.distribution_inputs import DistributionCase
from wealthlab.retirement.distributions import run


def test_a_lock_ending_on_the_withdrawal_date_does_not_block_it():
    data = synthetic().model_dump(mode="json")
    data["liquidity_locks"] = [
        dict(
            id="lock",
            provenance="assumption",
            account_id="ira",
            start="2026-01-01",
            end="2026-06-01",
        )
    ]
    result = run(DistributionCase.model_validate(data))
    assert result["orders"][0]["paid"] == 10000
    assert not result["orders"][0]["blocked_by_liquidity"]


def test_annual_compilation_clips_without_extending_a_cross_year_lock():
    lock = AccountLock(
        id="lock",
        provenance="assumption",
        account_id="ira",
        start=date(2026, 11, 1),
        end=date(2027, 2, 1),
    )
    first, second = annual([lock], 2026)[0], annual([lock], 2027)[0]
    assert (first.start, first.end) == (date(2026, 11, 1), date(2027, 1, 1))
    assert (second.start, second.end) == (date(2027, 1, 1), date(2027, 2, 1))
    assert lock.start == date(2026, 11, 1)
