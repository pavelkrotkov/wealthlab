"""Cash conservation separates premiums, noncash interest and extinguished debt."""

from tests.life_contract_cases import case, event
from wealthlab.products.life_contract import run
from wealthlab.products.life_contract_example import synthetic


def test_zero_cash_lapse_creates_income_and_no_surviving_asset_or_loan():
    result = run(synthetic())
    assert result["external_cash"] == 0
    assert result["closing_loan"] == 0
    assert result["closed_contract_asset"] == 0
    assert result["rows"][1]["federal_ordinary_income"] == 26000
    assert result["annual"][0]["tax_change"] > 0


def test_living_values_do_not_add_death_benefit_to_surrender_cash():
    result = run(synthetic())
    assert result["values"][0]["net_cash_value"] == 5000
    assert result["values"][0]["net_surrender_value"] == 3000
    assert result["values"][0]["net_death_benefit"] == 180000
    assert result["values"][0]["protection_shortfall"] == 120000


def test_paid_interest_fee_and_repayment_do_not_become_premium_basis():
    result = run(
        case(
            [
                event("premium", 20),
                event("dividend_cash", 5, 2),
                event("loan_advance", 40, 3),
                event("capitalized_interest", 2, 4),
                event("loan_interest_payment", 1, 5),
                event("loan_principal_repayment", 10, 6),
                event("external_fee", 3, 7),
            ]
        )
    )
    assert result["external_cash"] == 11  # -20 +5 +40 -1 -10 -3
    assert result["closing_loan"] == 32
    assert result["closing_federal_basis"] == 115
    assert result["premium_paid"] == 20
    assert result["premiums_from_retirement"] == 0
    assert result["closed_contract_asset"] is None


def test_unconfirmed_or_missing_values_stay_unknown():
    data = synthetic().model_dump(mode="json")
    data["contract"]["values"][0]["gross_surrender_value"] = None
    from wealthlab.products.life_contract_inputs import LifeContractCase

    result = run(LifeContractCase.model_validate(data))
    assert result["values"][0]["net_surrender_value"] is None
    data["contract"]["values_match_executed_events_confirmed"] = False
    result = run(LifeContractCase.model_validate(data))
    assert result["values"][0]["net_cash_value"] is None
    assert result["values"][0]["protection_shortfall"] is None
