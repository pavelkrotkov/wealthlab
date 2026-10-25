"""Equal opening wealth and spending preserve the economic cost of separate protection.

All three cases open with $10,000 and spend $3,000. The supplied limited-pay
values end with $7,000 marked living wealth; $300 term premiums leave $6,700.
The latter buys greater protection, which must remain visible beside wealth.
"""

from wealthlab.products.life_comparison import compare
from wealthlab.products.life_comparison_example import synthetic


def test_matched_liquid_saving_and_term_costs_reconcile_without_death_wealth():
    result = compare(synthetic())
    outcomes = {name: value["outcomes"][0] for name, value in result["alternatives"].items()}
    assert outcomes["limited"]["marked_wealth_after_recognized_tax"] == 7000
    assert outcomes["longer"]["marked_wealth_after_recognized_tax"] == 6700
    assert outcomes["liquid_term"]["marked_wealth_after_recognized_tax"] == 6700
    assert outcomes["liquid_term"]["saving_spent"] == 1800
    assert outcomes["liquid_term"]["closing_cash"] == 4900
    assert result["differences"]["limited"][0]["marked_wealth_change"] == 300


def test_insurance_need_and_retirement_obligations_do_not_become_investment_returns():
    result = compare(synthetic())
    outcomes = {name: value["outcomes"][0] for name, value in result["alternatives"].items()}
    assert outcomes["limited"]["ending_protection_gap"] == 50500
    assert outcomes["liquid_term"]["ending_protection_gap"] == 0
    assert outcomes["liquid_term"]["ending_death_protection"] == 150000
    assert outcomes["limited"]["future_retirement_premiums"] == 0
    assert outcomes["longer"]["future_retirement_premiums"] == 2000
    assert outcomes["liquid_term"]["premiums_from_retirement"] == 200
