"""Actual escrow settlement extinguishes the real lien once and cannot invent owner cash.

Opening cash20000 + home300000 - lien60000 =260000. Five paid600
interest installments precede June's actual600 interest,60000 principal and
10000 closing costs:246400 cash remains, with no home/debt or duplicate receipt.
"""

from decimal import Decimal as D

from tests.property_cases import change, holding, negative, retain, sale
from wealthlab.household.funding import opening_wealth
from wealthlab.household.projection import project
from wealthlab.household.property_example import synthetic


def test_actual_close_conserves_wealth_and_payoff_is_not_a_second_generic_payment():
    case = synthetic()
    before = case.model_dump_json()
    rows = project(case)
    assert opening_wealth(case) == 260000
    close = rows[5]
    expected = dict(
        opening_cash=17000,
        property_cash_received=229400,
        property_debt_principal_paid=60000,
        property_debt_interest_paid=600,
        debt_payment=0,
        interest=0,
        principal=0,
    )
    assert {key: close[key] for key in expected} == expected
    assert sum(r["debt_payment"] for r in rows) == 3000
    assert rows[-1]["account_balances"] == dict(cash=D(246400), home=D(0))
    assert (rows[-1]["net_wealth"], rows[-1]["debt_balances"]) == (246400, dict(home_lien=D(0)))
    assert case.model_dump_json() == before


def test_negative_equity_close_consumes_only_existing_authorized_cash_and_no_debt_forgiveness():
    rows = project(change(negative))
    close = rows[5]
    # 50000 gross pays1000 costs and60600 real lien/interest; owner contributes11600.
    assert close["property_owner_cash_paid"] == 11600
    assert close["property_cash_received"] == close["debt_payment"] == 0
    assert close["closing_cash"] == rows[-1]["closing_cash"] == 5400
    assert rows[-1]["net_wealth"] == 5400
    assert rows[-1]["debt_balances"]["home_lien"] == 0
    assert rows[-1]["account_balances"]["home"] == 0
    assert rows[-1]["annual_tax"]["total_liability"] == 0


def test_retained_marks_are_equity_not_spending_cash_and_do_not_reset_basis():
    def changed(data):
        retain(data)
        holding(data)["observations"][-1]["value"] = "350000"

    rows = project(change(changed))
    last = rows[-1]
    expected = dict(
        closing_cash=12800,
        net_wealth=302800,
        account_balances=dict(cash=D(12800), home=D(350000)),
        debt_balances=dict(home_lien=D(60000)),
    )
    assert {key: last[key] for key in expected} == expected
    position = last["property_positions"][0]
    assert position["net_equity"] == 290000
    assert (position["federal_basis"], position["nj_basis"]) == (250000, 240000)
    assert last["property_audit"]["closing_events"] == []
    assert last["annual_tax"]["federal"]["agi"] == 0


def test_independent_tax_recognition_posts_once_after_close_without_second_cash_receipt():
    def changed(data):
        sale(data).update(federal_taxable_gain="40000", nj_taxable_gain="50000")

    rows = project(change(changed))
    assert sum(r["tax_event_cash"] for r in rows) == 0
    assert rows[-1]["annual_tax"]["federal"]["agi"] == 40000
    assert rows[-1]["annual_tax"]["federal"]["income_tax"] == 0
    # Frozen2025 joint NJ:50000 less2000 exemptions,48000-48050 table band =>770.
    assert rows[-1]["annual_tax"]["new_jersey"]["income_tax"] == 770
    assert rows[-1]["closing_cash"] == 245630
