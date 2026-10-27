"""An executed cash election has a real funding oracle even though legal closure is unknown."""

from wealthlab.employment.compensation_example import synthetic
from wealthlab.employment.compensation_exit_state import from_rows
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def disposition_case(election):
    data = synthetic().model_dump(mode="json")
    data["compensation_plan"]["tranches"][0]["liquid_from"] = data["start"]
    base = dict(tranche="award", provenance="illustration", date=data["start"])
    data["compensation_plan"]["events"] = [
        dict(
            base,
            id="redeem",
            sequence=0,
            kind="distribution",
            amount="20000",
            bucket="vested",
            purpose="ordinary",
            election=election,
        ),
        dict(base, id="forfeit", sequence=1, kind="forfeit", amount=None),
    ]
    return Scenario.model_validate(data)


def test_full_native_cash_and_forfeiture_do_not_invent_contract_units():
    cash, retained = project(disposition_case("cash")), project(disposition_case("retain"))
    result = from_rows(cash)["award"]
    assert cash[-1]["closing_cash"] - retained[-1]["closing_cash"] == 20000
    assert cash[-1]["net_wealth"] == retained[-1]["net_wealth"]
    assert result["cash_distributed"] == 20000
    assert result["forfeited_value"] == 80000
    assert result["dollar_positions_zero"]
    assert result["contract_units"] is result["contractual_exit_proven"] is None


def test_retained_distribution_preserves_exact_source_and_failed_liquidity_evidence():
    rows = project(disposition_case("retain"))
    result = from_rows(rows)["award"]
    record = result["disposition_events"][0]
    assert result["account_balance"] == 20000
    assert record["bucket"] == "vested"
    assert record["election"] == "retain"
    assert record["cash"] == 0
    assert record["requested"] == 20000
