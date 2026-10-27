"""Independent value/basis checks follow contribution through actual household cash and exit tax."""

from exchange_fund_cases import flat

from wealthlab.products.exchange_fund_compare import compare


def test_flat_complete_exit_recognizes_deferred_gain_and_conserves_household_capital():
    scenario = flat()
    before = scenario.model_dump_json()
    result = compare(scenario)
    for rows in result["rows"].values():
        assert_completed_exit(rows)
    assert result["outcomes"]["exchange"] == result["outcomes"]["direct_sale"]
    assert scenario.model_dump_json() == before


def assert_completed_exit(rows):
    final = rows[-1]
    assert final["annual_tax"]["federal"]["agi"] == 80000
    assert final["annual_tax"]["new_jersey"]["gross_income"] == 70000
    assert final["net_wealth"] == 130000 - final["annual_tax"]["total_liability"]
    assert final["account_balances"]["exchange"] == 0
    assert sum(row["tax_event_cash"] for row in rows) == 0
