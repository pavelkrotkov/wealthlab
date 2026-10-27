"""Fresh allocation units cannot silently rewrite old holdings, loans or supplied tax history."""

from decimal import Decimal

import pytest

from wealthlab.products.option_allocation import scale_new_plan
from wealthlab.products.option_household_example import synthetic as old_holdings
from wealthlab.products.option_household_inputs import OptionPlan
from wealthlab.products.option_purchase_example import unit_plan


def changed_case(**updates):
    plan = unit_plan()
    return plan.model_copy(update={"case": plan.case.model_copy(update=updates)})


@pytest.mark.parametrize(
    "updates",
    [
        {"outside_cash": Decimal(1)},
        {"allow_settlement_loan": True},
        {"unwind": False},
    ],
)
def test_separate_reserves_borrowing_and_retained_contract_books_are_rejected(updates):
    with pytest.raises(ValueError):
        scale_new_plan(changed_case(**updates), 1, per_unit_fees_confirmed=True)


def test_old_lots_are_not_rescaled_or_given_fresh_acquisition_basis():
    plan = unit_plan()
    lots = old_holdings().option_plan.case.holdings.lots
    book = plan.case.holdings.model_copy(update={"lots": lots})
    original = lots[0].model_dump_json()
    with pytest.raises(ValueError, match="pre-owned lots"):
        scale_new_plan(changed_case(holdings=book), 2, per_unit_fees_confirmed=True)
    assert lots[0].model_dump_json() == original


@pytest.mark.parametrize("field", ["federal_deferrals", "nj_deferrals"])
def test_old_position_specific_loss_deferrals_are_not_assumed_proportional(field):
    plan = unit_plan()
    tax = plan.case.tax.model_copy(update={field: {"prior_loss": Decimal(10)}})
    with pytest.raises(ValueError, match="deferred losses"):
        scale_new_plan(changed_case(tax=tax), 2, per_unit_fees_confirmed=True)


def test_initial_unit_capital_must_fund_actual_opening_purchase_and_collateral():
    data = unit_plan().model_dump(mode="json")
    data["case"]["holdings"]["accounts"][0]["cash"] = "1"
    with pytest.raises(ValueError, match="does not fund native opening"):
        scale_new_plan(OptionPlan.model_validate(data), 1, per_unit_fees_confirmed=True)


def test_later_contract_openings_cannot_be_folded_into_an_opening_unit():
    plan = unit_plan()
    legs = [plan.case.legs[0].model_copy(update={"opened": plan.case.marks[1].date})]
    with pytest.raises(ValueError, match="open every supplied contract at start"):
        scale_new_plan(changed_case(legs=legs), 1, per_unit_fees_confirmed=True)


def test_ordinary_dividends_require_the_same_explicit_cash_receipt_tax_assumption():
    data = unit_plan().model_dump(mode="json")
    data["case"]["dividends"] = [dict(ex_date="2026-01-31", pay_date="2026-02-28", per_share="1")]
    with pytest.raises(ValueError, match="ordinary dividend"):
        scale_new_plan(OptionPlan.model_validate(data), 1, per_unit_fees_confirmed=True)
