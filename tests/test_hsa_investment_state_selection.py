"""State-basis choice changes realized state gains without inventing asset returns."""

from wealthlab.retirement.hsa_investment_example import synthetic
from wealthlab.retirement.hsa_investment_inputs import HSAInvestments
from wealthlab.retirement.hsa_investments import run


def case(selection):
    data = synthetic().model_dump(mode="json")
    c = data["case"]
    c["accounts"][0]["cash"] = "0"
    c.update(trades=[], distributions=[], fee_schedules=[], closing_prices=dict(fund="100"))
    original = c["lots"][0]
    c["lots"] = [
        dict(original, id=key, quantity="10", federal_basis=str(fed), nj_basis=str(nj))
        for key, fed, nj in (("fed_high", 2000, 200), ("nj_high", 1000, 900))
    ]
    data.update(
        marks=[],
        cash_targets=[
            dict(
                id="raise",
                provenance="assumption",
                date="2026-12-31",
                account_id="hsa",
                amount="1000",
            )
        ],
    )
    data["funding_sources"][0].update(selection=selection, commission="0")
    return HSAInvestments.model_validate(data)


def test_nj_hifo_uses_state_basis_and_keeps_the_same_economic_wealth():
    ordinary = run(case("hifo"))
    state = run(case("nj_hifo"))
    assert ordinary["disposals"][0]["lot_id"] == "fed_high"
    assert state["disposals"][0]["lot_id"] == "nj_high"
    assert ordinary["nj_income_by_year"][2026]["dispositions"] == 800
    assert state["nj_income_by_year"][2026]["dispositions"] == 100
    assert ordinary["net_wealth"] == state["net_wealth"] == 2000
    assert state["federal_investment_income"] == 0
