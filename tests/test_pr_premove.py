"""Pre-move appreciation keeps independent federal lookback and local treatment."""

from datetime import date
from decimal import Decimal

from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.pr_incentive_examples import new_gain
from wealthlab.tax.pr_incentives import evaluate
from wealthlab.tax.pr_inputs import income


def premove_case(year=2025, lookback="yes"):
    comparison = new_gain()
    row = comparison.annual.income[0].model_copy(
        update={
            "received": date(year, 12, 31),
            "federal_amount": Decimal(600000),
            "pr_amount": Decimal(600000),
        }
    )
    residence = comparison.annual.primary.model_copy(
        update={"local_start": date(2020, 1, 1), "local_end": date(year, 12, 31)}
    )
    baseline = comparison.annual.baseline.model_copy(
        update={
            "policy": comparison.annual.baseline.policy.model_copy(update={"year": year}),
            "federal_income": income([row]),
            "nj_income": NJIncome(dispositions=Decimal(600000)),
        }
    )
    annual = comparison.annual.model_copy(
        update={"income": [row], "primary": residence, "baseline": baseline}
    )
    decree = comparison.decree.model_copy(
        update={
            "application_date": date(2020, 1, 1),
            "granted_on": date(2020, 2, 1),
            "effective_from": date(2020, 1, 1),
            "residence_since": date(2020, 1, 1),
            "valid_until": date(2035, 12, 31),
        }
    )
    asset = comparison.gains[0].model_copy(
        update={
            "acquired": date(2010, 1, 1),
            "sale_proceeds": Decimal(700000),
            "federal_move_fmv": Decimal(200000),
            "pr_move_fmv": Decimal(200000),
            "federal_possession_start": date(2020, 1, 1),
            "pr_resident_since": date(2020, 1, 1),
            "us_non_bfr_in_prior_ten_years": lookback,
        }
    )
    return comparison.model_copy(update={"annual": annual, "decree": decree, "gains": [asset]})


def test_premove_gain_preserves_us_tax_and_local_credit_and_abt():
    # FMV election: pre 100k remains US source; post 500k is PR source.
    # US LTC: (100k - 2,625 allocated STD - 48,350 zero-rate band) x15%.
    # Ordinary PR ABT: (600k - 3,500) x24%=143,160; legacy branch taxes
    # only pre 100k at15%, then credits the actual US tax on that same amount.
    result = evaluate(premove_case())
    assert result["incentive"]["federal"]["income_tax"] == Decimal("7353.75")
    assert result["incentive"]["puerto_rico"]["income_tax"] == Decimal("7646.25")
    assert result["incentive"]["federal_pr_payroll_total"] == 15000
    assert result["ordinary"]["federal_pr_payroll_total"] == 143160


def test_ended_federal_lookback_does_not_erase_local_five_percent_pre_gain():
    result = evaluate(premove_case(2035, "no"))["incentive"]
    assert result["federal"]["income_tax"] == 0
    assert result["puerto_rico"]["special_in_lieu_tax"] == 5000
    assert result["puerto_rico"]["income_tax"] == 5000
    assert result["gain_allocations"][0]["pr_pre"] == 100000


def test_no_election_retains_federal_post_move_gain_and_scales_local_paid_credit():
    comparison = premove_case()
    row = comparison.annual.income[0].model_copy(
        update={"federal_amount": Decimal(180000), "pr_amount": Decimal(180000)}
    )
    baseline = comparison.annual.baseline.model_copy(update={"federal_income": income([row])})
    annual = comparison.annual.model_copy(update={"income": [row], "baseline": baseline})
    comparison = comparison.model_copy(update={"annual": annual})
    gain = comparison.gains[0].model_copy(
        update={
            "federal_fmv_election": "fails",
            "sale_proceeds": Decimal(210000),
            "federal_cost": Decimal(30000),
            "pr_cost": Decimal(30000),
            "federal_move_fmv": Decimal(60000),
            "pr_move_fmv": Decimal(60000),
        }
    )
    result = evaluate(comparison.model_copy(update={"gains": [gain]}))["incentive"]
    # US tax on all gain is not fully creditable against the pre-only local base.
    credit = result["puerto_rico"]["regular_credit"]
    federal = result["federal"]["income_tax"] - result["federal"]["niit"]
    assert credit["reported_paid_or_accrued"] == federal / 6
    assert credit["reported_paid_or_accrued"] == Decimal("2897.50")
    # A2 all-ordinary option wins: (1,120 + 1,500 x14%) x95%=1,263.50.
    # The credit cannot exceed that lower actual local regular liability.
    assert credit["allowed"] == Decimal("1263.50")
