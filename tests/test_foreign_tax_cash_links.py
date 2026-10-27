"""Source withholding and delayed refunds cannot create duplicated household cash.

A payer sends $11,000 directly to the foreign authority and $9,000 to the
wallet; only the latter can fund another obligation. A later EUR1,000 refund
is a $1,400 assessed claim before receipt, then actual cash on its supplied
date. Its $1,100 original US-credit reversal and $300 separately recognized
currency income retain independent tax and cash identities.
"""

from decimal import Decimal

import pytest
from foreign_tax_cases import refunded, withheld

from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_payer_withholding_records_foreign_tax_without_a_second_wallet_debit():
    row = project(Scenario.model_validate(withheld()))[0]
    assert row["tax_event_cash"] == Decimal(9000)
    assert row["foreign_tax_paid"] == Decimal(11000)
    assert row["tax_withheld"] == Decimal(1530)
    assert row["tax_source_withholding"] == 0
    assert row["closing_cash"] == Decimal(57470)
    assert row["foreign_tax_position"] == 0
    assert row["annual_tax"]["federal"]["foreign_tax_credit"] == 0


def test_foreign_withholding_without_its_shared_book_is_explicitly_rejected():
    data = withheld()
    data["foreign_tax_plan"] = None
    with pytest.raises(ValueError, match="shared foreign tax cash plan"):
        project(Scenario.model_validate(data))


def test_assessed_refund_is_a_claim_before_actual_cash_arrives():
    rows = project(Scenario.model_validate(refunded()))
    november = rows[1]
    assert november["foreign_tax_position"] == Decimal(-1400)
    assert november["closing_cash"] == Decimal(39000)
    assert november["foreign_tax_refund_received"] == 0
    assert november["net_wealth"] == Decimal(40400) - november["tax_position"]


def test_actual_refund_uses_receipt_fx_and_original_credit_fx_without_another_income_receipt():
    row = project(Scenario.model_validate(refunded()))[-1]
    refund = row["foreign_tax_cash_records"][0]
    assert row["foreign_tax_refund_received"] == Decimal(1400)
    assert refund["credit_tax_usd"] == Decimal(-1100)
    assert row["foreign_tax_position"] == 0
    assert row["annual_tax"]["federal"]["agi"] == Decimal(100300)
    assert row["tax_event_cash"] == 0
    assert not row["foreign_tax_unresolved"]


def test_unconfirmed_refund_claim_cannot_increase_actual_wealth_before_receipt():
    data = refunded()
    data["foreign_tax_plan"]["assessments"][0]["refund_claim_eligibility"] = "unresolved"
    row = project(Scenario.model_validate(data))[1]
    assert row["foreign_tax_position"] == 0
    assert row["foreign_tax_positions"][0]["contingent_refund_marked_usd"] == Decimal(1400)
    assert row["net_wealth"] == Decimal(39000) - row["tax_position"]
    assert row["foreign_tax_unresolved"]
    assert row["funding_failure"]


def test_known_reduced_assessment_cannot_keep_excess_unreconciled_credit_facts():
    row = project(Scenario.model_validate(refunded()))[1]
    assert row["annual_tax"]["federal"]["foreign_tax_credit"] == 0
    assert any("revised foreign assessment" in reason for reason in row["foreign_tax_unresolved"])
    assert row["foreign_tax_refund_received"] == 0
