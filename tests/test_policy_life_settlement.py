"""Known terminal gains and policy loans use the native book after selecting a full path.

The source illustration controls gross settlement, not spendable wealth. A loan
receipt reduces later net settlement, and actual paid premiums increase tax basis.
"""

from optimization_cases import changed
from optimization_life_cases import case

from wealthlab.optimization.search import search
from wealthlab.products.life_household_example import event


def test_supplied_terminal_gain_uses_actual_paid_basis_without_adding_tax_income_to_cash():
    def edit(data):
        data["dimensions"][1]["locked_choice"] = "two_premiums"
        terminal = data["life_opportunities"][2]["holding"]["contract"]["events"][-1]
        terminal.update(amount="12200", nj_ordinary_income="200")

    report = search(changed(case(), edit))
    rows = report["selected_training"]["details"][0]["rows"]
    terminal = rows[-1]["life_policy_audit"]["executed"][-1]
    assert terminal["federal_basis_before"] == 12000
    assert terminal["federal_ordinary_income"] == terminal["nj_ordinary_income"] == 200
    assert sum(row["life_cash_received"] for row in rows) == 12200
    assert rows[-1]["closing_cash"] == 262199


def test_loan_cash_and_net_surrender_reconcile_to_same_economic_receipt():
    def edit(data):
        data["dimensions"][1]["locked_choice"] = "two_premiums"
        events = data["life_opportunities"][2]["holding"]["contract"]["events"]
        events.insert(
            -1, event("loan", "2027-01-16", "loan_advance", 500, cash_value_before="11800")
        )

    report = search(changed(case(), edit))
    rows = report["selected_training"]["details"][0]["rows"]
    terminal = rows[-1]["life_policy_audit"]["executed"][-1]
    assert terminal["loan_before"] == 500 and terminal["loan_after"] == 0
    assert terminal["received_cash"] == 11300
    assert sum(row["life_cash_received"] for row in rows) == 11800
    assert rows[-1]["closing_cash"] == 261799
