"""A real option premium becomes required-tax cash before optional saving can use it.

The $500 premium arrives in the option book after the first foreign-tax
attempt had zero cash. The next receipt/product boundary must retry the same
$500 obligation once. Repeated boundaries see a zero remaining payable and
cannot debit it again or create another payment record.
"""

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.portfolio.household_example import plan
from wealthlab.products.option_household_example import synthetic as options
from wealthlab.tax.foreign_credit_example import synthetic as credits
from wealthlab.tax.foreign_tax_example import foreign_plan


def late_case():
    data = options().model_dump(mode="json")
    data.update(end="2026-02-01", expenses=[])
    data["accounts"][0]["balance"] = "0"
    option = data["option_plan"]["case"]
    option["holdings"]["end"] = "2026-01-31"
    option["marks"] = option["marks"][:2]
    option["unwind"] = False
    data["accounts"].append(
        dict(
            id="brokerage",
            owner="person_a",
            wrapper="taxable",
            currency="USD",
            monthly_fee="0",
            balance="0",
            provenance="assumption",
        )
    )
    lots = plan(Scenario.model_validate(data))
    lots["case"]["lots"], lots["funding_sources"] = [], []
    lots["monthly_marks"][0]["prices"]["stock"] = "100"
    lots["case"]["closing_prices"]["stock"] = "100"
    lots["savings"] = [
        dict(
            id="optional",
            provenance="assumption",
            date="2026-01-31",
            account_id="brokerage",
            amount="500",
            target_weights={"stock": "1"},
            commission_per_trade="0",
            minimum_cash="0",
        )
    ]
    data["lot_plan"] = lots
    data["foreign_tax_plan"] = tax_plan(data["tax_plan"]["cases"][0])
    return Scenario.model_validate(data)


def tax_plan(annual):
    profile = credits().model_dump(mode="json")
    profile.update(
        annual=annual,
        as_of="2026-01-31",
        tax_cash=[],
        people={"person_a": "primary", "person_b": "spouse"},
        eligibility="denied",
    )
    foreign = foreign_plan(profile)
    foreign["assessments"][0].update(
        liability_year=2026, observed="2026-01-01", tax_type="wealth", amount_native="500"
    )
    foreign["schedules"][0].update(
        due_date="2026-01-31",
        requested_native="500",
        creditable_fraction="0",
        income_ids=[],
        source_income_year=None,
    )
    foreign["quotes"] = [
        dict(
            date="2026-01-31",
            currency="EUR",
            usd_per_unit="1",
            source="Invented dated quote for exact cash conservation",
        )
    ]
    return foreign


def test_late_option_receipt_pays_required_tax_before_optional_saving():
    row = project(late_case())[0]
    assert row["option_cash_released"] == 500
    assert row["foreign_tax_paid"] == 500
    assert row["saving_spent"] == 0
    assert row["saving_unfilled"] == 500
    assert row["foreign_tax_position"] == 0
    assert row["closing_cash"] == 0


def test_repeated_receipt_boundaries_do_not_debit_a_paid_obligation_again():
    row = project(late_case())[0]
    assert len(row["foreign_tax_cash_records"]) == 1
    assert row["foreign_tax_cash_records"][0]["native_amount"] == 500
    assert row["foreign_tax_unfunded"] == 0
    assert not row["foreign_tax_unresolved"]
