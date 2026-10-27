"""Synthetic mixed US/PR sources share the native published full-year PR residence facts."""

from wealthlab.tax.annual import AnnualCase
from wealthlab.tax.foreign_credit_example import amount
from wealthlab.tax.foreign_credit_example import synthetic as credits
from wealthlab.tax.foreign_credit_inputs import ForeignCreditCase
from wealthlab.tax.pr_examples import synthetic as pr_example
from wealthlab.tax.pr_execution_facts import PRFederalProfile
from wealthlab.tax.pr_source_facts import SourceIncome


def annual(government=False):
    base = credits().annual
    context = pr_example()
    rows = [
        dict(
            id="work_us",
            owner_id="person_a",
            classification_assumed_confirmed=True,
            income=SourceIncome(
                received="2025-06-30",
                kind="wages",
                federal_amount=50000,
                pr_amount=50000,
                federal_source="US",
                pr_source="US",
                evidence="Synthetic independently sourced US services",
            ).model_dump(),
        ),
        dict(
            id="work_pr",
            owner_id="person_a",
            classification_assumed_confirmed=True,
            income=SourceIncome(
                received="2025-09-30",
                kind="wages",
                federal_amount=50000,
                pr_amount=50000,
                federal_source="PR",
                pr_source="PR",
                us_government_wages=government,
                evidence="Synthetic PR services; government exception explicit",
            ).model_dump(),
        ),
    ]
    profile = PRFederalProfile.model_validate(
        dict(
            as_of="2025-12-31",
            people={"person_a": "primary"},
            primary=context.primary,
            sources=rows,
            pr_regime="published_2025",
            pr_wages_reported_on_form_499r2="assumed",
            source="Invented full-year PR eligibility; no legal conclusion",
        )
    )
    return AnnualCase.model_validate(base.model_copy(update=dict(pr_federal=profile)).model_dump())


def credit_case(government=False, eligibility="allowed"):
    data = credits().model_dump(mode="json")
    data["annual"] = annual(government).model_dump(mode="json")
    data["income"][0].update(id="work_us", value=amount("2025-06-30", 50000))
    data["income"][1].update(id="work_pr", country="PR", value=amount("2025-09-30", 50000))
    payment = data["tax_cash"][0]
    payment.update(
        country="PR",
        income_ids=["work_pr"],
        value=amount("2025-12-15", 10000),
        creditable_native="10000",
    )
    data["eligibility"] = eligibility
    return ForeignCreditCase.model_validate(data)


def household(government=False, credit_eligibility="allowed"):
    from wealthlab.household.scenario import Scenario
    from wealthlab.tax.foreign_tax_example import synthetic

    data = synthetic().model_dump(mode="json")
    profile = credit_case(government).model_dump(mode="json")
    profile["tax_cash"] = []
    profile["annual"]["payments"]["federal_income_withheld"] = "0"
    data["tax_plan"]["cases"] = [profile["annual"]]
    foreign = data["foreign_tax_plan"]
    foreign["credit_profiles"] = [profile]
    foreign["assessments"][0].update(country="PR", currency="USD")
    foreign["schedules"][0].update(
        income_ids=["work_pr"],
        credit_eligibility=credit_eligibility,
        creditable_fraction="1" if credit_eligibility == "allowed" else "0",
    )
    for quote in foreign["quotes"]:
        quote.update(currency="USD", usd_per_unit="1")
    return Scenario.model_validate(data)
