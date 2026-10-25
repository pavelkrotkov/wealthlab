"""Threaded changing STD ratios/credits cannot leak into another prepared or ordinary return.

Each continuous ratio derives from new positive wages and a complete worldwide
100,000 denominator. The supported amounts avoid refundable-credit residence
questions. Every invocation must restore original policy and record arrays,
while one dedicated per-year calculator handles all these distinct ratios.
"""

from decimal import Decimal

from pr_execution_helpers import annual

from wealthlab.tax import federal
from wealthlab.tax.facts import Deductions
from wealthlab.tax.foreign_credit_facts import ForeignCredits
from wealthlab.tax.pr_execution_context import prepare
from wealthlab.tax.pr_federal import calculate


def test_continuous_ratio_thread_calls_reset_native_credits_and_isolate_ordinary_policy():
    from concurrent.futures import ThreadPoolExecutor

    from wealthlab.tax.pr_federal_engine import engine

    case, _ = prepare(annual())
    world = case.baseline
    ordinary_before = federal.calculate(
        world.filing, world.federal_income, Deductions(), world.policy
    )
    scenarios = []
    for amount, claimed in [("43215.67", "100"), ("87654.32", "1000"), ("50000", "0")]:
        one = case.income[0].model_copy(update=dict(federal_amount=Decimal(amount)))
        two = case.income[1].model_copy(update=dict(federal_amount=100000 - Decimal(amount)))
        changed = case.model_copy(update=dict(income=[one, two]))
        credit = ForeignCredits(
            regular=Decimal(claimed), eligibility="allowed", source="Synthetic fact"
        )
        scenarios.append((changed, [one], credit))

    def run(values):
        changed, rows, credit = values
        return calculate(changed, rows, [], native_credits=credit)

    run(scenarios[0])
    misses = engine.cache_info().misses
    expected = [run(item) for item in scenarios]
    with ThreadPoolExecutor(max_workers=3) as pool:
        actual = list(pool.map(run, scenarios * 2))
    ordinary_after = federal.calculate(
        world.filing, world.federal_income, Deductions(), world.policy
    )
    assert actual == expected * 2
    assert engine.cache_info().misses == misses
    assert ordinary_before == ordinary_after
    assert [r["foreign_tax_credit"] for r in actual[:3]] == [100, 1000, 0]
