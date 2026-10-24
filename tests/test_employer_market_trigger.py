"""A decline observed at January close changes only subsequent wages and unvested value."""

from employer_market_cases import crashed

from wealthlab.markets.household_run import run


def test_next_month_job_loss_forfeiture_and_rehire_reconcile():
    household, batch, binding = crashed()
    result = run(household, batch, binding)
    rows = result["details"][0]["rows"]
    assert rows[0]["income"] == 10000
    assert rows[1]["income"] == rows[6]["income"] == 0
    assert rows[7]["income"] == 5000
    assert sum(r["income"] for r in rows) == 35000
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 55000


def test_job_loss_forfeits_contingent_value_without_erasing_vested_assets():
    household, batch, binding = crashed()
    rows = run(household, batch, binding)["details"][0]["rows"]
    assert rows[0]["employer_vested"] == 10000
    assert rows[0]["employer_unvested_contingent"] == 40000
    assert rows[1]["employer_unvested_contingent"] == 0
    assert rows[-1]["account_balances"]["employer_fund"] == 10000
