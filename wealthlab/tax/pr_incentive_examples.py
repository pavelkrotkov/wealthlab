"""Original synthetic examples distinguish US-source dividends from PR-source gains."""

from datetime import date
from decimal import Decimal

from wealthlab.tax.nj_facts import NJIncome
from wealthlab.tax.pr_decree_facts import Decree, MarketableGain, PRComparison
from wealthlab.tax.pr_examples import synthetic as ordinary
from wealthlab.tax.pr_inputs import income


def legacy_dividends():
    annual = ordinary()
    row = annual.income[0].model_copy(
        update={
            "kind": "dividends",
            "qualified_dividends": Decimal(100000),
            "federal_source": "US",
            "pr_source": "US",
            "evidence": "Original synthetic qualified dividend from a US corporation",
        }
    )
    baseline = annual.baseline.model_copy(
        update={
            "federal_income": income([row]),
            "nj_income": NJIncome(dividends=Decimal(100000)),
        }
    )
    annual = annual.model_copy(update={"income": [row], "baseline": baseline})
    decree = Decree(
        status="assumed",
        application_date=date(2024, 11, 1),
        granted_on=date(2024, 12, 1),
        effective_from=date(2025, 1, 1),
        valid_until=date(2035, 12, 31),
        residence_since=date(2025, 1, 1),
        eligibility_history="assumed",
        prior_residence_window_2006_2012="assumed",
        compliance="assumed",
        not_revoked="assumed",
        evidence="Original synthetic grant; no actual eligibility finding",
    )
    return PRComparison(annual=annual, decree=decree)


def new_gain():
    comparison = legacy_dividends()
    annual = comparison.annual
    row = annual.income[0].model_copy(
        update={
            "kind": "long_term",
            "qualified_dividends": Decimal(0),
            "received": date(2029, 12, 31),
            "federal_source": "PR",
            "pr_source": "PR",
            "evidence": "Original synthetic marketable security acquired after relocation",
        }
    )
    baseline = gain_baseline(annual, row)
    residence = annual.primary.model_copy(
        update={
            "local_start": date(2027, 1, 1),
            "local_end": date(2029, 12, 31),
        }
    )
    annual = annual.model_copy(
        update={
            "baseline": baseline,
            "income": [row],
            "primary": residence,
            "pr_regime": "freeze_2025",
        }
    )
    decree = comparison.decree.model_copy(
        update={
            "application_date": date(2027, 1, 1),
            "granted_on": date(2027, 2, 1),
            "effective_from": date(2027, 1, 1),
            "valid_until": date(2055, 12, 31),
            "residence_since": date(2027, 1, 1),
            "six_prior_years_nonresident": "assumed",
        }
    )
    gain = MarketableGain(
        income_index=0,
        acquired=date(2027, 3, 1),
        sale_proceeds=Decimal(200000),
        federal_cost=Decimal(100000),
        pr_cost=Decimal(100000),
        federal_possession_start=date(2027, 1, 1),
        pr_resident_since=date(2027, 1, 1),
        federal_move_fmv=Decimal(0),
        pr_move_fmv=Decimal(0),
        ordinary_public_stock_classification="assumed",
        actively_traded_throughout="assumed",
        continuous_residence="assumed",
        us_non_bfr_in_prior_ten_years="yes",
        federal_fmv_election="confirmed",
        evidence="Original synthetic purchase and sale; not historical market data",
    )
    return PRComparison(
        annual=annual, decree=decree, gains=[gain], other_preferential_entitlement="fails"
    )


def gain_baseline(annual, row):
    baseline = annual.baseline.model_copy(
        update={
            "policy": annual.baseline.policy.model_copy(update={"year": 2029}),
            "federal_income": income([row]),
            "nj_income": NJIncome(dispositions=Decimal(100000)),
            "nj_regime": "freeze_2025",
        }
    )
    return baseline
