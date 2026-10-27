"""Independent two-source examples share the public PR residence fixture, not its tax answer."""

from decimal import Decimal

from wealthlab.tax.pr_examples import synthetic
from wealthlab.tax.pr_inputs import income
from wealthlab.tax.pr_tax_slices import Slice


def ordinary():
    case = synthetic()
    row = case.income[0].model_copy(update=dict(kind="interest"))
    rows = [
        row.model_copy(
            update=dict(
                federal_amount=Decimal(10000),
                pr_amount=Decimal(10000),
                federal_source="US",
                pr_source="US",
            )
        ),
        row.model_copy(update=dict(federal_amount=Decimal(20000), pr_amount=Decimal(20000))),
    ]
    baseline = case.baseline.model_copy(
        update=dict(
            federal_income=income(rows),
            nj_income=case.baseline.nj_income.model_copy(
                update=dict(wages=Decimal(0), interest=Decimal(30000))
            ),
        )
    )
    return case.model_copy(update=dict(income=rows, baseline=baseline))


def mixed(ordinary_amount=100000, gain_amount=50000):
    case = synthetic()
    wage = case.income[0].model_copy(
        update=dict(federal_amount=Decimal(ordinary_amount), pr_amount=Decimal(ordinary_amount))
    )
    gain = wage.model_copy(
        update=dict(
            kind="long_term",
            federal_amount=Decimal(gain_amount),
            pr_amount=Decimal(gain_amount),
            federal_source="US",
            pr_source="US",
        )
    )
    return case, [Slice(wage), Slice(gain, "lt15")]


def household():
    from wealthlab.household.scenario import Scenario
    from wealthlab.tax.annual import Payments
    from wealthlab.tax.foreign_credit_example import amount
    from wealthlab.tax.jurisdiction_execution_example import native_pr

    case = ordinary()
    data = native_pr().model_dump(mode="json")
    context = data["tax_plan"]["cases"][0]["pr_federal"]
    annual = case.baseline.model_dump(mode="json")
    annual["payments"] = Payments().model_dump(mode="json")
    context["sources"] = [
        dict(
            id=identity,
            owner_id="person_a",
            classification_assumed_confirmed=True,
            income=dict(row.model_dump(mode="json"), received="2025-06-30"),
        )
        for identity, row in zip(("interest_us", "interest_pr"), case.income, strict=True)
    ]
    annual["pr_federal"] = context
    data["tax_plan"]["cases"] = [annual]
    foreign = data["foreign_tax_plan"]
    profile = foreign["credit_profiles"][0]
    profile.update(
        annual=annual,
        eligibility="denied",
        passive_category_no_special_reclassification_confirmed=True,
    )
    profile["income"] = [
        dict(
            id=row["id"],
            owner_id="person_a",
            country=row["income"]["federal_source"],
            kind="interest",
            basket="passive",
            value=amount("2025-06-30", value),
            source_classification="Independent synthetic ordinary-interest source",
        )
        for row, value in zip(context["sources"], (10000, 20000), strict=True)
    ]
    foreign["schedules"][0].update(
        creditable_fraction="0",
        credit_eligibility="denied",
        income_ids=["interest_us", "interest_pr"],
    )
    return Scenario.model_validate(data)
