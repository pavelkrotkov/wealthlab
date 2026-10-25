"""Original synthetic PR wage comparison, with every residence claim explicitly assumed."""

from datetime import date
from decimal import Decimal

from wealthlab.tax.annual import synthetic as mainland
from wealthlab.tax.filing import Filing
from wealthlab.tax.pr_facts import PRCase, Residence, SourceIncome
from wealthlab.tax.pr_inputs import income


def synthetic():
    row = SourceIncome(
        received=date(2025, 12, 31),
        kind="wages",
        federal_amount=Decimal(100000),
        pr_amount=Decimal(100000),
        federal_source="PR",
        pr_source="PR",
        evidence="Synthetic services performed entirely in Puerto Rico",
    )
    baseline = mainland().model_copy(
        update={
            "filing": Filing(status="single", age_primary=40, age_spouse=0, dependents=[]),
            "federal_income": income([row]),
            "nj_income": mainland().nj_income.model_copy(update={"wages": Decimal(100000)}),
        }
    )
    residence = Residence(
        us_citizen="assumed",
        federal_bfr="full_year",
        presence_days=365,
        tax_home="assumed",
        closer_connection="assumed",
        local_start=date(2025, 1, 1),
        local_end=date(2025, 12, 31),
        evidence="Original synthetic full-year assumption; no taxpayer eligibility finding",
    )
    return PRCase(
        baseline=baseline,
        primary=residence,
        income=[row],
        pr_wages_reported_on_form_499r2="assumed",
    )
