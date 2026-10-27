"""Native wrapper deposits retain the fee, while actual medical funding sells only the true gap."""

from tests.advisory_cases import with_fee
from tests.medical_bill_cases import data
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import plan as lot_plan


def test_native_personal_hsa_deposit_cannot_consume_the_reserved_outer_fee():
    value = data(cash=1000, hsa=0)
    value["hsa_plan"]["medical_bills"] = []
    value["hsa_plan"]["contributions"] = [
        dict(
            id="optional_personal",
            provenance="illustration",
            date="2026-01-15",
            destination="cash_hsa",
            source="personal_cash",
            amount="1000",
        )
    ]
    rows = project(with_fee(Scenario.model_validate(value), account="cash", rate="0", fixed="100"))
    assert rows[0]["hsa_personal_contributions"] == 900
    assert rows[0]["advisory_fees_paid"] == 100
    assert rows[0]["closing_cash"] == 0
    assert rows[0]["account_balances"]["cash_hsa"] == rows[0]["net_wealth"] == 900


def test_native_hsa_medical_payment_and_fee_use_one_actual_lot_funding_gap():
    value = data()
    value["accounts"].append(
        dict(
            id="brokerage",
            provenance="illustration",
            owner="person_a",
            wrapper="taxable",
            currency="USD",
            balance="100000",
            monthly_fee="0",
        )
    )
    case = Scenario.model_validate(value)
    case = case.model_copy(update=dict(lot_plan=lot_plan_model(case)))
    first = project(with_fee(case, rate="0", fixed="100"))[0]
    # $3k HSA direct payment +$1k cash leave $2k bill +$100 fee; one $1 sale commission.
    assert first["medical_provider_paid"] == first["medical_cash_paid"] == 3000
    assert first["lot_funding_proceeds"] == 2100
    assert first["advisory_fees_paid"] == 100
    assert first["medical_owed"] == first["fees_owed"] == 0
    assert first["net_wealth"] == 97899


def lot_plan_model(case):
    from wealthlab.portfolio.household_inputs import HouseholdLots

    return HouseholdLots.model_validate(lot_plan(case))
