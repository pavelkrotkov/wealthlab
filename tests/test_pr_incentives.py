"""Matched ordinary/decree alternatives preserve US tax and deny blanket exemptions."""

from decimal import Decimal

from wealthlab.tax.pr_incentive_examples import legacy_dividends, new_gain
from wealthlab.tax.pr_incentives import evaluate


def test_legacy_us_dividends_keep_us_federal_tax_and_ordinary_alternative():
    # 2025 single: (100,000 - 15,750 - 48,350) x 15% = 5,385 US tax.
    # A local legacy exemption cannot turn a US corporate dividend into PR source.
    result = evaluate(legacy_dividends())
    assert result["ordinary"]["federal"]["income_tax"] == 5385
    assert result["ordinary"]["puerto_rico"]["income_tax"] == Decimal("12996.60")
    assert result["incentive"]["federal"]["income_tax"] == 5385
    assert result["incentive"]["puerto_rico"]["income_tax"] == 0
    assert result["incentive"]["tax_plus_supplied_compliance_cost"] is None
    assert result["incentive"]["conditional"]


def test_new_regime_post_move_gain_is_four_percent_not_zero():
    # Original stock acquired after the move has no inherited pre-move gain.
    # Ordinary LTC tax is 15,000; the new Act60 branch is 4,000, both excluding
    # that PR-source gain federally under the supplied full-year BFR assumptions.
    result = evaluate(new_gain())
    assert result["ordinary"]["puerto_rico"]["income_tax"] == 15000
    assert result["incentive"]["federal"]["income_tax"] == 0
    assert result["incentive"]["puerto_rico"]["income_tax"] == 4000
    assert result["incentive"]["gain_allocations"][0]["pr_pre"] == 0


def test_denied_and_unset_decrees_do_not_block_ordinary_computation():
    comparison = legacy_dividends()
    denied = comparison.model_copy(
        update={"decree": comparison.decree.model_copy(update={"status": "denied"})}
    )
    result = evaluate(denied)
    assert result["ordinary"] is not None
    assert result["incentive"] is None
    assert result["qualification"]["reasons"]


def test_supplied_compliance_cost_is_separate_from_tax_and_not_zero_by_default():
    comparison = legacy_dividends()
    decree = comparison.decree.model_copy(update={"annual_compliance_cost": Decimal(12345)})
    result = evaluate(comparison.model_copy(update={"decree": decree}))["incentive"]
    assert result["federal_pr_payroll_total"] == 5385
    assert result["tax_plus_supplied_compliance_cost"] == 17730


def test_new_four_percent_does_not_override_more_favorable_ordinary_law():
    comparison = new_gain()
    rows = [
        comparison.annual.income[0].model_copy(
            update={"federal_amount": Decimal(1000), "pr_amount": Decimal(1000)}
        )
    ]
    annual = comparison.annual.model_copy(
        update={
            "income": rows,
            "baseline": comparison.annual.baseline.model_copy(
                update={
                    "federal_income": comparison.annual.baseline.federal_income.model_copy(
                        update={"long_term": Decimal(1000)}
                    )
                }
            ),
        }
    )
    gain = comparison.gains[0].model_copy(update={"sale_proceeds": Decimal(101000)})
    result = evaluate(comparison.model_copy(update={"annual": annual, "gains": [gain]}))
    assert result["incentive"]["puerto_rico"]["income_tax"] == 0
    assert "favorable" in result["incentive"]["tax_treatment_selected"]
