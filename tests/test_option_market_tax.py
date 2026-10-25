"""Compiled year-end option marks preserve independent federal/NJ recognition without cash twice."""

from tests.option_market_cases import change, flat
from wealthlab.markets.household_run import run


def test_open_cash_1256_legs_mark_and_reset_before_same_day_model_unwind():
    scenario, batch, binding = flat()

    def setup(data):
        for leg in data["option_plan"]["case"]["legs"]:
            if leg["underlying"] == "INDEX":
                leg.update(federal_class="section1256", expiry="2027-01-31")

    result = run(change(scenario, setup), batch, binding)
    rows = result["details"][0]["rows"][-1]["option_tax_audit"]
    federal, nj = selected(rows, "federal"), selected(rows, "nj")
    assert (len(federal), len(nj)) == (4, 2)
    assert sum(row["recognized"] for row in federal) == sum(row["recognized"] for row in nj)
    assert all(row["short_term"] is None for row in nj)


def selected(rows, jurisdiction):
    return [
        row
        for row in rows
        if row["jurisdiction"] == jurisdiction and row["id"].startswith("index_")
    ]
