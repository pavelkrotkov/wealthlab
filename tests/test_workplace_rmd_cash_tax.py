"""Withholding and shortfall excise share existing tax credits without invented cash.

Two $0.02 shortfalls total $0.04: their combined25% tax is exactly $0.01.
Independent per-plan rounding would lose that cent. A fully withheld RMD
similarly creates a payment credit and no immediately spendable cash.
"""

from decimal import Decimal
from types import SimpleNamespace

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_rmd_example import synthetic
from wealthlab.retirement.workplace_rmd_reporting import finalize


def test_aggregate_excise_rounding_preserves_one_cent_across_two_small_shortfalls():
    rows: dict[str, dict] = {
        name: dict(shortfall=None, excise_tax=Decimal(0)) for name in ("alpha", "beta")
    }
    book = SimpleNamespace(
        current=rows,
        config=SimpleNamespace(shortfall_treatment="ordinary_25_percent"),
        remaining=lambda _: Decimal(".02"),
    )
    shortfall, excise = finalize(book)
    assert shortfall == Decimal(".04")
    assert excise == Decimal(".01")
    assert sum(row["excise_tax"] for row in rows.values()) == excise


def test_rmd_only_auto_payment_can_use_a_fully_elected_combined_source_rate():
    data = synthetic().model_dump(mode="json")
    plan = data["workplace_plan"]["cash_withdrawals"]
    plan["orders"] = []
    plan["rmd"]["automatic_nj_withholding_rate"] = ".9"
    rows = project(Scenario.model_validate(data))
    assert rows[11]["tax_source_withholding"] == rows[11]["workplace_withdrawal_gross"]
    assert rows[11]["closing_cash"] == 0
    assert rows[-1]["net_wealth"] == 492000
