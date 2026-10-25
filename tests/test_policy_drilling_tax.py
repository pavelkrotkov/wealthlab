"""The original well costs and final cash sale recognize tax through the same native return."""

from optimization_drilling_search_cases import case, changed

from wealthlab.optimization.search import search


def test_actual_property_costs_and_tax_return_pass_through_native_books():
    profile = changed(case(), lambda d: d["dimensions"][0].update(locked_choice="well"))
    result = search(profile)
    rows = result["selected_training"]["details"][0]["rows"]
    assert sum(row["drilling_call_funded"] for row in rows) == 100000
    assert sum(row["drilling_exit_cash"] for row in rows) == 40000
    # 10k paid manager loss plus70k IDC, offset by20k gain above20k remaining basis.
    assert rows[-1]["annual_tax"]["federal"]["agi"] == -60000
    assert rows[-1]["account_balances"] == {"cash": 140000, "drilling": 0}
