"""Guardrail cuts use observed wealth, preserve essentials and expose lifestyle reductions.

The synthetic price loss occurs during month one, so its first discretionary
bill remains $1k. Later observed-wealth reviews cut it once to $800, without
compounding. The matched fixed-spending run provides the economic cost/benefit
comparison on the identical batch, with capital preserved by exactly the cuts.
"""

from tests.guardrail_cases import case
from wealthlab.markets.household_run import paired, run
from wealthlab.markets.paths import generate


def test_observed_drawdown_cuts_only_discretionary_and_reports_the_reduction():
    household, market, binding = case()
    batch = generate(market)
    guarded = run(household, batch, binding)
    rows = guarded["details"][0]["rows"]
    assert [r["discretionary"] for r in rows[:3]] == [1000, 800, 800]
    assert all(r["essential"] == 1000 for r in rows)
    assert guarded["outcomes"][0]["discretionary_spending_reduction"] == 4600
    fixed = run(household, batch, binding.model_copy(update=dict(spending_guardrail=None)))
    difference = paired(fixed, guarded)[0]
    assert difference["discretionary_reduction_change"] == 4600
    assert difference["real_wealth_change"] == 4600


def test_observed_recovery_restores_the_original_uncompounded_spending():
    household, market, binding = case(recovery=True)
    rows = run(household, generate(market), binding)["details"][0]["rows"]
    assert [r["discretionary"] for r in rows[:3]] == [1000, 800, 1000]
    assert [r["guardrail_cut_active"] for r in rows[:3]] == [False, True, False]


def test_annual_review_cannot_act_earlier_than_its_selected_interval():
    household, market, binding = case()
    annual = binding.spending_guardrail.model_copy(update=dict(review_interval_months=12))
    rows = run(
        household, generate(market), binding.model_copy(update=dict(spending_guardrail=annual))
    )["details"][0]["rows"]
    assert all(r["discretionary"] == 1000 for r in rows[:12])
    assert rows[12]["discretionary"] == 800
