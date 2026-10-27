"""The opening cash purchase binds acquisition before native cash-exit tax recognition.

A20000purchase with an independent2000basis reduction exits for20000in its
first year. The native audit must recognize2000short-term gain with zero tax-
event cash; the original supplied long-term unit label cannot govern this exit.
"""

import pytest
from optimization_allocation_cases import case
from optimization_cases import changed

from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.search import search
from wealthlab.optimization.validation import validate


@pytest.fixture(scope="module")
def early_exit():
    def edit(data):
        data["dimensions"][1]["locked_choice"] = "private_fund"
        contract = data["sleeve_opportunities"][1]["unit"]["private_fund_contract"]
        contract.update(settlement_days=0)
        contract["requests"][0]["notice_date"] = "2026-06-01"
        contract["basis_adjustments"] = [
            dict(
                id="independent_basis",
                provenance="illustration",
                date="2026-09-01",
                federal="-1000",
                new_jersey="-1000",
                explanation="Conditional independent basis reduction without a current deduction",
            )
        ]

    return search(changed(case(), edit))


def test_early_cash_fund_exit_uses_actual_purchase_date_without_adding_income_as_cash(early_exit):
    rows = early_exit["selected_training"]["details"][0]["rows"]
    state = next(row for row in rows[-1]["sleeve_audit"] if row["redemption_paid"])
    event = state["fund_tax_audit"][-1]["conditional_exit"]["recognition_schedule"][0]
    assert event["federal"]["short_term"] == "2000.00"
    assert event["federal"]["long_term"] == "0"
    assert event["cash_received"] == "0"
    assert rows[-1]["closing_cash"] == 251999


def test_subscription_binds_new_acquisition_instead_of_legacy_capital_character(early_exit):
    contract = early_exit["selected_training"]["household"]["sleeve_plan"]["sleeves"][0][
        "private_fund_contract"
    ]
    assert contract["federal_holding_start"] == "2026-01-01"
    assert contract["federal_capital_character"] is None


@pytest.mark.parametrize(
    "changes,match",
    [
        ({"ordinary_holding_period_assumed_confirmed": False}, "confirmed ordinary"),
        (
            {"federal_holding_start": "2020-01-01", "federal_capital_character": None},
            "different historical",
        ),
    ],
)
def test_new_cash_offer_cannot_inherit_older_holding_or_unconfirmed_special_treatment(
    changes, match
):
    data = case().model_dump(mode="json")
    data["sleeve_opportunities"][1]["unit"]["private_fund_contract"].update(changes)
    with pytest.raises(ValueError, match=match):
        validate(PolicySearch.model_validate(data))
