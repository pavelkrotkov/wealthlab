"""Policy cash is spendable once; policy debt and drilling creditors reduce equity once."""

from drilling_life_cases import blended
from streamlit.testing.v1 import AppTest

from wealthlab.household.projection import project


def test_actual_policy_premium_precedes_drilling_and_leaves_real_creditor_claim():
    row = project(blended())[0]
    assert (row["life_payments_paid"], row["drilling_call_funded"]) == (1000, 99500)
    assert (row["drilling_call_owed"], row["drilling_creditor_payables"]) == (500, 500)
    assert (row["closing_cash"], row["drilling_recourse_liability"]) == (0, 0)
    assert row["net_wealth"] + row["annual_tax"]["total_liability"] == 30400
    assert (row["account_balances"]["life_policy"], row["drilling_account_value"]) == (10900, 19500)


def test_actual_mec_loan_funds_drilling_and_shares_recognized_tax_without_duplicate_debt():
    row = project(blended(loan=True))[0]
    assert (row["life_cash_received"], row["drilling_call_funded"]) == (500, 100000)
    assert (row["closing_cash"], row["drilling_call_owed"], row["drilling_creditor_payables"]) == (
        0,
        0,
        0,
    )
    federal = row["annual_tax"]["federal"]
    assert (federal["insurance_ordinary_income"], federal["insurance_additional_tax"]) == (500, 50)
    assert row["net_wealth"] + row["annual_tax"]["total_liability"] == 29500
    assert row["life_policy_values"][0]["loan"] == 500


def test_generic_results_keep_life_and_drilling_nested_audits_outside_numeric_charts():
    data = blended(loan=True).model_dump_json()
    source = "\n".join(
        [
            "from wealthlab.household.scenario import Scenario",
            "from wealthlab.household.projection import project",
            "from wealthlab.ui.results import display",
            f"case = Scenario.model_validate_json({data!r})",
            "display(case, project(case))",
        ]
    )
    app = AppTest.from_string(source, default_timeout=90).run()
    assert (bool(app.exception), bool(app.error)) == (False, False)
    assert any("life_policies" in item.value and "drilling" in item.value for item in app.json)
